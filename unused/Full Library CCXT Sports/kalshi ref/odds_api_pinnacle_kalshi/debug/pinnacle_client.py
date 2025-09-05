"""
Pinnacle API Client for MLB Moneyline Odds via OddsAPI
Development version for testing and validation
"""

import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time

class PinnacleClient:
    def __init__(self, api_key_file: str):
        """Initialize Pinnacle client with OddsAPI key"""
        self.base_url = "https://api.the-odds-api.com/v4"
        self.api_key = self._load_api_key(api_key_file)
        self.sport = "baseball_mlb"
        self.bookmaker = "pinnacle"
        self.market = "h2h"  # Head-to-head (moneyline)
        self.region = "us"
        
    def _load_api_key(self, key_file: str) -> str:
        """Load API key from file"""
        try:
            with open(key_file, 'r') as f:
                content = f.read().strip()
                # Handle format: api_key = 'value' or just the key value
                if "=" in content:
                    return content.split("=")[1].strip().strip("'\"")
                return content
        except FileNotFoundError:
            raise ValueError(f"API key file not found: {key_file}")
    
    def get_mlb_odds(self) -> Dict:
        """Fetch MLB moneyline odds from Pinnacle via OddsAPI"""
        url = f"{self.base_url}/sports/{self.sport}/odds"
        
        params = {
            'apiKey': self.api_key,
            'regions': self.region,
            'markets': self.market,
            'bookmakers': self.bookmaker,
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        try:
            print(f"Fetching Pinnacle MLB odds...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"Successfully fetched {len(data)} games from Pinnacle")
            
            return {
                'success': True,
                'data': data,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'pinnacle_odds_api'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Pinnacle odds: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def normalize_pinnacle_data(self, raw_data: Dict) -> List[Dict]:
        """Convert Pinnacle API response to normalized schema"""
        if not raw_data.get('success'):
            return []
        
        normalized_games = []
        
        for game in raw_data.get('data', []):
            try:
                # Extract basic game info
                game_id = f"pinnacle_{game.get('id')}"
                home_team = game.get('home_team')
                away_team = game.get('away_team')
                game_time = game.get('commence_time')
                
                # Find Pinnacle bookmaker data
                pinnacle_data = None
                for bookmaker in game.get('bookmakers', []):
                    if bookmaker.get('key') == 'pinnacle':
                        pinnacle_data = bookmaker
                        break
                
                if not pinnacle_data:
                    print(f"No Pinnacle data found for game: {home_team} vs {away_team}")
                    continue
                
                # Extract moneyline odds
                h2h_market = None
                for market in pinnacle_data.get('markets', []):
                    if market.get('key') == 'h2h':
                        h2h_market = market
                        break
                
                if not h2h_market or len(h2h_market.get('outcomes', [])) < 2:
                    print(f"No valid moneyline market for: {home_team} vs {away_team}")
                    continue
                
                # Map outcomes to home/away
                home_odds = None
                away_odds = None
                
                for outcome in h2h_market['outcomes']:
                    team_name = outcome.get('name')
                    american_odds = outcome.get('price')
                    
                    if team_name == home_team:
                        home_odds = self._create_odds_object(american_odds)
                    elif team_name == away_team:
                        away_odds = self._create_odds_object(american_odds)
                
                if not home_odds or not away_odds:
                    print(f"Missing odds for game: {home_team} vs {away_team}")
                    continue
                
                # Create normalized game object
                normalized_game = {
                    "game_id": game_id,
                    "game_date": game_time[:10] if game_time else None,
                    "game_time": game_time,
                    "sport": "MLB",
                    "home_team": self._standardize_team_name(home_team),
                    "away_team": self._standardize_team_name(away_team),
                    "source": "pinnacle",
                    "home_odds": home_odds,
                    "away_odds": away_odds,
                    "metadata": {
                        "last_updated": raw_data.get('timestamp'),
                        "bookmaker": "pinnacle",
                        "market_type": "moneyline",
                        "raw_data": game
                    }
                }
                
                normalized_games.append(normalized_game)
                
            except Exception as e:
                print(f"Error normalizing game data: {e}")
                continue
        
        print(f"Successfully normalized {len(normalized_games)} games from Pinnacle")
        return normalized_games
    
    def _create_odds_object(self, american_odds: int) -> Dict:
        """Convert American odds to full odds object"""
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
        # Simple standardization - can be enhanced with full mapping
        team_mappings = {
            "Los Angeles Angels": "LAA",
            "Houston Astros": "HOU", 
            "Oakland Athletics": "OAK",
            "Toronto Blue Jays": "TOR",
            "Atlanta Braves": "ATL",
            "Milwaukee Brewers": "MIL",
            "St. Louis Cardinals": "STL",
            "Chicago Cubs": "CHC",
            "Arizona Diamondbacks": "ARI",
            "Colorado Rockies": "COL",
            "Los Angeles Dodgers": "LAD",
            "San Diego Padres": "SD",
            "San Francisco Giants": "SF",
            "Miami Marlins": "MIA",
            "New York Mets": "NYM",
            "Philadelphia Phillies": "PHI",
            "Pittsburgh Pirates": "PIT",
            "Washington Nationals": "WSH",
            "Chicago White Sox": "CWS",
            "Cleveland Guardians": "CLE",
            "Detroit Tigers": "DET",
            "Kansas City Royals": "KC",
            "Minnesota Twins": "MIN",
            "New York Yankees": "NYY",
            "Baltimore Orioles": "BAL",
            "Boston Red Sox": "BOS",
            "Tampa Bay Rays": "TB",
            "Texas Rangers": "TEX",
            "Seattle Mariners": "SEA"
        }
        
        return team_mappings.get(team_name, team_name)

# Test function for development
def test_pinnacle_client():
    """Test the Pinnacle client functionality"""
    try:
        client = PinnacleClient("keys/odds_api_key.txt")
        
        # Fetch raw odds data
        raw_data = client.get_mlb_odds()
        print("\n=== RAW DATA SAMPLE ===")
        print(json.dumps(raw_data, indent=2)[:500] + "...")
        
        # Normalize the data
        normalized_games = client.normalize_pinnacle_data(raw_data)
        print(f"\n=== NORMALIZED GAMES: {len(normalized_games)} ===")
        
        if normalized_games:
            print(json.dumps(normalized_games[0], indent=2))
        
        return normalized_games
        
    except Exception as e:
        print(f"Test failed: {e}")
        return []

if __name__ == "__main__":
    test_pinnacle_client()