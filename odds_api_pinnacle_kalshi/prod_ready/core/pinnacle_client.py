"""
Pinnacle API Client for Sports Moneyline Odds via OddsAPI
Supports MLB, NFL, NBA, NHL, and college sports
"""

import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.timestamp_utils import simplify_timestamp, simplify_date, parse_game_time_safe, format_display_time
from config.sports_config import get_sport_config, get_available_sports

class PinnacleClient:
    
    # Dynamic sport mapping using sports_config
    @staticmethod
    def _get_sport_map() -> Dict[str, str]:
        """Get sport mapping from sports configuration"""
        sport_map = {}
        for sport_key, config in [(k, get_sport_config(k)) for k in get_available_sports()]:
            if config and config.pinnacle_key:
                sport_map[sport_key] = config.pinnacle_key
        return sport_map
    
    def __init__(self, api_key_file: str):
        """Initialize Pinnacle client with OddsAPI key"""
        self.base_url = "https://api.the-odds-api.com/v4"
        self.api_key = self._load_api_key(api_key_file)
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
    
    def get_sports_odds(self, sport_type: str = 'mlb') -> Dict:
        """Fetch moneyline odds for specified sport from Pinnacle via OddsAPI"""
        sport_map = self._get_sport_map()
        if sport_type not in sport_map:
            return {
                'success': False,
                'error': f'Unsupported sport: {sport_type}. Supported: {", ".join(sport_map.keys())}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        odds_api_sport = sport_map[sport_type]
        url = f"{self.base_url}/sports/{odds_api_sport}/odds"
        
        params = {
            'apiKey': self.api_key,
            'regions': self.region,
            'markets': self.market,
            'bookmakers': self.bookmaker,
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        try:
            print(f"Fetching Pinnacle {sport_type.upper()} odds...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"Successfully fetched {len(data)} {sport_type.upper()} games from Pinnacle")
            
            return {
                'success': True,
                'data': data,
                'sport_type': sport_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'pinnacle_odds_api'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Pinnacle {sport_type} odds: {e}")
            return {
                'success': False,
                'error': str(e),
                'sport_type': sport_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_mlb_odds(self) -> Dict:
        """Legacy method - fetch MLB odds"""
        return self.get_sports_odds('mlb')
    
    def get_easy_data_view(self, sport_type: str = 'mlb', limit: int = 20) -> Dict:
        """Easy-to-read view of Pinnacle sports odds data"""
        print(f"Fetching easy data view for Pinnacle {sport_type.upper()} odds...")
        
        # Get odds data
        odds_data = self.get_sports_odds(sport_type)
        
        if not odds_data.get('success'):
            return odds_data
        
        games = odds_data.get('data', [])
        easy_view = []
        
        for game in games[:limit]:
            home_team = game.get('home_team', 'N/A')
            away_team = game.get('away_team', 'N/A')
            commence_time = game.get('commence_time', 'N/A')
            
            # Extract Pinnacle odds
            pinnacle_odds = None
            for bookmaker in game.get('bookmakers', []):
                if bookmaker.get('key') == 'pinnacle':
                    pinnacle_odds = bookmaker
                    break
            
            if pinnacle_odds:
                markets = pinnacle_odds.get('markets', [])
                h2h_market = next((m for m in markets if m.get('key') == 'h2h'), {})
                outcomes = h2h_market.get('outcomes', [])
                
                home_odds = 'N/A'
                away_odds = 'N/A'
                
                for outcome in outcomes:
                    if outcome.get('name') == home_team:
                        home_odds = outcome.get('price', 'N/A')
                    elif outcome.get('name') == away_team:
                        away_odds = outcome.get('price', 'N/A')
            else:
                home_odds = 'No Pinnacle odds'
                away_odds = 'No Pinnacle odds'
            
            easy_view.append({
                'game': f"{away_team} @ {home_team}",
                'sport': sport_type.upper(),
                'home_odds': home_odds,
                'away_odds': away_odds,
                'game_time': simplify_timestamp(commence_time),
                'game_time_display': format_display_time(commence_time),
                'bookmaker': 'Pinnacle'
            })
        
        return {
            'success': True,
            'data': easy_view,
            'total_found': len(games),
            'showing': len(easy_view),
            'sport': sport_type.upper(),
            'timestamp': odds_data.get('timestamp')
        }
    
    def normalize_pinnacle_data(self, raw_data: Dict, min_time_buffer_minutes: int = 15) -> List[Dict]:
        """Convert Pinnacle API response to normalized schema, filtering out live games"""
        if not raw_data.get('success'):
            return []
        
        sport_type = raw_data.get('sport_type', 'unknown').upper()
        normalized_games = []
        now = datetime.now(timezone.utc)
        live_games_filtered = 0
        
        for game in raw_data.get('data', []):
            try:
                # Extract basic game info
                game_id = f"pinnacle_{game.get('id')}"
                home_team = game.get('home_team')
                away_team = game.get('away_team')
                game_time = game.get('commence_time')
                
                # Skip games that have already started or are starting soon
                if not self._is_future_game(game_time, min_time_buffer_minutes):
                    live_games_filtered += 1
                    continue
                
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
                
                # Create normalized game object with simplified timestamps
                normalized_game = {
                    "game_id": game_id,
                    "game_date": simplify_date(game_time),
                    "game_time": simplify_timestamp(game_time),
                    "game_time_display": format_display_time(game_time),
                    "sport": sport_type,
                    "home_team": self._standardize_team_name(home_team, sport_type.lower()),
                    "away_team": self._standardize_team_name(away_team, sport_type.lower()),
                    "source": "pinnacle",
                    "home_odds": home_odds,
                    "away_odds": away_odds,
                    "metadata": {
                        "last_updated": raw_data.get('timestamp'),
                        "bookmaker": "pinnacle",
                        "market_type": "moneyline",
                        "raw_data": game,
                        "original_game_time": game_time
                    }
                }
                
                normalized_games.append(normalized_game)
                
            except Exception as e:
                print(f"Error normalizing game data: {e}")
                continue
        
        if live_games_filtered > 0:
            print(f"Filtered out {live_games_filtered} live/starting games from Pinnacle")
        print(f"Successfully normalized {len(normalized_games)} future games from Pinnacle")
        return normalized_games
    
    def _is_future_game(self, game_time_str: str, min_buffer_minutes: int = 15) -> bool:
        """Check if game is in the future with minimum buffer using safe parsing"""
        return parse_game_time_safe(game_time_str, min_buffer_minutes)
    
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
    
    def _standardize_team_name(self, team_name: str, sport: str = 'unknown') -> str:
        """Standardize team names for consistent matching across all sports"""
        team_name = team_name.strip()
        
        # MLB team mappings
        mlb_mappings = {
            "Los Angeles Angels": "LAA", "Angels": "LAA",
            "Houston Astros": "HOU", "Astros": "HOU",
            "Oakland Athletics": "OAK", "Athletics": "OAK", "A's": "OAK",
            "Toronto Blue Jays": "TOR", "Blue Jays": "TOR",
            "Atlanta Braves": "ATL", "Braves": "ATL",
            "Milwaukee Brewers": "MIL", "Brewers": "MIL",
            "St. Louis Cardinals": "STL", "Cardinals": "STL",
            "Chicago Cubs": "CHC", "Cubs": "CHC",
            "Arizona Diamondbacks": "ARI", "Diamondbacks": "ARI",
            "Colorado Rockies": "COL", "Rockies": "COL",
            "Los Angeles Dodgers": "LAD", "Dodgers": "LAD",
            "San Diego Padres": "SD", "Padres": "SD",
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
        
        # NFL team mappings  
        nfl_mappings = {
            "Arizona Cardinals": "ARI", "Cardinals": "ARI",
            "Atlanta Falcons": "ATL", "Falcons": "ATL",
            "Baltimore Ravens": "BAL", "Ravens": "BAL",
            "Buffalo Bills": "BUF", "Bills": "BUF",
            "Carolina Panthers": "CAR", "Panthers": "CAR",
            "Chicago Bears": "CHI", "Bears": "CHI",
            "Cincinnati Bengals": "CIN", "Bengals": "CIN",
            "Cleveland Browns": "CLE", "Browns": "CLE",
            "Dallas Cowboys": "DAL", "Cowboys": "DAL",
            "Denver Broncos": "DEN", "Broncos": "DEN",
            "Detroit Lions": "DET", "Lions": "DET",
            "Green Bay Packers": "GB", "Packers": "GB",
            "Houston Texans": "HOU", "Texans": "HOU",
            "Indianapolis Colts": "IND", "Colts": "IND",
            "Jacksonville Jaguars": "JAX", "Jaguars": "JAX",
            "Kansas City Chiefs": "KC", "Chiefs": "KC",
            "Las Vegas Raiders": "LV", "Raiders": "LV",
            "Los Angeles Chargers": "LAC", "Chargers": "LAC",
            "Los Angeles Rams": "LAR", "Rams": "LAR",
            "Miami Dolphins": "MIA", "Dolphins": "MIA",
            "Minnesota Vikings": "MIN", "Vikings": "MIN",
            "New England Patriots": "NE", "Patriots": "NE",
            "New Orleans Saints": "NO", "Saints": "NO",
            "New York Giants": "NYG", "Giants": "NYG",
            "New York Jets": "NYJ", "Jets": "NYJ",
            "Philadelphia Eagles": "PHI", "Eagles": "PHI",
            "Pittsburgh Steelers": "PIT", "Steelers": "PIT",
            "San Francisco 49ers": "SF", "49ers": "SF",
            "Seattle Seahawks": "SEA", "Seahawks": "SEA",
            "Tampa Bay Buccaneers": "TB", "Buccaneers": "TB",
            "Tennessee Titans": "TEN", "Titans": "TEN",
            "Washington Commanders": "WAS", "Commanders": "WAS"
        }
        
        # Select appropriate mapping based on sport
        if sport == 'mlb':
            return mlb_mappings.get(team_name, team_name)
        elif sport == 'nfl':
            return nfl_mappings.get(team_name, team_name)
        else:
            # Try all mappings if sport unknown
            for mapping in [mlb_mappings, nfl_mappings]:
                if team_name in mapping:
                    return mapping[team_name]
            return team_name

# Test function for development
def test_pinnacle_client():
    """Test the Pinnacle client functionality"""
    try:
        client = PinnacleClient("../keys/odds_api_key.txt")
        
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