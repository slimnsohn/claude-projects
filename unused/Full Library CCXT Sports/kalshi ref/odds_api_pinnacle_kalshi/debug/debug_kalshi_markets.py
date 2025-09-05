"""
Debug script to examine all available Kalshi markets
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'prod_ready'))

from kalshi_client import KalshiClientUpdated as KalshiClient
import json

def debug_all_markets():
    """Debug all available Kalshi markets"""
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        print("=== DEBUGGING ALL KALSHI MARKETS ===")
        all_markets = client.get_all_markets()
        
        if not all_markets.get('success'):
            print(f"Failed to fetch markets: {all_markets}")
            return
            
        markets = all_markets.get('data', [])
        print(f"Total markets available: {len(markets)}")
        
        # Analyze categories
        categories = {}
        tickers_with_baseball = []
        titles_with_baseball = []
        
        print(f"\n=== ANALYZING ALL MARKETS ===")
        for i, market in enumerate(markets):
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            category = market.get('category', '')
            
            # Count categories
            if category:
                categories[category] = categories.get(category, 0) + 1
            
            # Look for any baseball-related content
            baseball_keywords = ['baseball', 'mlb', 'athletics', 'twins', 'yankee', 'dodger',
                               'probaseball', 'pro-baseball', 'a\'s', 'athletics', 'minnesota']
            
            title_lower = title.lower()
            ticker_lower = ticker.lower()
            category_lower = category.lower()
            
            has_baseball = any(keyword in title_lower or keyword in ticker_lower or keyword in category_lower 
                              for keyword in baseball_keywords)
            
            if has_baseball:
                tickers_with_baseball.append(ticker)
                titles_with_baseball.append(title)
                print(f"  BASEBALL MATCH: {ticker} - {title} (category: '{category}')")
            
            # Print first few markets as examples
            if i < 5:
                print(f"Market {i+1}: {ticker} - {title} (category: '{category}')")
        
        print(f"\n=== CATEGORIES FOUND ===")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} markets")
        
        print(f"\n=== BASEBALL SEARCH RESULTS ===")
        print(f"Tickers with baseball terms: {len(tickers_with_baseball)}")
        print(f"Titles with baseball terms: {len(titles_with_baseball)}")
        
        if tickers_with_baseball:
            print("Baseball-related tickers:")
            for ticker in tickers_with_baseball:
                print(f"  - {ticker}")
        
        if titles_with_baseball:
            print("Baseball-related titles:")
            for title in titles_with_baseball[:5]:  # Show first 5
                print(f"  - {title}")
                
        # Look specifically for A's/Athletics and Twins
        print(f"\n=== SEARCHING FOR SPECIFIC TEAMS (A's, Twins) ===")
        specific_teams = ['athletics', 'a\'s', 'twins', 'minnesota', 'oakland']
        for market in markets:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '').lower()
            category = market.get('category', '').lower()
            
            if any(team in title or team in ticker or team in category for team in specific_teams):
                print(f"  TEAM MATCH: {market.get('ticker')} - {market.get('title')} (category: '{market.get('category')}')")
                print(f"    Yes price: {market.get('yes_price', 'N/A')}")
                print(f"    No price: {market.get('no_price', 'N/A')}")
                print()
        
    except Exception as e:
        print(f"Debug failed: {e}")

if __name__ == "__main__":
    debug_all_markets()