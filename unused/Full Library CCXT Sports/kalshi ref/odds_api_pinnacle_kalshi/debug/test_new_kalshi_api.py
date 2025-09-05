"""
Test new Kalshi API endpoints and search for MLB markets
"""

import requests
import json

def test_new_kalshi_endpoints():
    """Test the new Kalshi API endpoints"""
    
    endpoints = [
        "https://api.elections.kalshi.com/trade-api/v2/markets",
        "https://demo-api.kalshi.co/trade-api/v2/markets"
    ]
    
    print("Testing new Kalshi API endpoints...")
    
    for endpoint in endpoints:
        print(f"\n=== Testing {endpoint} ===")
        
        try:
            # Try without authentication first
            response = requests.get(endpoint, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                print(f"Success: Found {len(markets)} markets")
                
                # Look for sports/baseball related markets
                baseball_keywords = ['mlb', 'baseball', 'world series', 'yankees', 'dodgers', 
                                   'red sox', 'mets', 'giants', 'braves', 'astros', 'cubs',
                                   'orioles', 'rangers', 'twins', 'tigers', 'athletics',
                                   'angels', 'mariners', 'rays', 'nationals', 'brewers']
                
                baseball_markets = []
                sports_markets = []
                
                for market in markets[:50]:  # Check first 50 markets
                    title = market.get('title', '').lower()
                    ticker = market.get('ticker', '').lower()
                    category = market.get('category', '').lower()
                    
                    # Check for any baseball keywords
                    if any(keyword in title or keyword in ticker for keyword in baseball_keywords):
                        baseball_markets.append(market)
                    
                    # Check for sports category
                    if 'sport' in category or 'sport' in title:
                        sports_markets.append(market)
                
                print(f"Baseball-related markets found: {len(baseball_markets)}")
                print(f"Sports-related markets found: {len(sports_markets)}")
                
                if baseball_markets:
                    print("\nBaseball markets:")
                    for market in baseball_markets[:3]:
                        print(f"  - {market.get('ticker')}: {market.get('title')}")
                        print(f"    Yes: ${market.get('yes_price', 0)/100:.2f}, No: ${market.get('no_price', 0)/100:.2f}")
                
                elif sports_markets:
                    print("\nSports markets (for reference):")
                    for market in sports_markets[:3]:
                        print(f"  - {market.get('ticker')}: {market.get('title')}")
                
                else:
                    print("\nSample markets (no baseball found):")
                    for market in markets[:3]:
                        print(f"  - {market.get('ticker')}: {market.get('title')}")
                        print(f"    Category: {market.get('category', 'N/A')}")
                
            else:
                print(f"Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"Exception: {e}")

def test_market_categories():
    """Test what market categories are available"""
    print(f"\n=== Testing Market Categories ===")
    
    try:
        response = requests.get("https://demo-api.kalshi.co/trade-api/v2/markets", timeout=30)
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            
            # Get unique categories
            categories = set()
            for market in markets:
                cat = market.get('category', 'uncategorized')
                categories.add(cat)
            
            print(f"Available categories: {sorted(categories)}")
            
            # Show sample markets from each category
            for category in sorted(categories)[:5]:
                category_markets = [m for m in markets if m.get('category') == category]
                print(f"\n{category} ({len(category_markets)} markets):")
                for market in category_markets[:2]:
                    print(f"  - {market.get('title', 'No title')}")
                    
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_new_kalshi_endpoints()
    test_market_categories()