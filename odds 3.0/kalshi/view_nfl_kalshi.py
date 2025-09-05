"""
View NFL Markets from Kalshi
Simple script to display Kalshi NFL prediction markets
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def view_kalshi_nfl():
    """Display NFL markets from Kalshi"""
    print("=" * 60)
    print("KALSHI NFL MARKETS")
    print("=" * 60)
    
    try:
        # Initialize Kalshi client
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get NFL markets
        result = client.search_sports_markets('nfl')
        
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
            return
        
        markets = result.get('data', [])
        print(f"Found {len(markets)} NFL markets:\n")
        
        for i, market in enumerate(markets, 1):
            ticker = market.get('ticker')
            title = market.get('title')
            status = market.get('status')
            close_time = market.get('close_time', 'N/A')
            
            # Get pricing
            yes_bid = market.get('yes_bid', 0)
            no_bid = market.get('no_bid', 0)
            
            print(f"{i}. {title}")
            print(f"   Ticker: {ticker}")
            print(f"   Status: {status}")
            print(f"   Close Time: {close_time}")
            if yes_bid or no_bid:
                print(f"   Pricing: YES {yes_bid}% / NO {no_bid}%")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_kalshi_nfl()