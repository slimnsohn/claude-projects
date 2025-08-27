#!/usr/bin/env python3

import json

def test_position_data():
    """Test if position data is correctly structured for the HTML dashboard"""
    
    with open('dashboard_data.json', 'r') as f:
        data = json.load(f)
    
    positions = data['positions']
    
    print(f"SUCCESS: Found {len(positions)} unique tickers in positions data")
    
    # Test a few positions
    sample_tickers = ['AAPL', 'VFIAX', 'VOO', 'VMFXX']
    
    for ticker in sample_tickers:
        if ticker in positions:
            pos_data = positions[ticker]
            print(f"\nSUCCESS: {ticker}:")
            print(f"   Accounts: {len(pos_data)}")
            total_shares = sum(p['shares'] for p in pos_data)
            print(f"   Total shares: {total_shares}")
            
            for i, pos in enumerate(pos_data):
                print(f"   Account {i+1}: {pos['account_name']} - {pos['shares']} shares")
        else:
            print(f"ERROR: {ticker} not found in positions")
    
    # Check price data
    with open('current_prices.json', 'r') as f:
        price_data = json.load(f)
    
    prices = price_data['prices']
    print(f"\nSUCCESS: Found {len(prices)} prices")
    
    for ticker in sample_tickers:
        if ticker in prices:
            print(f"   {ticker}: ${prices[ticker]}")
        else:
            print(f"ERROR: {ticker} price not found")

if __name__ == "__main__":
    test_position_data()