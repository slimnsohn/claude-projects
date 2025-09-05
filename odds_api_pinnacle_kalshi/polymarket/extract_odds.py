"""
Extract actual odds from Polymarket pages
Test with one of the working URLs to understand the data structure
"""

import requests
import json
import re
from datetime import datetime

def extract_odds_from_polymarket_page(url):
    """Extract odds from a specific Polymarket page"""
    print(f"Extracting odds from: {url}")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            return None
        
        content = response.text
        print(f"Content length: {len(content)} characters")
        
        # Method 1: Look for JSON in script tags
        print("\n1. Searching for JSON data in script tags...")
        
        # Pattern for preloaded state
        preload_patterns = [
            r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.__NEXT_DATA__\s*=\s*({.*?});',
            r'__INITIAL_STATE__"\s*:\s*({.*?})',
        ]
        
        for i, pattern in enumerate(preload_patterns, 1):
            matches = re.findall(pattern, content, re.DOTALL)
            print(f"  Pattern {i}: Found {len(matches)} matches")
            
            for match in matches:
                try:
                    data = json.loads(match)
                    print(f"    Successfully parsed JSON with {len(data)} top-level keys")
                    
                    # Look for market-related data
                    market_keys = []
                    for key in data.keys():
                        if any(word in key.lower() for word in ['market', 'token', 'condition', 'outcome', 'price']):
                            market_keys.append(key)
                    
                    if market_keys:
                        print(f"    Market-related keys: {market_keys}")
                        
                        # Dig deeper into market data
                        for key in market_keys[:2]:  # Check first 2 keys
                            if isinstance(data[key], dict):
                                print(f"      {key} contains: {list(data[key].keys())[:5]}")
                            elif isinstance(data[key], list) and len(data[key]) > 0:
                                if isinstance(data[key][0], dict):
                                    print(f"      {key}[0] contains: {list(data[key][0].keys())[:5]}")
                    
                    return data
                    
                except json.JSONDecodeError as e:
                    print(f"    JSON parse error: {str(e)[:100]}")
                except Exception as e:
                    print(f"    Other error: {str(e)[:100]}")
        
        # Method 2: Look for specific price patterns
        print("\n2. Searching for price patterns...")
        
        price_patterns = [
            r'[\$]?(\d+\.?\d*)¢',  # Cent prices
            r'[\$]?(\d+\.?\d*)\s*cent',  # Cent prices with space
            r'"price"\s*:\s*"?(\d*\.?\d+)"?',  # JSON price fields
            r'(\d+\.?\d*)\s*%',  # Percentage prices
            r'\$(\d+\.?\d+)',  # Dollar prices
        ]
        
        all_prices = []
        for i, pattern in enumerate(price_patterns, 1):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                prices = [float(p) for p in matches if p and float(p) > 0]
                print(f"  Pattern {i}: Found {len(prices)} prices: {prices[:5]}")
                all_prices.extend(prices)
        
        # Method 3: Look for outcome/team names
        print("\n3. Searching for outcome patterns...")
        
        # Extract team names from URL
        url_parts = url.split('/')[-1]  # Get the slug
        potential_teams = re.findall(r'nfl-([a-z]+)-([a-z]+)-', url_parts)
        if potential_teams:
            team1, team2 = potential_teams[0]
            print(f"  Teams from URL: {team1.upper()} vs {team2.upper()}")
            
            # Look for these teams in the content
            team1_mentions = len(re.findall(team1, content, re.IGNORECASE))
            team2_mentions = len(re.findall(team2, content, re.IGNORECASE))
            print(f"  {team1.upper()} mentions: {team1_mentions}")
            print(f"  {team2.upper()} mentions: {team2_mentions}")
        
        # Method 4: Look for binary outcome patterns (Yes/No)
        print("\n4. Searching for binary outcomes...")
        
        yes_pattern = r'"?Yes"?\s*[:\-]?\s*[\$]?(\d+\.?\d*)[¢%]?'
        no_pattern = r'"?No"?\s*[:\-]?\s*[\$]?(\d+\.?\d*)[¢%]?'
        
        yes_matches = re.findall(yes_pattern, content, re.IGNORECASE)
        no_matches = re.findall(no_pattern, content, re.IGNORECASE)
        
        if yes_matches:
            print(f"  'Yes' prices found: {[float(p) for p in yes_matches[:3]]}")
        if no_matches:
            print(f"  'No' prices found: {[float(p) for p in no_matches[:3]]}")
        
        # Method 5: Look for React component data
        print("\n5. Searching for React props...")
        
        react_patterns = [
            r'props"\s*:\s*({[^}]+})',
            r'"market"\s*:\s*({[^}]+})',
            r'"tokens"\s*:\s*(\[[^\]]+\])',
        ]
        
        for i, pattern in enumerate(react_patterns, 1):
            matches = re.findall(pattern, content)
            if matches:
                print(f"  React pattern {i}: Found {len(matches)} matches")
                for match in matches[:2]:
                    try:
                        data = json.loads(match)
                        print(f"    Parsed: {list(data.keys()) if isinstance(data, dict) else len(data)}")
                    except:
                        print(f"    Raw: {match[:100]}...")
        
        # Summary
        print(f"\n6. Summary:")
        print(f"  Total unique prices found: {len(set(all_prices))}")
        if all_prices:
            print(f"  Price range: {min(all_prices):.2f} - {max(all_prices):.2f}")
        
        return {
            'url': url,
            'prices': list(set(all_prices)),
            'content_length': len(content),
            'status': 'success'
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_multiple_games():
    """Test odds extraction on multiple games"""
    test_urls = [
        "https://polymarket.com/event/nfl-kc-lac-2025-09-05",
        "https://polymarket.com/event/nfl-dal-phi-2025-09-04",
        "https://polymarket.com/event/nfl-min-chi-2025-09-08",
    ]
    
    results = []
    
    for url in test_urls:
        print("\n" + "="*100)
        result = extract_odds_from_polymarket_page(url)
        if result:
            results.append(result)
    
    print("\n" + "="*100)
    print("OVERALL SUMMARY")
    print("="*100)
    print(f"Successfully extracted data from {len(results)}/{len(test_urls)} URLs")
    
    for result in results:
        print(f"\n{result['url']}:")
        print(f"  Prices found: {result['prices']}")

if __name__ == "__main__":
    test_multiple_games()