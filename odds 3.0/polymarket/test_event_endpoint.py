"""
Test the event-specific endpoint that returned 200
"""

import requests
import json

def test_event_endpoint():
    """Test the event endpoint that worked"""
    
    url = "https://clob.polymarket.com/markets"
    
    # Test the event that returned 200
    params = {'event': 'nfl-bal-buf-2025-09-07'}
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== NFL BAL-BUF EVENT DATA ===")
            print(f"Keys: {list(data.keys())}")
            print(f"Data count: {data.get('count', 0)}")
            print(f"Markets found: {len(data.get('data', []))}")
            
            markets = data.get('data', [])
            if markets:
                print("\nMarket details:")
                for i, market in enumerate(markets):
                    question = market.get('question', 'N/A')
                    active = market.get('active', False)
                    closed = market.get('closed', True)
                    tokens = market.get('tokens', [])
                    
                    print(f"\n{i+1}. {question}")
                    print(f"   Active: {active}, Closed: {closed}")
                    print(f"   Tokens: {len(tokens)}")
                    
                    for token in tokens:
                        token_id = token.get('token_id', '')[:20] + '...' if token.get('token_id') else 'N/A'
                        outcome = token.get('outcome', 'N/A')
                        print(f"     - {outcome}: {token_id}")
                    
                    # Try to get prices for these tokens
                    if tokens and active and not closed:
                        print("   Prices:")
                        for token in tokens:
                            token_id = token.get('token_id')
                            if token_id:
                                try:
                                    price_url = "https://clob.polymarket.com/midpoint"
                                    price_params = {'token_id': token_id}
                                    price_resp = requests.get(price_url, params=price_params, timeout=5)
                                    
                                    if price_resp.status_code == 200:
                                        price_data = price_resp.json()
                                        midpoint = price_data.get('midpoint', 'N/A')
                                        print(f"     - {token.get('outcome')}: {midpoint}")
                                    else:
                                        print(f"     - {token.get('outcome')}: No price ({price_resp.status_code})")
                                except:
                                    print(f"     - {token.get('outcome')}: Price error")
            else:
                print("No markets found for this event")
                
        else:
            print(f"Error: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Exception: {e}")

    # Also test a few other potential event slugs
    print("\n" + "="*50)
    print("Testing other potential NFL events...")
    
    potential_events = [
        'nfl-2025-09-07',
        'nfl-week-1',
        'ravens-bills',
        'chiefs-raiders'
    ]
    
    for event in potential_events:
        try:
            params = {'event': event}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"{event}: {count} markets")
                
                if count > 0:
                    markets = data.get('data', [])
                    for market in markets[:3]:  # Show first 3
                        question = market.get('question', 'N/A')
                        active = market.get('active', False)
                        closed = market.get('closed', True)
                        print(f"  - {question} (Active: {active}, Closed: {closed})")
            else:
                print(f"{event}: Status {response.status_code}")
                
        except Exception as e:
            print(f"{event}: Error - {e}")

if __name__ == "__main__":
    test_event_endpoint()