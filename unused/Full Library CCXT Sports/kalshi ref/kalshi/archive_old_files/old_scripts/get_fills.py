#!/usr/bin/env python3
"""
Get fills (trades) from Kalshi API
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment

def get_fills_with_resolutions():
    """Get all fills and their market resolution data."""
    load_dotenv()
    env = Environment.PROD
    KEYID = os.getenv('DEMO_KEYID') if env == Environment.DEMO else os.getenv('PROD_KEYID')
    KEYFILE = os.getenv('DEMO_KEYFILE') if env == Environment.DEMO else os.getenv('PROD_KEYFILE')

    try:
        with open(KEYFILE, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found at {KEYFILE}")

    client = KalshiHttpClient(key_id=KEYID, private_key=private_key, environment=env)
    
    print("Getting fills...")
    fills_response = client.get_fills(limit=1000)
    
    if 'fills' not in fills_response:
        return {"error": "No fills found", "response": fills_response}
    
    fills = fills_response['fills']
    print(f"Found {len(fills)} fills")
    
    # Get unique tickers for market data
    unique_tickers = list(set(fill.get('ticker') for fill in fills))
    print(f"Getting market data for {len(unique_tickers)} markets...")
    
    market_data = {}
    for i, ticker in enumerate(unique_tickers, 1):
        print(f"  {i}/{len(unique_tickers)}: {ticker}")
        try:
            market_info = client.get_market(ticker)
            market_data[ticker] = market_info
            time.sleep(0.05)  # Rate limiting
        except Exception as e:
            print(f"    Error: {e}")
            market_data[ticker] = {"error": str(e)}
    
    # Enhance fills with market data
    enhanced_fills = []
    for fill in fills:
        ticker = fill.get('ticker')
        market_info = market_data.get(ticker, {})
        
        enhanced_fill = fill.copy()
        
        if 'market' in market_info:
            market = market_info['market']
            enhanced_fill['market_status'] = market.get('status')
            enhanced_fill['market_close_time'] = market.get('close_time')
            enhanced_fill['market_result'] = market.get('result')
            enhanced_fill['final_price'] = market.get('last_price')
        
        enhanced_fills.append(enhanced_fill)
    
    # Create result data
    result_data = {
        "retrieved_at": datetime.now().isoformat(),
        "total_fills": len(enhanced_fills),
        "fills": enhanced_fills,
        "market_data": market_data
    }
    
    # Save to current file
    os.makedirs("data", exist_ok=True)
    
    # Save timestamped version
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    timestamped_file = f"data/archive/fills_with_resolutions_{timestamp}.json"
    os.makedirs("data/archive", exist_ok=True)
    
    with open(timestamped_file, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    # Save current version
    with open("data/fills_with_resolutions_current.json", 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"Data saved to data/fills_with_resolutions_current.json")
    print(f"Archive saved to {timestamped_file}")
    
    return result_data

if __name__ == "__main__":
    result = get_fills_with_resolutions()
    if "error" not in result:
        print(f"SUCCESS: Retrieved {result['total_fills']} fills with market data")