"""
Aggressive search for ALL Kalshi markets using maximum limits
"""

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

def fetch_maximum_markets():
    """Try to fetch as many markets as possible"""
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    print("AGGRESSIVE SEARCH FOR ALL KALSHI MARKETS")
    print("=" * 60)
    
    # Try increasingly large limits
    for limit in [500, 1000, 2000, 5000, 10000]:
        print(f"\nTrying limit={limit}...")
        
        try:
            url = f"{base_url}/markets"
            params = {'limit': limit}
            
            response = requests.get(url, params=params, timeout=60)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                cursor = data.get('cursor', '')
                
                print(f"  SUCCESS: Found {len(markets)} markets")
                print(f"  Cursor exists: {bool(cursor)}")
                
                if len(markets) >= limit:
                    print(f"  NOTE: Might be more markets (hit limit)")
                else:
                    print(f"  NOTE: This appears to be all available markets")
                
                return markets, cursor
                
            else:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Exception: {e}")
    
    return [], None

def comprehensive_baseball_search(markets):
    """Most comprehensive search for baseball content"""
    print(f"\nCOMPREHENSIVE BASEBALL SEARCH - {len(markets)} MARKETS")
    print("=" * 60)
    
    # Exhaustive search terms
    baseball_terms = [
        # Direct terms
        'baseball', 'mlb', 'probaseball', 'pro-baseball',
        
        # All MLB teams (multiple variants)
        'athletic', 'athletics', 'a\'s', 'oakland',
        'twin', 'twins', 'minnesota', 'minneapolis',
        'yankee', 'yankees', 'new york', 'ny',
        'dodger', 'dodgers', 'los angeles', 'la',
        'giant', 'giants', 'san francisco', 'sf',
        'cub', 'cubs', 'chicago',
        'red sox', 'redsox', 'boston',
        'met', 'mets', 'new york',
        'brave', 'braves', 'atlanta',
        'astro', 'astros', 'houston',
        'cardinal', 'cardinals', 'st. louis', 'saint louis',
        'angel', 'angels',
        'ranger', 'rangers', 'texas',
        'mariner', 'mariners', 'seattle',
        'ray', 'rays', 'tampa bay', 'tampa',
        'oriole', 'orioles', 'baltimore',
        'royal', 'royals', 'kansas city',
        'tiger', 'tigers', 'detroit',
        'white sox', 'whitesox',
        'guardian', 'guardians', 'cleveland',
        'padre', 'padres', 'san diego',
        'rockie', 'rockies', 'colorado', 'denver',
        'diamondback', 'diamondbacks', 'arizona', 'phoenix',
        'marlin', 'marlins', 'miami', 'florida',
        'brewers', 'milwaukee',
        'pirate', 'pirates', 'pittsburgh',
        'national', 'nationals', 'washington',
        'phillie', 'phillies', 'philadelphia',
        
        # Generic sports terms
        'sport', 'game', 'match', 'win', 'beat', 'defeat',
        'championship', 'playoff', 'series', 'season',
        'home', 'away', 'vs', 'versus', 'at',
        
        # Percentage patterns that might indicate sports betting
        '53', '47', '52', '48', '51', '49'
    ]
    
    exact_matches = []
    percentage_matches = []
    city_matches = []
    
    for i, market in enumerate(markets):
        ticker = market.get('ticker', '').lower()
        title = market.get('title', '').lower()
        category = market.get('category', '').lower()
        yes_bid = market.get('yes_bid', 0)
        no_bid = market.get('no_bid', 0)
        
        # Calculate percentages
        yes_pct = yes_bid / 100 if yes_bid else 0
        no_pct = no_bid / 100 if no_bid else 0
        
        found_terms = []
        for term in baseball_terms:
            if term in ticker or term in title or term in category:
                found_terms.append(term)
        
        market_info = {
            'index': i,
            'ticker': market.get('ticker'),
            'title': market.get('title'),
            'category': market.get('category'),
            'yes_pct': yes_pct,
            'no_pct': no_pct,
            'status': market.get('status'),
            'found_terms': found_terms
        }
        
        # Categorize matches
        if any(term in ['baseball', 'mlb', 'athletic', 'twin'] for term in found_terms):
            exact_matches.append(market_info)
        elif (45 <= yes_pct*100 <= 55) or (45 <= no_pct*100 <= 55):
            percentage_matches.append(market_info)
        elif found_terms:
            city_matches.append(market_info)
    
    print(f"\nEXACT BASEBALL MATCHES: {len(exact_matches)}")
    for match in exact_matches:
        print(f"  {match['ticker']}: {match['title']}")
        print(f"    Terms: {match['found_terms']}")
        print(f"    Prices: {match['yes_pct']:.1%} / {match['no_pct']:.1%}")
        print()
    
    print(f"\nMARKETS WITH 45-55% PRICING (potential sports): {len(percentage_matches)}")
    for match in percentage_matches[:10]:  # Show first 10
        print(f"  {match['ticker']}: {match['title']}")
        print(f"    Prices: {match['yes_pct']:.1%} / {match['no_pct']:.1%}")
        print()
    
    print(f"\nCITY/TEAM NAME MATCHES: {len(city_matches)}")
    for match in city_matches[:5]:  # Show first 5
        print(f"  {match['ticker']}: {match['title']}")
        print(f"    Terms: {match['found_terms']}")
        print()
    
    return exact_matches, percentage_matches, city_matches

