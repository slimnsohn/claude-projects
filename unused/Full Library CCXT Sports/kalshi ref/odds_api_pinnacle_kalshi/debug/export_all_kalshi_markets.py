"""
Export all Kalshi markets to a readable file for analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'prod_ready'))

from kalshi_client import KalshiClientUpdated as KalshiClient
import json

def export_all_markets():
    """Export all Kalshi markets to files"""
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        print("Fetching all Kalshi markets for export...")
        all_markets = client.get_all_markets()
        
        if not all_markets.get('success'):
            print(f"Failed to fetch markets: {all_markets}")
            return
            
        markets = all_markets.get('data', [])
        print(f"Total markets fetched: {len(markets)}")
        
        # Create detailed text file
        with open('debug/all_kalshi_markets.txt', 'w', encoding='utf-8') as f:
            f.write(f"ALL KALSHI MARKETS - {len(markets)} TOTAL\n")
            f.write("=" * 80 + "\n\n")
            
            for i, market in enumerate(markets, 1):
                ticker = market.get('ticker', 'NO_TICKER')
                title = market.get('title', 'NO_TITLE')
                category = market.get('category', 'NO_CATEGORY')
                yes_price = market.get('yes_price', 'N/A')
                no_price = market.get('no_price', 'N/A')
                status = market.get('status', 'N/A')
                close_time = market.get('close_time', 'N/A')
                
                f.write(f"MARKET {i:3d}: {ticker}\n")
                f.write(f"  Title:     {title}\n")
                f.write(f"  Category:  '{category}'\n")
                f.write(f"  Yes Price: {yes_price}\n")
                f.write(f"  No Price:  {no_price}\n")
                f.write(f"  Status:    {status}\n")
                f.write(f"  Close:     {close_time}\n")
                f.write("-" * 80 + "\n")
        
        # Create JSON file with full data
        with open('debug/all_kalshi_markets.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': all_markets.get('timestamp'),
                'source': all_markets.get('source'),
                'total_markets': len(markets),
                'markets': markets
            }, f, indent=2, default=str)
        
        # Create CSV file for easy viewing
        with open('debug/all_kalshi_markets.csv', 'w', encoding='utf-8') as f:
            f.write("Index,Ticker,Title,Category,YesPrice,NoPrice,Status,CloseTime\n")
            for i, market in enumerate(markets, 1):
                ticker = market.get('ticker', '').replace('"', '""')
                title = market.get('title', '').replace('"', '""')
                category = market.get('category', '').replace('"', '""')
                yes_price = market.get('yes_price', '')
                no_price = market.get('no_price', '')
                status = market.get('status', '')
                close_time = market.get('close_time', '')
                
                f.write(f'{i},"{ticker}","{title}","{category}",{yes_price},{no_price},{status},{close_time}\n')
        
        print("\nEXPORTED TO FILES:")
        print("  - debug/all_kalshi_markets.txt (human readable)")
        print("  - debug/all_kalshi_markets.json (complete data)")  
        print("  - debug/all_kalshi_markets.csv (spreadsheet format)")
        
        # Show some sample markets that might be baseball
        print(f"\nSEARCHING FOR POTENTIAL BASEBALL MARKETS:")
        potential_baseball = []
        
        for market in markets:
            ticker = market.get('ticker', '').lower()
            title = market.get('title', '').lower()
            
            # Broader search terms
            baseball_terms = [
                'baseball', 'mlb', 'athletic', 'twin', 'yankee', 'dodger', 'giant',
                'cub', 'red sox', 'met', 'brave', 'astro', 'cardinal', 'angel',
                'ranger', 'mariner', 'ray', 'oriole', 'royal', 'tiger', 'white sox',
                'guardian', 'padre', 'rockie', 'diamondback', 'marlin', 'brewers',
                'pirate', 'national', 'phillie', 'oakland', 'minnesota', 'houston',
                'boston', 'chicago', 'new york', 'los angeles', 'san francisco',
                'atlanta', 'milwaukee', 'st. louis', 'arizona', 'colorado',
                'san diego', 'miami', 'philadelphia', 'pittsburgh', 'washington',
                'cleveland', 'detroit', 'kansas city', 'baltimore', 'tampa bay',
                'texas', 'seattle', 'sport', 'game', 'match', 'win', 'beat'
            ]
            
            if any(term in ticker or term in title for term in baseball_terms):
                potential_baseball.append(market)
        
        if potential_baseball:
            print(f"Found {len(potential_baseball)} potential baseball markets:")
            for market in potential_baseball[:10]:  # Show first 10
                print(f"  - {market.get('ticker')}: {market.get('title')}")
        else:
            print("No potential baseball markets found with broader search terms")
        
        # Show unique categories
        categories = set()
        for market in markets:
            cat = market.get('category', '')
            if cat:
                categories.add(cat)
        
        print(f"\nUNIQUE CATEGORIES FOUND:")
        if categories:
            for cat in sorted(categories):
                print(f"  - '{cat}'")
        else:
            print("  No categories found (all markets have empty category)")
        
    except Exception as e:
        print(f"Export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_all_markets()