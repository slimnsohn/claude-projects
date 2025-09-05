"""
Test Polymarket API to see what markets are available
"""

import requests
import json

def test_polymarket_api():
    """Test raw API calls to Polymarket"""
    base_url = "https://gamma-api.polymarket.com"
    
    print("Testing Polymarket API...")
    print("=" * 60)
    
    # Test basic connection
    try:
        response = requests.get(f"{base_url}/markets", params={'limit': 5})
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check structure
            if isinstance(data, list):
                markets = data
            elif isinstance(data, dict) and 'data' in data:
                markets = data['data']
            else:
                markets = []
            
            print(f"Found {len(markets)} markets in test query")
            
            # Show first few markets
            for i, market in enumerate(markets[:3], 1):
                print(f"\nMarket {i}:")
                print(f"  Question: {market.get('question', 'N/A')[:80]}...")
                print(f"  Active: {market.get('active', 'N/A')}")
                volume = market.get('volume', 0)
                if isinstance(volume, (int, float)):
                    print(f"  Volume: ${volume:,.0f}")
                else:
                    print(f"  Volume: {volume}")
            
            # Search for NFL specifically
            print("\n" + "=" * 60)
            print("Searching for NFL markets...")
            
            nfl_response = requests.get(f"{base_url}/markets", params={
                'search': 'NFL',
                'limit': 10,
                'active': 'true'
            })
            
            if nfl_response.status_code == 200:
                nfl_data = nfl_response.json()
                
                if isinstance(nfl_data, list):
                    nfl_markets = nfl_data
                elif isinstance(nfl_data, dict) and 'data' in nfl_data:
                    nfl_markets = nfl_data['data']
                else:
                    nfl_markets = []
                
                print(f"Found {len(nfl_markets)} NFL-related markets")
                
                # Show NFL markets
                for i, market in enumerate(nfl_markets[:5], 1):
                    print(f"\nNFL Market {i}:")
                    print(f"  ID: {market.get('id', 'N/A')}")
                    print(f"  Question: {market.get('question', 'N/A')}")
                    print(f"  Active: {market.get('active', 'N/A')}")
                    
                    # Try to get details
                    if market.get('id'):
                        detail_response = requests.get(f"{base_url}/markets/{market['id']}")
                        if detail_response.status_code == 200:
                            details = detail_response.json()
                            outcomes = details.get('outcomes', [])
                            print(f"  Outcomes: {len(outcomes)}")
                            for outcome in outcomes[:2]:
                                price = float(outcome.get('price', 0))
                                print(f"    - {outcome.get('name', 'N/A')}: ${price:.3f} ({price*100:.1f}%)")
                            volume = details.get('volume', 0)
                            if isinstance(volume, (int, float)):
                                print(f"  Volume: ${volume:,.0f}")
                            else:
                                print(f"  Volume: {volume}")
                            print(f"  End Date: {details.get('end_date', 'N/A')}")
            
            # Try different search terms
            print("\n" + "=" * 60)
            print("Trying different search terms...")
            
            search_terms = ['football', 'NFL game', 'NFL win', 'NFL week', 'NFL 2024', 'NFL 2025']
            for term in search_terms:
                response = requests.get(f"{base_url}/markets", params={
                    'search': term,
                    'limit': 5,
                    'active': 'true'
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict) and 'data' in data:
                        count = len(data['data'])
                    else:
                        count = 0
                    print(f"  '{term}': {count} markets found")
            
        else:
            print(f"API returned status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_polymarket_api()