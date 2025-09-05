"""
Debug Polymarket API structure
"""

import requests
import json

def debug_polymarket():
    """Debug raw API structure"""
    base_url = "https://gamma-api.polymarket.com"
    
    print("Debugging Polymarket API Structure...")
    print("=" * 60)
    
    # Get a single market
    response = requests.get(f"{base_url}/markets", params={'limit': 1})
    
    if response.status_code == 200:
        data = response.json()
        
        print("Response type:", type(data))
        
        if isinstance(data, list) and len(data) > 0:
            market = data[0]
            print("\nFirst market structure:")
            print("Keys:", list(market.keys()))
            print("\nSample market:")
            print(json.dumps(market, indent=2)[:1000])
        elif isinstance(data, dict):
            print("Dict keys:", list(data.keys()))
            if 'data' in data:
                print("\nData is nested under 'data' key")
                markets = data['data']
                if markets and len(markets) > 0:
                    print("First market keys:", list(markets[0].keys()))
        
        # Try searching for NFL
        print("\n" + "=" * 60)
        print("Searching for 'NFL'...")
        
        nfl_response = requests.get(f"{base_url}/markets", params={
            'search': 'NFL',
            'limit': 2
        })
        
        if nfl_response.status_code == 200:
            nfl_data = nfl_response.json()
            print("NFL search response type:", type(nfl_data))
            
            if isinstance(nfl_data, list):
                print(f"Found {len(nfl_data)} results")
                if len(nfl_data) > 0:
                    print("\nFirst NFL result:")
                    print(json.dumps(nfl_data[0], indent=2)[:1500])
        
        # Try getting market details
        print("\n" + "=" * 60)
        print("Testing market details endpoint...")
        
        # Get first market ID
        first_market_id = None
        if isinstance(data, list) and len(data) > 0:
            first_market_id = data[0].get('id')
        
        if first_market_id:
            print(f"Getting details for market ID: {first_market_id}")
            detail_response = requests.get(f"{base_url}/markets/{first_market_id}")
            
            if detail_response.status_code == 200:
                details = detail_response.json()
                print("Detail response type:", type(details))
                
                if isinstance(details, dict):
                    print("Detail keys:", list(details.keys()))
                    
                    # Check for outcomes
                    if 'outcomes' in details:
                        outcomes = details['outcomes']
                        print(f"\nOutcomes type: {type(outcomes)}")
                        if isinstance(outcomes, str):
                            # It might be a JSON string
                            try:
                                outcomes = json.loads(outcomes)
                                print("Parsed outcomes from string")
                            except:
                                print("Could not parse outcomes string")
                        
                        if isinstance(outcomes, list) and len(outcomes) > 0:
                            print(f"Number of outcomes: {len(outcomes)}")
                            print("First outcome:")
                            print(json.dumps(outcomes[0], indent=2)[:500])

if __name__ == "__main__":
    debug_polymarket()