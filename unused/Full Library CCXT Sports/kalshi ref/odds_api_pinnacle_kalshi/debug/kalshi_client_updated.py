"""
Updated Kalshi API Client - Uses new endpoints and handles current market reality
Development version for testing and validation
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time

class KalshiClientUpdated:
    def __init__(self, credentials_file: str):
        """Initialize Kalshi client with new API endpoints"""
        # Use the working demo endpoint for now
        self.base_url = "https://demo-api.kalshi.co/trade-api/v2"
        self.production_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.credentials = self._load_credentials(credentials_file)
        self.session_token = None
        
    def _load_credentials(self, creds_file: str) -> Dict:
        """Load Kalshi credentials from file"""
        try:
            credentials = {}
            with open(creds_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        credentials[key] = value
            return credentials
        except FileNotFoundError:
            raise ValueError(f"Credentials file not found: {creds_file}")
    
    def get_all_markets(self) -> Dict:
        """Fetch all available markets from Kalshi"""
        url = f"{self.base_url}/markets"
        
        try:
            print("Fetching all Kalshi markets...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            markets = data.get('markets', [])
            
            print(f"Successfully fetched {len(markets)} markets from Kalshi")
            
            return {
                'success': True,
                'data': markets,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'kalshi_demo_api'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Kalshi markets: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    
    def search_sports_markets(self) -> Dict:
        """Search for any sports-related markets in the available data"""
        all_markets = self.get_all_markets()
        
        if not all_markets.get('success'):
            return all_markets
        
        sports_keywords = [
            'mlb', 'baseball', 'world series', 'yankees', 'dodgers', 'red sox', 
            'mets', 'giants', 'braves', 'astros', 'cubs', 'sport', 'football', 
            'basketball', 'nba', 'nfl', 'college', 'playoff', 'championship',
            'tennis', 'match', 'tournament', 'vs', 'win', 'beat'
        ]
        
        sports_markets = []
        all_markets_data = all_markets.get('data', [])
        
        for market in all_markets_data:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '').lower()
            
            if any(keyword in title or keyword in ticker for keyword in sports_keywords):
                sports_markets.append(market)
        
        print(f"Found {len(sports_markets)} sports-related markets out of {len(all_markets_data)} total")
        
        return {
            'success': True,
            'data': sports_markets,
            'total_markets': len(all_markets_data),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_sports_search'
        }
    
    def create_mock_mlb_data(self) -> Dict:
        """Create mock MLB market data for demonstration purposes"""
        print("Creating mock MLB market data for demonstration...")
        
        mock_games = [
            {
                'ticker': 'MOCKMLB-25AUG21-MINOAK',
                'title': 'Will Minnesota Twins beat Oakland Athletics on Aug 21?',
                'yes_price': 4500,  # 45% 
                'no_price': 5500,   # 55% 
                'close_time': '2025-08-21T17:11:00Z',
                'category': 'sports',
                'status': 'open'
            },
            {
                'ticker': 'MOCKMLB-25AUG21-NYYBAL',
                'title': 'Will New York Yankees beat Baltimore Orioles on Aug 21?',
                'yes_price': 6000,  # 60% 
                'no_price': 4000,   # 40% 
                'close_time': '2025-08-21T19:05:00Z',
                'category': 'sports',
                'status': 'open'
            },
            {
                'ticker': 'MOCKMLB-25AUG21-LADSD',
                'title': 'Will Los Angeles Dodgers beat San Diego Padres on Aug 21?',
                'yes_price': 5200,  # 52% 
                'no_price': 4800,   # 48% 
                'close_time': '2025-08-21T22:10:00Z',
                'category': 'sports',
                'status': 'open'
            }
        ]
        
        return {
            'success': True,
            'data': mock_games,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_mock_data',
            'note': 'Mock data for demonstration purposes'
        }
    
    def create_mock_mlb_data(self) -> Dict:
        """Create mock MLB market data for demonstration purposes"""
        print("Creating mock MLB market data for demonstration...")
        
        mock_games = [
            {
                'ticker': 'MOCKMLB-25AUG21-MINOAK',
                'title': 'Will Minnesota Twins beat Oakland Athletics on Aug 21?',
                'yes_price': 4500,  # 45% = +122 odds
                'no_price': 5500,   # 55% = -122 odds
                'close_time': '2025-08-21T17:11:00Z',
                'category': 'sports',
                'status': 'open'
            },
            {
                'ticker': 'MOCKMLB-25AUG21-NYYBAL',
                'title': 'Will New York Yankees beat Baltimore Orioles on Aug 21?',
                'yes_price': 6000,  # 60% = -150 odds
                'no_price': 4000,   # 40% = +150 odds
                'close_time': '2025-08-21T19:05:00Z',
                'category': 'sports',
                'status': 'open'
            },
            {
                'ticker': 'MOCKMLB-25AUG21-LADSD',
                'title': 'Will Los Angeles Dodgers beat San Diego Padres on Aug 21?',
                'yes_price': 5200,  # 52% = -108 odds
                'no_price': 4800,   # 48% = +108 odds
                'close_time': '2025-08-21T22:10:00Z',
                'category': 'sports',
                'status': 'open'
            }
        ]
        
        return {
            'success': True,
            'data': mock_games,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'kalshi_mock_data',
            'note': 'This is mock data for demonstration purposes'
        }
    
    def normalize_kalshi_data(self, raw_data: Dict, use_mock: bool = False) -> List[Dict]:
        """Convert Kalshi API response to normalized schema"""
        if not raw_data.get('success'):
            return []
        
        normalized_games = []
        
        for market in raw_data.get('data', []):
            try:
                # Extract basic market info
                market_id = market.get('ticker')
                title = market.get('title', '')
                
                # For mock data or real sports markets, try to extract team info
                if use_mock or 'beat' in title.lower() or 'vs' in title.lower():
                    teams = self._extract_teams_from_title(title)
                    if not teams:
                        print(f"Could not extract teams from market: {title}")
                        continue
                    
                    home_team, away_team = teams
                    
                    # Get market pricing
                    yes_price = market.get('yes_price', 5000) / 10000.0  # Convert to percentage
                    no_price = market.get('no_price', 5000) / 10000.0
                    
                    # Convert Kalshi prices to odds
                    home_odds = self._kalshi_price_to_odds(yes_price)
                    away_odds = self._kalshi_price_to_odds(no_price)
                    
                    # Extract game date/time
                    event_date = market.get('close_time', market.get('expire_time'))
                    game_date = event_date[:10] if event_date else None
                    
                    normalized_game = {
                        "game_id": f"kalshi_{market_id}",
                        "game_date": game_date,
                        "game_time": event_date,
                        "sport": "MLB",
                        "home_team": self._standardize_team_name(home_team),
                        "away_team": self._standardize_team_name(away_team),
                        "source": "kalshi",
                        "home_odds": home_odds,
                        "away_odds": away_odds,
                        "metadata": {
                            "last_updated": raw_data.get('timestamp'),
                            "bookmaker": "kalshi",
                            "market_type": "prediction_market",
                            "raw_data": market,
                            "kalshi_yes_price": yes_price,
                            "kalshi_no_price": no_price
                        }
                    }
                    
                    normalized_games.append(normalized_game)
                    
            except Exception as e:
                print(f"Error normalizing Kalshi market: {e}")
                continue
        
        print(f"Successfully normalized {len(normalized_games)} games from Kalshi")
        return normalized_games
    
    def _extract_teams_from_title(self, title: str) -> Optional[tuple]:
        """Extract team names from Kalshi market title"""
        import re
        
        # Pattern for "Will X beat Y" format
        beat_pattern = r'Will (.+?) beat (.+?)(?: on| \?|$)'
        match = re.search(beat_pattern, title, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return (team2, team1)  # (home, away) - team being beaten is home
        
        # Pattern for "X vs Y" format
        vs_pattern = r'(.+?) vs (.+?)(?: |$)'
        match = re.search(vs_pattern, title, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            return (team2, team1)  # Assume second team is home
        
        return None
    
    def _kalshi_price_to_odds(self, price: float, fee: float = 0.03) -> Dict:
        """Convert Kalshi percentage price to odds object"""
        if price <= 0 or price >= 1:
            price = 0.5
        
        # For demonstration, let's not apply fees since these are mock markets
        adjusted_price = price  # price * (1 - fee) for real markets
        
        # Convert to American odds
        if adjusted_price >= 0.5:
            american_odds = int(-100 * adjusted_price / (1 - adjusted_price))
        else:
            american_odds = int(100 * (1 - adjusted_price) / adjusted_price)
        
        # Calculate decimal odds and implied probability
        decimal_odds = self._american_to_decimal(american_odds)
        implied_prob = self._decimal_to_probability(decimal_odds)
        
        return {
            "american": american_odds,
            "decimal": decimal_odds,
            "implied_probability": implied_prob
        }
    
    def _american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def _decimal_to_probability(self, decimal_odds: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1 / decimal_odds
    
    def _standardize_team_name(self, team_name: str) -> str:
        """Standardize team names for consistent matching"""
        team_mappings = {
            "Los Angeles Angels": "LAA", "Angels": "LAA",
            "Houston Astros": "HOU", "Astros": "HOU",
            "Oakland Athletics": "OAK", "Athletics": "OAK", "A's": "OAK",
            "Toronto Blue Jays": "TOR", "Blue Jays": "TOR", "Jays": "TOR",
            "Atlanta Braves": "ATL", "Braves": "ATL",
            "Milwaukee Brewers": "MIL", "Brewers": "MIL",
            "St. Louis Cardinals": "STL", "Cardinals": "STL",
            "Chicago Cubs": "CHC", "Cubs": "CHC",
            "Arizona Diamondbacks": "ARI", "Diamondbacks": "ARI", "D-backs": "ARI",
            "Colorado Rockies": "COL", "Rockies": "COL",
            "Los Angeles Dodgers": "LAD", "Dodgers": "LAD",
            "San Diego Padres": "SD", "Padres": "SD", "Padres": "SD",
            "San Francisco Giants": "SF", "Giants": "SF",
            "Miami Marlins": "MIA", "Marlins": "MIA",
            "New York Mets": "NYM", "Mets": "NYM",
            "Philadelphia Phillies": "PHI", "Phillies": "PHI",
            "Pittsburgh Pirates": "PIT", "Pirates": "PIT",
            "Washington Nationals": "WSH", "Nationals": "WSH",
            "Chicago White Sox": "CWS", "White Sox": "CWS",
            "Cleveland Guardians": "CLE", "Guardians": "CLE",
            "Detroit Tigers": "DET", "Tigers": "DET",
            "Kansas City Royals": "KC", "Royals": "KC",
            "Minnesota Twins": "MIN", "Twins": "MIN",
            "New York Yankees": "NYY", "Yankees": "NYY",
            "Baltimore Orioles": "BAL", "Orioles": "BAL",
            "Boston Red Sox": "BOS", "Red Sox": "BOS",
            "Tampa Bay Rays": "TB", "Rays": "TB",
            "Texas Rangers": "TEX", "Rangers": "TEX",
            "Seattle Mariners": "SEA", "Mariners": "SEA"
        }
        
        return team_mappings.get(team_name, team_name)

# Test function for development
def test_updated_kalshi_client():
    """Test the updated Kalshi client functionality"""
    try:
        client = KalshiClientUpdated("keys/kalshi_credentials.txt")
        
        # Test 1: Search for real sports markets
        print("=== SEARCHING FOR REAL SPORTS MARKETS ===")
        sports_data = client.search_sports_markets()
        print(f"Found {len(sports_data.get('data', []))} sports markets")
        
        if sports_data.get('data'):
            print("\nReal sports markets found:")
            for market in sports_data['data'][:3]:
                print(f"  - {market.get('ticker')}: {market.get('title')}")
        
        # Test 2: Use mock MLB data for demonstration
        print(f"\n=== USING MOCK MLB DATA ===")
        mock_data = client.create_mock_mlb_data()
        normalized_games = client.normalize_kalshi_data(mock_data, use_mock=True)
        
        print(f"Normalized {len(normalized_games)} mock games")
        if normalized_games:
            print(f"\nSample normalized game:")
            print(json.dumps(normalized_games[0], indent=2))
        
        return normalized_games
        
    except Exception as e:
        print(f"Test failed: {e}")
        return []

if __name__ == "__main__":
    test_updated_kalshi_client()