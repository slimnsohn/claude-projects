"""
Test Polymarket Gamma API for active sports markets
"""

import requests
import json
from datetime import datetime

def test_gamma_sports():
    """Test Gamma API for sports markets"""
    
    gamma_url = "https://gamma-api.polymarket.com/markets"
    
    print("=== POLYMARKET GAMMA API SPORTS TEST ===")
    print("="*60)
    
    try:
        # Get markets from Gamma API
        response = requests.get(gamma_url, timeout=15)
        
        if response.status_code == 200:
            markets = response.json()
            print(f"Total markets from Gamma API: {len(markets)}")
            
            # Look for active sports markets
            sports_keywords = [
                'nfl', 'football', 'mlb', 'baseball', 'nba', 'basketball', 
                'nhl', 'hockey', 'chiefs', 'patriots', 'cowboys', 'yankees', 
                'lakers', 'vs', 'win', 'game', 'match'
            ]
            
            active_sports = []
            all_sports = []
            
            for market in markets:
                question = market.get('question', '').lower()
                category = market.get('category', '').lower()
                active = market.get('active', False)
                closed = market.get('closed', True)
                
                # Check if it's a sports market
                if (any(keyword in question or keyword in category for keyword in sports_keywords) and
                    ('vs' in question or 'win' in question)):
                    
                    all_sports.append(market)
                    
                    if active and not closed:
                        active_sports.append(market)
            
            print(f"Total sports markets found: {len(all_sports)}")
            print(f"Active sports markets: {len(active_sports)}")
            
            # Show active sports markets
            if active_sports:
                print("\nACTIVE SPORTS MARKETS:")
                print("-" * 80)
                
                for i, market in enumerate(active_sports[:10], 1):
                    question = market.get('question')
                    slug = market.get('slug')
                    category = market.get('category')
                    end_date = market.get('endDate')
                    outcomes = market.get('outcomes', [])
                    prices = market.get('outcomePrices', [])
                    
                    print(f"{i}. {question}")
                    print(f"   Category: {category}")
                    print(f"   Slug: {slug}")
                    print(f"   End Date: {end_date}")
                    print(f"   Outcomes: {[o for o in outcomes]}")
                    print(f"   Prices: {prices}")
                    print()
            else:
                print("\nNo active sports markets found.")
                print("\nShowing recent CLOSED sports markets:")
                print("-" * 80)
                
                # Show recent closed sports markets
                for i, market in enumerate(all_sports[:10], 1):
                    question = market.get('question')
                    category = market.get('category')
                    active = market.get('active', False)
                    closed = market.get('closed', True)
                    
                    status = "ACTIVE" if active and not closed else "CLOSED"
                    
                    print(f"{i}. [{status}] {question}")
                    print(f"   Category: {category}")
                    print()
                    
        else:
            print(f"Gamma API error: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Exception testing Gamma API: {e}")

if __name__ == "__main__":
    test_gamma_sports()