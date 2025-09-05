"""
Fetch current NFL markets from Polymarket
"""

from py_clob_client.client import ClobClient
import json
from datetime import datetime

def fetch_current_nfl():
    """Fetch and display current NFL markets"""
    print("Fetching current NFL markets from Polymarket...")
    print("=" * 80)
    
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137
    )
    
    # Get markets
    response = client.get_markets()
    
    if isinstance(response, dict) and 'data' in response:
        markets = response['data']
    else:
        markets = response if isinstance(response, list) else []
    
    print(f"Total markets fetched: {len(markets)}")
    
    # Find NFL markets
    nfl_markets = []
    for market in markets:
        if isinstance(market, dict):
            question = market.get('question', '').lower()
            if 'nfl' in question or any(team in question for team in [
                'chiefs', 'bills', 'eagles', 'cowboys', '49ers', 'ravens',
                'bengals', 'lions', 'packers', 'dolphins', 'rams', 'browns'
            ]):
                nfl_markets.append(market)
    
    print(f"Found {len(nfl_markets)} NFL-related markets")
    
    # Categorize markets
    game_markets = []
    prop_markets = []
    future_markets = []
    
    for market in nfl_markets:
        question = market.get('question', '')
        q_lower = question.lower()
        
        # Check if it's closed
        is_closed = market.get('closed', False)
        
        # Categorize
        if any(word in q_lower for word in ['win', 'beat', 'defeat']) and not any(word in q_lower for word in ['super bowl', 'championship', 'season']):
            game_markets.append(market)
        elif any(word in q_lower for word in ['touchdown', 'yard', 'pass', 'reception']):
            prop_markets.append(market)
        else:
            future_markets.append(market)
    
    # Display results
    print(f"\nMarket Breakdown:")
    print(f"  Game Winners: {len(game_markets)}")
    print(f"  Props: {len(prop_markets)}")
    print(f"  Futures: {len(future_markets)}")
    
    if game_markets:
        print(f"\n{'='*80}")
        print("GAME WINNER MARKETS")
        print('='*80)
        
        for i, market in enumerate(game_markets[:10], 1):
            print(f"\n{i}. {market.get('question', 'N/A')}")
            print(f"   Market ID: {market.get('condition_id', 'N/A')[:20]}...")
            print(f"   Active: {not market.get('closed', False)}")
            print(f"   Volume: ${market.get('volume', 0):,.0f}")
            
            # Check for tokens/outcomes
            tokens = market.get('tokens', [])
            if tokens:
                print(f"   Outcomes: {len(tokens)}")
                for token in tokens[:2]:
                    if isinstance(token, dict):
                        outcome = token.get('outcome', 'N/A')
                        price = token.get('price', 0)
                        print(f"     - {outcome}: ${price:.3f}")
            
            # Check end date
            end_date = market.get('end_date_iso')
            if end_date:
                try:
                    dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    print(f"   Game Date: {dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    pass
    
    # Try searching for specific current games
    print(f"\n{'='*80}")
    print("SEARCHING FOR CURRENT NFL GAMES")
    print('='*80)
    
    search_terms = ['NFL Week', 'NFL 2024', 'NFL 2025', 'NFL game', 'football game']
    
    for term in search_terms:
        print(f"\nSearching for '{term}'...")
        try:
            # Search markets - get_markets doesn't take search param
            search_response = client.get_markets()
            if isinstance(search_response, dict) and 'data' in search_response:
                results = search_response['data']
            else:
                results = search_response if isinstance(search_response, list) else []
            
            print(f"  Found {len(results)} results")
            
            if results:
                for market in results[:3]:
                    if isinstance(market, dict):
                        print(f"  - {market.get('question', 'N/A')[:70]}...")
                        
        except Exception as e:
            print(f"  Error searching: {e}")

if __name__ == "__main__":
    fetch_current_nfl()