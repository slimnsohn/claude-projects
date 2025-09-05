"""
Simple NFL game test for Polymarket
Test the URLs that were returning 200 status codes
"""

import requests
import json
import re

def test_working_urls():
    """Test the URLs that returned 200 status codes"""
    print("Testing working Polymarket URLs...")
    print("=" * 60)
    
    # URLs that returned 200
    working_urls = [
        "https://polymarket.com/event/nfl-kc-lac-2025-09-05",
        "https://polymarket.com/event/nfl-dal-phi-2025-09-04"
    ]
    
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    for url in working_urls:
        print(f"\nTesting: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Look for market data in the HTML
                teams = extract_teams_from_url(url)
                print(f"Expected teams: {teams}")
                
                # Search for team names in content
                team_mentions = {}
                for team in teams:
                    count = content.upper().count(team.upper())
                    team_mentions[team] = count
                
                print(f"Team mentions: {team_mentions}")
                
                # Look for market-related data
                market_patterns = [
                    r'"market[^"]*":\s*{[^}]+}',
                    r'"condition[^"]*":\s*"[^"]+"',
                    r'"token[^"]*":\s*\[[^\]]+\]',
                    r'"price[^"]*":\s*[\d\.]+',
                    r'"outcome[^"]*":\s*"[^"]+"'
                ]
                
                found_patterns = []
                for pattern in market_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        found_patterns.extend(matches[:2])  # First 2 matches
                
                if found_patterns:
                    print("Found market data patterns:")
                    for pattern in found_patterns[:3]:
                        print(f"  {pattern[:100]}...")
                
                # Look for JSON data in script tags
                script_pattern = r'<script[^>]*>.*?({.*?"market".*?}|{.*?"condition".*?}|{.*?"token".*?}).*?</script>'
                script_matches = re.findall(script_pattern, content, re.DOTALL | re.IGNORECASE)
                
                if script_matches:
                    print("Found JSON in script tags:")
                    for match in script_matches[:2]:
                        try:
                            # Try to parse as JSON
                            data = json.loads(match)
                            print(f"  Parsed JSON keys: {list(data.keys())[:5]}")
                        except:
                            print(f"  JSON snippet: {match[:100]}...")
                
                # Check if page indicates market is active
                if any(word in content.lower() for word in ['active', 'trading', 'bet', 'odds']):
                    print("Page appears to have active market")
                
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

def extract_teams_from_url(url):
    """Extract team abbreviations from URL"""
    # Pattern: nfl-team1-team2-date
    pattern = r'nfl-([a-z]+)-([a-z]+)-\d{4}-\d{2}-\d{2}'
    match = re.search(pattern, url)
    
    if match:
        team1, team2 = match.groups()
        return [team1.upper(), team2.upper()]
    
    return []

def test_api_with_market_data():
    """Try to extract market IDs from web pages and use API"""
    print("\nTrying to extract market data for API calls...")
    print("=" * 60)
    
    # Try a different approach - look for the gamma API calls
    session = requests.Session()
    
    # Test direct API call patterns
    api_patterns = [
        "https://gamma-api.polymarket.com/markets?active=true&limit=100",
        "https://gamma-api.polymarket.com/events",
        "https://clob.polymarket.com/markets",
    ]
    
    for api_url in api_patterns:
        print(f"\nTesting API: {api_url}")
        try:
            response = session.get(api_url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    markets = data
                elif isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                else:
                    markets = []
                
                print(f"Found {len(markets)} markets")
                
                # Look for NFL markets
                nfl_markets = []
                for market in markets[:50]:  # Check first 50
                    if isinstance(market, dict):
                        question = market.get('question', '').lower()
                        if any(term in question for term in ['nfl', 'chiefs', 'chargers', 'eagles', 'cowboys', 'kc', 'lac', 'phi', 'dal']):
                            nfl_markets.append(market)
                
                print(f"NFL-related markets: {len(nfl_markets)}")
                
                for i, market in enumerate(nfl_markets[:3], 1):
                    print(f"  {i}. {market.get('question', 'N/A')}")
                    print(f"     Active: {not market.get('closed', False)}")
                    print(f"     ID: {market.get('id', 'N/A')}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_working_urls()
    test_api_with_market_data()