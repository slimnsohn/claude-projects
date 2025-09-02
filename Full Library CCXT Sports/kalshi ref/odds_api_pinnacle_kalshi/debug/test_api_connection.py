"""
Test OddsAPI connection and available sports/bookmakers
"""

import requests
import json

def load_api_key():
    with open("keys/odds_api_key.txt", 'r') as f:
        content = f.read().strip()
        if "=" in content:
            return content.split("=")[1].strip().strip("'\"")
        return content

def test_api_connection():
    """Test basic API connectivity and available sports"""
    api_key = load_api_key()
    base_url = "https://api.the-odds-api.com/v4"
    
    print("Testing OddsAPI connection...")
    print(f"API Key: {api_key[:10]}...")
    
    # Test 1: Get available sports
    print("\n=== AVAILABLE SPORTS ===")
    try:
        sports_response = requests.get(f"{base_url}/sports", params={'apiKey': api_key})
        sports_response.raise_for_status()
        sports = sports_response.json()
        
        mlb_sports = [s for s in sports if 'baseball' in s.get('key', '').lower()]
        print(f"MLB-related sports found: {len(mlb_sports)}")
        for sport in mlb_sports:
            print(f"  - {sport['key']}: {sport['title']} (active: {sport.get('active', False)})")
            
    except Exception as e:
        print(f"Error getting sports: {e}")
        return
    
    # Test 2: Check what's currently available for baseball
    print("\n=== TESTING BASEBALL SPORTS ===")
    for sport in mlb_sports:
        sport_key = sport['key']
        print(f"\nTesting {sport_key}...")
        
        try:
            odds_response = requests.get(
                f"{base_url}/odds",
                params={
                    'apiKey': api_key,
                    'sport': sport_key,
                    'regions': 'us',
                    'markets': 'h2h',
                    'oddsFormat': 'american'
                }
            )
            
            if odds_response.status_code == 200:
                data = odds_response.json()
                print(f"  SUCCESS: {len(data)} games found")
                
                # Check available bookmakers
                if data:
                    bookmakers = set()
                    for game in data[:3]:  # Check first 3 games
                        for book in game.get('bookmakers', []):
                            bookmakers.add(book.get('key'))
                    print(f"  Available bookmakers: {sorted(bookmakers)}")
                    print(f"  Pinnacle available: {'pinnacle' in bookmakers}")
                    
            else:
                print(f"  ERROR {odds_response.status_code}: {odds_response.text[:100]}...")
                
        except Exception as e:
            print(f"  EXCEPTION: {e}")

if __name__ == "__main__":
    test_api_connection()