def export_comprehensive_results(markets, exact_matches, percentage_matches):
    """Export all results"""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Export full data
    with open('debug/maximum_kalshi_markets.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_markets': len(markets),
            'exact_baseball_matches': len(exact_matches),
            'percentage_matches': len(percentage_matches),
            'markets': markets,
            'exact_matches': exact_matches,
            'percentage_matches': percentage_matches
        }, f, indent=2, default=str)
    
    # Export summary
    with open('debug/maximum_kalshi_search_summary.txt', 'w', encoding='utf-8') as f:
        f.write(f"MAXIMUM KALSHI MARKET SEARCH RESULTS\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total Markets Found: {len(markets)}\n")
        f.write(f"=" * 60 + "\n\n")
        
        f.write(f"EXACT BASEBALL MATCHES: {len(exact_matches)}\n")
        f.write("-" * 40 + "\n")
        for match in exact_matches:
            f.write(f"{match['ticker']}: {match['title']}\n")
            f.write(f"  Terms: {match['found_terms']}\n")
            f.write(f"  Prices: {match['yes_pct']:.1%} / {match['no_pct']:.1%}\n\n")
        
        f.write(f"\nPOTENTIAL SPORTS (45-55% pricing): {len(percentage_matches)}\n")
        f.write("-" * 40 + "\n")
        for match in percentage_matches:
            f.write(f"{match['ticker']}: {match['title']}\n")
            f.write(f"  Prices: {match['yes_pct']:.1%} / {match['no_pct']:.1%}\n\n")
    
    print(f"\nEXPORTED RESULTS:")
    print(f"  - debug/maximum_kalshi_markets.json (complete data)")
    print(f"  - debug/maximum_kalshi_search_summary.txt (summary)")

def main():
    """Main function"""
    # Get maximum markets
    markets, cursor = fetch_maximum_markets()
    
    if not markets:
        print("Failed to fetch markets")
        return
    
    # Comprehensive search
    exact_matches, percentage_matches, city_matches = comprehensive_baseball_search(markets)
    
    # Export results
    export_comprehensive_results(markets, exact_matches, percentage_matches)
    
    print(f"\nFINAL SUMMARY:")
    print(f"  Total Markets: {len(markets)}")
    print(f"  Exact Baseball Matches: {len(exact_matches)}")
    print(f"  45-55% Price Matches: {len(percentage_matches)}")
    print(f"  City/Team Matches: {len(city_matches)}")

if __name__ == "__main__":
    main()