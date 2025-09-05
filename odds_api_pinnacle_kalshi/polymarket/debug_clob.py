"""
Debug Polymarket CLOB client response structure
"""

from py_clob_client.client import ClobClient
import json

def debug_clob():
    """Debug CLOB client responses"""
    print("Debugging Polymarket CLOB API...")
    print("=" * 60)
    
    # Initialize client
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137
    )
    
    try:
        # Get markets
        print("Fetching markets...")
        markets = client.get_markets()
        
        print(f"Markets type: {type(markets)}")
        print(f"Markets length: {len(markets) if hasattr(markets, '__len__') else 'N/A'}")
        
        if isinstance(markets, list):
            if len(markets) > 0:
                print("\nFirst market type:", type(markets[0]))
                if isinstance(markets[0], dict):
                    print("First market keys:", list(markets[0].keys()))
                    print("\nFirst market sample:")
                    print(json.dumps(markets[0], indent=2)[:1000])
                else:
                    print("First market value:", str(markets[0])[:200])
        elif isinstance(markets, dict):
            print("Markets dict keys:", list(markets.keys()))
            if 'data' in markets:
                print("Data type:", type(markets['data']))
        else:
            print("Markets value:", str(markets)[:500])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Try simplified markets endpoint
    print("\n" + "=" * 60)
    print("Trying simplified markets endpoint...")
    
    try:
        import requests
        response = requests.get("https://clob.polymarket.com/markets")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"Number of markets: {len(data)}")
                print("\nFirst market:")
                print(json.dumps(data[0], indent=2)[:1000])
                
                # Look for NFL markets
                nfl_markets = [m for m in data if 'nfl' in str(m).lower()]
                print(f"\nNFL-related markets: {len(nfl_markets)}")
                
                if nfl_markets:
                    print("\nFirst NFL market:")
                    print(json.dumps(nfl_markets[0], indent=2)[:800])
                    
    except Exception as e:
        print(f"Error with direct request: {e}")

if __name__ == "__main__":
    debug_clob()