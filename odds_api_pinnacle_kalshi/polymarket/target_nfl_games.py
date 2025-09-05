"""
Target specific NFL games on Polymarket using URL patterns and direct searches
Based on examples: https://polymarket.com/event/nfl-kc-lac-2025-09-05 and https://polymarket.com/event/nfl-dal-phi-2025-09-04
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class PolymarketNFLTargeter:
    def __init__(self):
        self.base_api_url = "https://gamma-api.polymarket.com"
        self.web_base_url = "https://polymarket.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'NFL-Game-Fetcher/1.0'
        })
        
        # Real games from Kalshi data
        self.target_games = [
            {'teams': ['PHI', 'DAL'], 'date': '2025-09-05'},
            {'teams': ['KC', 'LAC'], 'date': '2025-09-06'},
            {'teams': ['DEN', 'TEN'], 'date': '2025-09-07'},
            {'teams': ['ARI', 'NO'], 'date': '2025-09-07'},
            {'teams': ['WAS', 'NYG'], 'date': '2025-09-07'},
            {'teams': ['CIN', 'CLE'], 'date': '2025-09-07'},
            {'teams': ['JAX', 'CAR'], 'date': '2025-09-07'},
            {'teams': ['BAL', 'BUF'], 'date': '2025-09-08'},
            {'teams': ['MIN', 'CHI'], 'date': '2025-09-09'},
        ]

    def test_direct_market_urls(self):
        """Test direct market URLs based on the patterns provided"""
        print("Testing direct Polymarket URLs...")
        print("=" * 80)
        
        # Test the exact examples provided
        examples = [
            "nfl-kc-lac-2025-09-05",
            "nfl-dal-phi-2025-09-04",  # Note: this might be 09-05 based on our data
            "nfl-phi-dal-2025-09-05"   # Try reversed order
        ]
        
        for slug in examples:
            print(f"\nTesting: {slug}")
            
            # Try web scraping approach
            web_url = f"{self.web_base_url}/event/{slug}"
            try:
                response = self.session.get(web_url)
                print(f"  Web URL ({web_url}): {response.status_code}")
                
                if response.status_code == 200:
                    # Look for market data in the page
                    content = response.text
                    if 'market' in content.lower() and any(team in content.upper() for team in ['KC', 'LAC', 'DAL', 'PHI']):
                        print(f"  SUCCESS: Found market page with team references")
                    else:
                        print(f"  FAIL: Page loaded but no market data found")
                        
            except Exception as e:
                print(f"  Error accessing web URL: {e}")
            
            # Try API approaches
            api_endpoints = [
                f"/markets/{slug}",
                f"/events/{slug}",
                f"/market/{slug}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    api_url = f"{self.base_api_url}{endpoint}"
                    response = self.session.get(api_url)
                    print(f"  API ({endpoint}): {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    SUCCESS: Got data: {type(data)} with {len(data) if hasattr(data, '__len__') else 'unknown'} items")
                        
                        # Look for relevant fields
                        if isinstance(data, dict):
                            relevant_keys = [k for k in data.keys() if any(word in k.lower() for word in ['question', 'market', 'outcome', 'token'])]
                            if relevant_keys:
                                print(f"    Relevant keys: {relevant_keys}")
                                
                except Exception as e:
                    print(f"  Error with {endpoint}: {e}")

    def generate_market_slugs(self):
        """Generate potential market slugs for target games"""
        print("\nGenerating market slugs for target games...")
        print("=" * 80)
        
        slugs = []
        
        for game in self.target_games:
            teams = game['teams']
            date = game['date']
            
            # Different slug patterns to try
            patterns = [
                f"nfl-{teams[0].lower()}-{teams[1].lower()}-{date}",
                f"nfl-{teams[1].lower()}-{teams[0].lower()}-{date}",
                f"{teams[0].lower()}-vs-{teams[1].lower()}-{date}",
                f"{teams[1].lower()}-vs-{teams[0].lower()}-{date}",
                f"nfl-game-{teams[0].lower()}-{teams[1].lower()}-{date}",
                f"who-will-win-{teams[0].lower()}-vs-{teams[1].lower()}-{date}",
            ]
            
            for pattern in patterns:
                slugs.append({
                    'slug': pattern,
                    'teams': teams,
                    'date': date
                })
        
        print(f"Generated {len(slugs)} potential slugs")
        return slugs

    def test_generated_slugs(self, limit=10):
        """Test generated slugs"""
        slugs = self.generate_market_slugs()
        
        print(f"\nTesting first {limit} generated slugs...")
        print("=" * 80)
        
        found_markets = []
        
        for i, slug_info in enumerate(slugs[:limit]):
            slug = slug_info['slug']
            teams = slug_info['teams']
            
            print(f"\n{i+1}. Testing: {slug} ({teams[0]} vs {teams[1]})")
            
            # Test web URL
            web_url = f"{self.web_base_url}/event/{slug}"
            try:
                response = self.session.get(web_url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ Web URL works: {response.status_code}")
                    found_markets.append({
                        'slug': slug,
                        'teams': teams,
                        'url': web_url,
                        'type': 'web'
                    })
                else:
                    print(f"  ❌ Web URL: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Web URL error: {str(e)[:50]}...")
        
        if found_markets:
            print(f"\nFOUND {len(found_markets)} WORKING MARKETS:")
            for market in found_markets:
                print(f"  - {market['teams'][0]} vs {market['teams'][1]}: {market['url']}")
        
        return found_markets

    def search_markets_by_team_names(self):
        """Search markets using team name patterns"""
        print("\nSearching markets by team names...")
        print("=" * 80)
        
        # Get all markets and filter by team names
        try:
            response = self.session.get(f"{self.base_api_url}/markets", params={'limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    markets = data
                elif isinstance(data, dict) and 'data' in data:
                    markets = data['data']
                else:
                    markets = []
                
                print(f"Retrieved {len(markets)} total markets")
                
                # Look for NFL markets with our target teams
                nfl_markets = []
                team_names = set()
                
                for game in self.target_games:
                    team_names.update(game['teams'])
                
                print(f"Looking for teams: {sorted(team_names)}")
                
                for market in markets:
                    if isinstance(market, dict):
                        question = market.get('question', '').upper()
                        
                        # Check if it contains our target teams
                        found_teams = [team for team in team_names if team in question]
                        
                        if len(found_teams) >= 1:  # At least one team
                            nfl_markets.append({
                                'market': market,
                                'found_teams': found_teams,
                                'question': market.get('question', '')
                            })
                
                print(f"\nFound {len(nfl_markets)} markets with target teams:")
                
                for i, match in enumerate(nfl_markets[:10], 1):  # Show first 10
                    print(f"{i}. Teams found: {match['found_teams']}")
                    print(f"   Question: {match['question']}")
                    print(f"   Active: {not match['market'].get('closed', False)}")
                    print(f"   Market ID: {match['market'].get('id', 'N/A')}")
                    
                    # Check if it has outcomes
                    outcomes = match['market'].get('outcomes', [])
                    if isinstance(outcomes, str):
                        try:
                            outcomes = json.loads(outcomes)
                        except:
                            pass
                    
                    if outcomes and isinstance(outcomes, list):
                        print(f"   Outcomes: {outcomes}")
                    print()
                
                return nfl_markets[:10]
                
        except Exception as e:
            print(f"Error searching markets: {e}")
            return []

    def test_alternative_endpoints(self):
        """Test alternative API endpoints"""
        print("\nTesting alternative API endpoints...")
        print("=" * 80)
        
        endpoints = [
            "/events",
            "/events/nfl",
            "/markets/nfl", 
            "/categories/sports",
            "/categories/nfl",
            "/search?q=nfl",
            "/search?q=KC",
            "/search?q=Chiefs",
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_api_url}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                print(f"{endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        data_type = type(data)
                        
                        if isinstance(data, list):
                            print(f"  ✅ Got {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"  ✅ Got dict with keys: {list(data.keys())[:5]}")
                            if 'data' in data and isinstance(data['data'], list):
                                print(f"      Contains {len(data['data'])} data items")
                        else:
                            print(f"  ✅ Got {data_type}")
                            
                    except:
                        print(f"  ✅ Got non-JSON response")
                else:
                    print(f"  ❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"{endpoint}: Error - {str(e)[:50]}...")

def main():
    """Main testing function"""
    print("POLYMARKET NFL GAME TARGETING")
    print("=" * 80)
    print("Based on URL patterns:")
    print("- https://polymarket.com/event/nfl-kc-lac-2025-09-05")
    print("- https://polymarket.com/event/nfl-dal-phi-2025-09-04")
    print("=" * 80)
    
    targeter = PolymarketNFLTargeter()
    
    # Test 1: Direct URLs
    targeter.test_direct_market_urls()
    
    # Test 2: Generated slugs 
    found_markets = targeter.test_generated_slugs(limit=8)
    
    # Test 3: Search by team names
    team_matches = targeter.search_markets_by_team_names()
    
    # Test 4: Alternative endpoints
    targeter.test_alternative_endpoints()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Working market URLs found: {len(found_markets) if 'found_markets' in locals() else 0}")
    print(f"Team name matches found: {len(team_matches) if 'team_matches' in locals() else 0}")

if __name__ == "__main__":
    main()