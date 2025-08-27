#!/usr/bin/env python3

import requests
import json
import time
import os
from typing import Dict, List
from datetime import datetime, timedelta

class PriceLookup:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.manual_prices = self._load_manual_prices()
        
    def get_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Get current prices for a list of tickers"""
        prices = {}
        uncached_tickers = []
        
        # Check cache first
        current_time = time.time()
        for ticker in tickers:
            if (ticker in self.cache and 
                current_time - self.cache[ticker]['timestamp'] < self.cache_timeout):
                prices[ticker] = self.cache[ticker]['price']
            else:
                uncached_tickers.append(ticker)
        
        # Fetch uncached prices
        if uncached_tickers:
            fetched_prices = self._fetch_prices_yahoo(uncached_tickers)
            for ticker, price in fetched_prices.items():
                self.cache[ticker] = {
                    'price': price,
                    'timestamp': current_time
                }
                prices[ticker] = price
        
        return prices
    
    def _load_manual_prices(self) -> Dict[str, float]:
        """Load manual price fallbacks from JSON file"""
        try:
            if os.path.exists("manual_prices.json"):
                with open("manual_prices.json", 'r') as f:
                    data = json.load(f)
                    return data.get('prices', {})
        except Exception as e:
            print(f"Warning: Could not load manual prices: {e}")
        return {}
    
    def _fetch_prices_yahoo(self, tickers: List[str]) -> Dict[str, float]:
        """Fetch prices from Yahoo Finance API"""
        prices = {}
        
        # Yahoo Finance API (free tier)
        try:
            for ticker in tickers:
                try:
                    # Using yfinance-like approach
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'chart' in data and data['chart']['result']:
                            result = data['chart']['result'][0]
                            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                                prices[ticker] = float(result['meta']['regularMarketPrice'])
                            else:
                                print(f"Warning: No price data for {ticker}")
                                prices[ticker] = self.manual_prices.get(ticker, 0.0)
                        else:
                            print(f"Warning: Invalid response for {ticker}")
                            prices[ticker] = self.manual_prices.get(ticker, 0.0)
                    else:
                        print(f"Warning: Failed to fetch {ticker} (status: {response.status_code})")
                        prices[ticker] = self.manual_prices.get(ticker, 0.0)
                        
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error fetching {ticker}: {e}")
                    prices[ticker] = self.manual_prices.get(ticker, 0.0)
                    
        except Exception as e:
            print(f"Error in price fetch: {e}")
            # Use manual prices for all tickers if API fails
            for ticker in tickers:
                prices[ticker] = self.manual_prices.get(ticker, 0.0)
        
        return prices
    
    def get_price(self, ticker: str) -> float:
        """Get price for a single ticker"""
        prices = self.get_prices([ticker])
        return prices.get(ticker, 0.0)

def create_price_file(tickers: List[str], output_file: str = "prices.json"):
    """Create a JSON file with current prices for all tickers"""
    price_lookup = PriceLookup()
    
    print(f"Fetching prices for {len(tickers)} tickers...")
    prices = price_lookup.get_prices(tickers)
    
    # Add metadata
    price_data = {
        "timestamp": datetime.now().isoformat(),
        "prices": prices,
        "tickers_count": len(tickers),
        "successful_lookups": len([p for p in prices.values() if p > 0])
    }
    
    with open(output_file, 'w') as f:
        json.dump(price_data, f, indent=2)
    
    print(f"Prices saved to {output_file}")
    print(f"Successfully fetched {price_data['successful_lookups']}/{len(tickers)} prices")
    
    return price_data

if __name__ == "__main__":
    # Test with some sample tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'VFIAX', 'VOO', 'VTI']
    
    result = create_price_file(test_tickers)
    
    for ticker, price in result['prices'].items():
        if price > 0:
            print(f"{ticker}: ${price:.2f}")
        else:
            print(f"{ticker}: No price data")