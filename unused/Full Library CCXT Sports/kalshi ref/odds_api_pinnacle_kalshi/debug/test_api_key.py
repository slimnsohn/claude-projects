"""
Test if the API key is valid by trying different endpoints and sports
"""

import requests
import json

def load_api_key():
    with open("keys/odds_api_key.txt", 'r') as f:
        content = f.read().strip()
        if "=" in content:
            return content.split("=")[1].strip().strip("'\"")
        return content

def test_api_key_validity():
    """Test API key with multiple approaches"""
    api_key = load_api_key()
    base_url = "https://api.the-odds-api.com/v4"
    
    print(f"Testing API key: {api_key}")
    
    # Test 1: Sports endpoint (should always work)
    print("\n=== Testing /sports endpoint ===")
    try:
        response = requests.get(f"{base_url}/sports", params={'apiKey': api_key})
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            active_sports = [s for s in data if s.get('active', False)]
            print(f"SUCCESS: Found {len(active_sports)} active sports")
            
            # Show some active sports
            for sport in active_sports[:5]:
                print(f"  - {sport['key']}: {sport['title']}")
                
        else:
            print(f"ERROR: {response.text}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 2: Try a popular active sport (NFL)
    print("\n=== Testing American Football NFL ===")
    try:
        response = requests.get(
            f"{base_url}/odds",
            params={
                'apiKey': api_key,
                'sport': 'americanfootball_nfl',
                'regions': 'us',
                'markets': 'h2h'
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Found {len(data)} NFL games")
            if data:
                game = data[0]
                print(f"Sample game: {game.get('away_team')} @ {game.get('home_team')}")
                bookmakers = [b.get('key') for b in game.get('bookmakers', [])]
                print(f"Available bookmakers: {bookmakers[:5]}...")  
                print(f"Pinnacle available: {'pinnacle' in bookmakers}")
        else:
            print(f"ERROR: {response.text[:200]}...")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
    
    # Test 3: Check quota/usage
    print("\n=== Checking API usage ===")
    try:
        response = requests.get(f"{base_url}/sports", params={'apiKey': api_key})
        if response.status_code == 200:
            remaining = response.headers.get('x-requests-remaining')
            used = response.headers.get('x-requests-used') 
            print(f"Requests remaining: {remaining}")
            print(f"Requests used: {used}")
        
    except Exception as e:
        print(f"EXCEPTION checking usage: {e}")

if __name__ == "__main__":
    test_api_key_validity()