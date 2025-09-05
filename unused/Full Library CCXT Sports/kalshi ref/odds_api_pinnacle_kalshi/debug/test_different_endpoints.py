"""
Test different OddsAPI endpoint structures
"""

import requests
import json

def load_api_key():
    with open("keys/odds_api_key.txt", 'r') as f:
        content = f.read().strip()
        if "=" in content:
            return content.split("=")[1].strip().strip("'\"")
        return content

def test_endpoint_variations():
    """Test different endpoint structures"""
    api_key = load_api_key()
    
    endpoints_to_test = [
        "https://api.the-odds-api.com/v3/odds",
        "https://api.the-odds-api.com/v4/odds",
        "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
    ]
    
    params_v3 = {
        'apiKey': api_key,
        'sport': 'americanfootball_nfl',
        'region': 'us',
        'mkt': 'h2h'
    }
    
    params_v4 = {
        'apiKey': api_key,
        'sport': 'americanfootball_nfl',
        'regions': 'us',
        'markets': 'h2h'
    }
    
    params_v4_path = {
        'apiKey': api_key,
        'regions': 'us', 
        'markets': 'h2h'
    }
    
    param_sets = [params_v3, params_v4, params_v4_path]
    
    for i, (endpoint, params) in enumerate(zip(endpoints_to_test, param_sets)):
        print(f"\n=== Test {i+1}: {endpoint} ===")
        print(f"Params: {params}")
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"SUCCESS: Found {len(data)} items")
                        if data:
                            print(f"Sample item keys: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"SUCCESS: Response keys: {list(data.keys())}")
                    else:
                        print(f"SUCCESS: Response type: {type(data)}")
                except:
                    print(f"SUCCESS: Response length: {len(response.text)} chars")
            else:
                error_text = response.text[:200].replace('\n', ' ')
                print(f"ERROR {response.status_code}: {error_text}...")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")

def test_simple_baseball():
    """Test with the simplest baseball request possible"""
    api_key = load_api_key()
    
    print("\n=== Simple Baseball Test ===")
    
    # Try the most basic request structure
    urls_to_try = [
        "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds",
        "https://api.the-odds-api.com/v3/odds"  
    ]
    
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        try:
            if "v3" in url:
                params = {
                    'apiKey': api_key,
                    'sport': 'baseball_mlb',
                    'region': 'us'
                }
            else:
                params = {
                    'apiKey': api_key,
                    'regions': 'us'
                }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: {len(data) if isinstance(data, list) else 'Got response'}")
                break
            else:
                print(f"ERROR: {response.text[:100]}...")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_endpoint_variations()
    test_simple_baseball()