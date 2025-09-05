import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

from market_data.base import DataProvider
from config.constants import Sport, Provider, PROVIDER_SPORT_MAPPING, BetType
from models import Game, Odds

class OddsAPIClient(DataProvider):
    """Implementation for The Odds API provider"""
    
    def __init__(self):
        super().__init__(Provider.ODDS_API.value)
        
        # Import here to avoid circular imports
        from config.settings import ODDS_API_KEY
        
        self.api_key = ODDS_API_KEY
        self.base_url = "https://api.the-odds-api.com/v4"
        
        if not self.api_key:
            raise ValueError("ODDS_API_KEY is required. Please add it to config/odds_api_key.txt or set as environment variable")
    
    def fetch_games(self, sport: str, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch games from The Odds API"""
        try:
            sport_enum = Sport(sport)
        except ValueError:
            raise ValueError(f"Unsupported sport: {sport}")
        
        sport_key = PROVIDER_SPORT_MAPPING[Provider.ODDS_API][sport_enum]
        
        params = {
            'api_key': self.api_key,
            'regions': 'us,us2,eu,uk,au',  # Include more regions for more sportsbooks
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american',
            'bookmakers': 'draftkings,fanduel,betmgm,caesars,williamhill_us,bovada,betrivers,betonlineag,betus,mybookieag,lowvig,pointsbetus,twinspires,circasports,barstool,wynnbet,superbook,unibet_us,betway,betfred,betparx,sugarhouse,foxbet,tipico_us,sisportsbook,intertops,betfair_ex_us,pinnacle'
        }
        
        if date:
            # Add date filtering if supported by API
            pass
        
        try:
            response = requests.get(
                f"{self.base_url}/sports/{sport_key}/odds",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Fetched {len(data)} games from Odds API")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching from Odds API: {e}")
            raise
    
    def parse_games(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse Odds API response"""
        if not isinstance(raw_data, list):
            self.logger.error("Expected list of games from Odds API")
            return []
        
        parsed_games = []
        
        for game in raw_data:
            try:
                parsed_game = {
                    'id': game['id'],
                    'home_team': game['home_team'],
                    'away_team': game['away_team'],
                    'commence_time': game['commence_time'],
                    'sport_key': game.get('sport_key'),
                    'bookmakers': game.get('bookmakers', [])
                }
                parsed_games.append(parsed_game)
                
            except KeyError as e:
                self.logger.warning(f"Missing required field in game data: {e}")
                continue
        
        self.logger.info(f"Parsed {len(parsed_games)} games")
        return parsed_games
    
    def normalize_games(self, parsed_data: List[Dict[str, Any]]) -> List[Game]:
        """Normalize to common Game format"""
        normalized_games = []
        
        for game_data in parsed_data:
            try:
                # Determine sport from sport_key
                sport = self._map_sport_key(game_data.get('sport_key', ''))
                
                game = Game(
                    game_id=f"odds_api_{game_data['id']}",
                    sport=sport,
                    home_team=self._normalize_team_name(game_data['home_team']),
                    away_team=self._normalize_team_name(game_data['away_team']),
                    start_time=self._parse_datetime(game_data['commence_time']),
                    provider_ids={Provider.ODDS_API: game_data['id']}
                )
                
                # Process odds from bookmakers
                for bookmaker in game_data.get('bookmakers', []):
                    odds_list = self._extract_odds(bookmaker, game_data)
                    for odds in odds_list:
                        if odds:
                            odds_key = f"{Provider.ODDS_API.value}_{bookmaker['key']}_{odds.bet_type.value}"
                            game.add_odds(odds_key, odds)
                
                normalized_games.append(game)
                
            except Exception as e:
                self.logger.warning(f"Error normalizing game {game_data.get('id')}: {e}")
                continue
        
        self.logger.info(f"Normalized {len(normalized_games)} games")
        return normalized_games
    
    def _map_sport_key(self, sport_key: str) -> Sport:
        """Map Odds API sport key to our Sport enum"""
        mapping = {
            'americanfootball_nfl': Sport.NFL,
            'basketball_nba': Sport.NBA,
            'baseball_mlb': Sport.MLB,
            'icehockey_nhl': Sport.NHL
        }
        return mapping.get(sport_key, Sport.NFL)  # Default to NFL
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to common format"""
        # Basic team name normalization
        team_mapping = {
            # NFL teams
            'Kansas City Chiefs': 'KC',
            'Buffalo Bills': 'BUF',
            'Cincinnati Bengals': 'CIN',
            'Pittsburgh Steelers': 'PIT',
            'Cleveland Browns': 'CLE',
            'Baltimore Ravens': 'BAL',
            'Houston Texans': 'HOU',
            'Indianapolis Colts': 'IND',
            'Jacksonville Jaguars': 'JAX',
            'Tennessee Titans': 'TEN',
            'Denver Broncos': 'DEN',
            'Las Vegas Raiders': 'LV',
            'Los Angeles Chargers': 'LAC',
            'New England Patriots': 'NE',
            'New York Jets': 'NYJ',
            'Miami Dolphins': 'MIA',
            # Add more as needed
        }
        
        # Try exact match first
        if team_name in team_mapping:
            return team_mapping[team_name]
        
        # Try partial matching for different variations
        for full_name, abbrev in team_mapping.items():
            if team_name in full_name or full_name in team_name:
                return abbrev
        
        # If no mapping found, return original name
        return team_name
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string from Odds API"""
        try:
            # Odds API returns ISO format with 'Z' suffix
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            # Fallback parsing
            return datetime.now()
    
    def _extract_odds(self, bookmaker: Dict, game_data: Dict) -> List[Odds]:
        """Extract odds from bookmaker data"""
        odds_list = []
        
        try:
            bookmaker_key = bookmaker['key']
            markets = bookmaker.get('markets', [])
            
            for market in markets:
                market_key = market['key']
                outcomes = market.get('outcomes', [])
                
                if market_key == 'h2h':  # Moneyline
                    odds = self._create_moneyline_odds(outcomes, bookmaker_key, game_data)
                    if odds:
                        odds_list.append(odds)
                        
                elif market_key == 'spreads':  # Point spread
                    odds = self._create_spread_odds(outcomes, bookmaker_key)
                    if odds:
                        odds_list.append(odds)
                        
                elif market_key == 'totals':  # Over/Under
                    odds = self._create_total_odds(outcomes, bookmaker_key)
                    if odds:
                        odds_list.append(odds)
                        
        except Exception as e:
            self.logger.warning(f"Error extracting odds from {bookmaker.get('key', 'unknown')}: {e}")
        
        return odds_list
    
    def _create_moneyline_odds(self, outcomes: List[Dict], bookmaker_key: str, game_data: Dict) -> Optional[Odds]:
        """Create moneyline odds from outcomes"""
        home_ml = None
        away_ml = None
        home_team = game_data.get('home_team', '')
        away_team = game_data.get('away_team', '')
        
        for outcome in outcomes:
            name = outcome.get('name', '')
            price = outcome.get('price')
            
            if price is None:
                continue
            
            # Convert to American odds if needed
            if isinstance(price, float) and price >= 1:
                # Assume decimal odds, convert to American
                american_odds = self._decimal_to_american(price)
            else:
                american_odds = int(price)
            
            # Match by team name (more reliable than position)
            if name == home_team:
                home_ml = american_odds
            elif name == away_team:
                away_ml = american_odds
        
        if home_ml is not None and away_ml is not None:
            return Odds(
                provider=Provider.ODDS_API,
                bet_type=BetType.MONEYLINE,
                timestamp=datetime.now(),
                home_ml=home_ml,
                away_ml=away_ml,
                bookmaker=bookmaker_key
            )
        
        return None
    
    def _create_spread_odds(self, outcomes: List[Dict], bookmaker_key: str) -> Optional[Odds]:
        """Create spread odds from outcomes"""
        spread_line = None
        home_spread_odds = None
        away_spread_odds = None
        
        for outcome in outcomes:
            price = outcome.get('price')
            point = outcome.get('point')
            
            if price is None or point is None:
                continue
            
            american_odds = self._decimal_to_american(price) if isinstance(price, float) else int(price)
            
            if spread_line is None:
                spread_line = float(point)
            
            # Determine home/away by point value (positive = home favored)
            if float(point) > 0:
                home_spread_odds = american_odds
            else:
                away_spread_odds = american_odds
        
        if spread_line is not None and home_spread_odds is not None and away_spread_odds is not None:
            return Odds(
                provider=Provider.ODDS_API,
                bet_type=BetType.SPREAD,
                timestamp=datetime.now(),
                spread_line=spread_line,
                home_spread_odds=home_spread_odds,
                away_spread_odds=away_spread_odds,
                bookmaker=bookmaker_key
            )
        
        return None
    
    def _create_total_odds(self, outcomes: List[Dict], bookmaker_key: str) -> Optional[Odds]:
        """Create total (over/under) odds from outcomes"""
        total_line = None
        over_odds = None
        under_odds = None
        
        for outcome in outcomes:
            name = outcome.get('name', '').lower()
            price = outcome.get('price')
            point = outcome.get('point')
            
            if price is None or point is None:
                continue
            
            american_odds = self._decimal_to_american(price) if isinstance(price, float) else int(price)
            
            if total_line is None:
                total_line = float(point)
            
            if 'over' in name:
                over_odds = american_odds
            elif 'under' in name:
                under_odds = american_odds
        
        if total_line is not None and over_odds is not None and under_odds is not None:
            return Odds(
                provider=Provider.ODDS_API,
                bet_type=BetType.TOTAL,
                timestamp=datetime.now(),
                total_line=total_line,
                over_odds=over_odds,
                under_odds=under_odds,
                bookmaker=bookmaker_key
            )
        
        return None
    
    def _decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def get_available_sports(self) -> List[str]:
        """Get list of available sports from Odds API"""
        try:
            response = requests.get(
                f"{self.base_url}/sports",
                params={'apiKey': self.api_key},
                timeout=30
            )
            response.raise_for_status()
            
            sports = response.json()
            return [sport['key'] for sport in sports if sport.get('active', False)]
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching available sports: {e}")
            return []