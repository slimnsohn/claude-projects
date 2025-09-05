"""
Comprehensive exploration of Kalshi API to find more markets
Check pagination, different endpoints, filters, etc.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'prod_ready'))

import requests
import json
from datetime import datetime, timezone

def load_credentials():
    credentials = {}
    with open("keys/kalshi_credentials.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                credentials[key] = value
    return credentials

def explore_kalshi_endpoints():
    """Explore different Kalshi endpoints and parameters"""
    credentials = load_credentials()
    
    # Try both endpoints
    endpoints = [
        "https://api.elections.kalshi.com/trade-api/v2",
        "https://demo-api.kalshi.co/trade-api/v2"
    ]
    
    for base_url in endpoints:
        print(f"\n{'='*80}")
        print(f"EXPLORING: {base_url}")
        print(f"{'='*80}")
        
        # Test 1: Basic markets endpoint with different limits
        print(f"\n--- Testing pagination with different limits ---")
        for limit in [100, 200, 500, 1000]:
            try:
                url = f"{base_url}/markets"
                params = {'limit': limit}
                
                print(f"Trying limit={limit}...")
                response = requests.get(url, params=params, timeout=30)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    cursor = data.get('cursor', '')
                    print(f"  Found: {len(markets)} markets")
                    print(f"  Cursor: {cursor[:50]}..." if cursor else "  No cursor")
                    
                    if len(markets) > 100:
                        print(f"  SUCCESS: Found more than 100 markets!")
                        return base_url, markets, cursor
                        
                else:
                    print(f"  Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"  Exception: {e}")
        
        # Test 2: Try with cursor pagination
        print(f"\n--- Testing cursor pagination ---")
        try:
            url = f"{base_url}/markets"
            all_markets = []
            cursor = None
            page = 1
            
            while page <= 5:  # Limit to 5 pages to avoid infinite loop
                params = {'limit': 100}
                if cursor:
                    params['cursor'] = cursor
                
                print(f"Page {page}, cursor: {cursor[:20] if cursor else 'None'}...")
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    new_cursor = data.get('cursor', '')
                    
                    print(f"  Got {len(markets)} markets")
                    all_markets.extend(markets)
                    
                    if not new_cursor or new_cursor == cursor:
                        print(f"  No more pages")
                        break
                        
                    cursor = new_cursor
                    page += 1
                else:
                    print(f"  Error: {response.status_code}")
                    break
            
            print(f"Total markets found with pagination: {len(all_markets)}")
            if len(all_markets) > 100:
                return base_url, all_markets, None
                
        except Exception as e:
            print(f"Pagination error: {e}")
        
        # Test 3: Try different market status filters
        print(f"\n--- Testing status filters ---")
        for status in ['active', 'closed', 'settled', 'open']:
            try:
                url = f"{base_url}/markets"
                params = {'status': status, 'limit': 200}
                
                print(f"Trying status={status}...")
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    print(f"  Found: {len(markets)} {status} markets")
                else:
                    print(f"  Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  Exception: {e}")
        
        # Test 4: Try different endpoints
        print(f"\n--- Testing different endpoints ---")
        alt_endpoints = [
            "/markets",
            "/events", 
            "/series",
            "/portfolio/positions",
            "/exchange/status"
        ]
        
        for endpoint in alt_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"Trying {endpoint}...")
                response = requests.get(url, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
                    
            except Exception as e:
                print(f"  Exception: {e}")
    
    return None, [], None

def search_for_baseball_in_all_markets(markets):
    """Search through all markets for baseball content"""
    print(f"\n{'='*80}")
    print(f"SEARCHING {len(markets)} MARKETS FOR BASEBALL CONTENT")
    print(f"{'='*80}")
    
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
        'texas', 'seattle', 'sport', 'game', 'probaseball', 'pro-baseball'
    ]
    
    potential_matches = []
    
    for i, market in enumerate(markets):
        ticker = market.get('ticker', '').lower()
        title = market.get('title', '').lower()
        category = market.get('category', '').lower()
        
        found_terms = []
        for term in baseball_terms:
            if term in ticker or term in title or term in category:
                found_terms.append(term)
        
        if found_terms:
            potential_matches.append({
                'index': i,
                'ticker': market.get('ticker'),
                'title': market.get('title'),
                'category': market.get('category'),
                'found_terms': found_terms,
                'yes_bid': market.get('yes_bid', 0),
                'no_bid': market.get('no_bid', 0),
                'status': market.get('status')
            })
    
    print(f"Found {len(potential_matches)} potential baseball matches:")
    for match in potential_matches:
        print(f"  {match['index']:3d}. {match['ticker']}")
        print(f"       {match['title']}")
        print(f"       Terms: {match['found_terms']}")
        print(f"       Category: '{match['category']}'")
        print(f"       Prices: Yes={match['yes_bid']/100:.1%}, No={match['no_bid']/100:.1%}")
        print(f"       Status: {match['status']}")
        print()
    
    return potential_matches

def export_all_found_markets(markets, source_url):
    """Export all markets found"""
    print(f"\n{'='*80}")
    print(f"EXPORTING {len(markets)} MARKETS TO FILES")
    print(f"{'='*80}")
    
    # Export comprehensive data
    with open('debug/all_kalshi_markets_comprehensive.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_url': source_url,
            'total_markets': len(markets),
            'markets': markets
        }, f, indent=2, default=str)
    
    # Export readable format
    with open('debug/all_kalshi_markets_comprehensive.txt', 'w', encoding='utf-8') as f:
        f.write(f"COMPREHENSIVE KALSHI MARKETS - {len(markets)} TOTAL\n")
        f.write(f"Source: {source_url}\n")
        f.write(f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, market in enumerate(markets, 1):
            ticker = market.get('ticker', 'NO_TICKER')
            title = market.get('title', 'NO_TITLE')
            category = market.get('category', '')
            status = market.get('status', '')
            yes_bid = market.get('yes_bid', 0)
            no_bid = market.get('no_bid', 0)
            
            f.write(f"MARKET {i:4d}: {ticker}\n")
            f.write(f"  Title:     {title}\n")
            f.write(f"  Category:  '{category}'\n")
            f.write(f"  Status:    {status}\n")
            f.write(f"  Prices:    Yes={yes_bid/100:.1%}, No={no_bid/100:.1%}\n")
            f.write("-" * 80 + "\n")
    
    print(f"Exported to:")
    print(f"  - debug/all_kalshi_markets_comprehensive.json")
    print(f"  - debug/all_kalshi_markets_comprehensive.txt")

def main():
    """Main exploration function"""
    print("COMPREHENSIVE KALSHI MARKET EXPLORATION")
    print("Searching for baseball markets and pagination...")
    
    # Explore endpoints
    working_url, all_markets, cursor = explore_kalshi_endpoints()
    
    if all_markets:
        print(f"\nFound {len(all_markets)} total markets!")
        
        # Search for baseball
        baseball_matches = search_for_baseball_in_all_markets(all_markets)
        
        # Export everything
        export_all_found_markets(all_markets, working_url)
        
        return len(all_markets), len(baseball_matches)
    else:
        print("No additional markets found beyond the original 100")
        return 100, 0

if __name__ == "__main__":
    total_markets, baseball_markets = main()
    print(f"\nFINAL RESULT:")
    print(f"  Total Markets Found: {total_markets}")
    print(f"  Baseball Markets: {baseball_markets}")