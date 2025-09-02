"""
Simple Pinnacle Sports Betting Client
Clean interface for getting games with odds data
"""

import requests
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import pandas as pd
import pytz

class PinnacleClient:
    """Simple client for fetching Pinnacle odds data"""
    
    def __init__(self, api_key_file: Optional[str] = None):
        """Initialize with API key"""
        if api_key_file and os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                content = f.read().strip()
        else:
            # Try default location
            default_key = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'keys', 'odds_api_key.txt')
            if os.path.exists(default_key):
                with open(default_key, 'r') as f:
                    content = f.read().strip()
            else:
                raise ValueError("API key file not found")
        
        # Extract key from file (handle different formats)
        if "'" in content:
            # Format: api_key = 'key_here'
            self.api_key = content.split("'")[1]
        elif '"' in content:
            # Format: api_key = "key_here"
            self.api_key = content.split('"')[1]
        else:
            # Format: just the key
            self.api_key = content
        
        self.base_url = "https://api.the-odds-api.com/v4"
        
        # League mappings
        self.league_map = {
            'mlb': 'baseball_mlb',
            'nfl': 'americanfootball_nfl', 
            'nba': 'basketball_nba',
            'nhl': 'icehockey_nhl',
            'ncaaf': 'americanfootball_ncaaf',
            'ncaab': 'basketball_ncaab'
        }
    
    def get_games(self, league: str = 'mlb', remove_live_games: bool = True) -> List[Dict]:
        """
        Get all games for a league
        
        Args:
            league: League name ('mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaab')
            remove_live_games: If True, filter out games that have started
            
        Returns:
            List of game dictionaries with standardized format
        """
        if league not in self.league_map:
            raise ValueError(f"Unsupported league: {league}. Available: {list(self.league_map.keys())}")
        
        sport_key = self.league_map[league]
        
        # Fetch data from OddsAPI
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            'api_key': self.api_key,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american',
            'bookmakers': 'pinnacle'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            games = []
            current_time = datetime.now(timezone.utc)
            
            for game in data:
                # Parse game time with better error handling
                try:
                    game_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
                except:
                    print(f"Warning: Could not parse game time for {game.get('home_team', 'Unknown')} vs {game.get('away_team', 'Unknown')}")
                    continue
                
                # Filter live/past games if requested with buffer
                time_buffer = timedelta(minutes=15)  # 15 minute buffer
                if remove_live_games and game_time <= (current_time + time_buffer):
                    print(f"Filtered past/live game: {game['away_team']} @ {game['home_team']} at {game_time}")
                    continue
                
                # Extract Pinnacle odds
                pinnacle_odds = None
                for bookmaker in game.get('bookmakers', []):
                    if bookmaker['key'] == 'pinnacle':
                        for market in bookmaker.get('markets', []):
                            if market['key'] == 'h2h':
                                pinnacle_odds = market['outcomes']
                                break
                        break
                
                if not pinnacle_odds or len(pinnacle_odds) != 2:
                    continue
                
                # Standardize format
                home_team = game['home_team']
                away_team = game['away_team']
                
                # Find home and away odds
                home_odds = None
                away_odds = None
                for outcome in pinnacle_odds:
                    if outcome['name'] == home_team:
                        home_odds = outcome['price']
                    elif outcome['name'] == away_team:
                        away_odds = outcome['price']
                
                if home_odds is None or away_odds is None:
                    continue
                
                # Determine favorite and dog
                if home_odds < away_odds:
                    favorite_team = self._normalize_team_name(home_team)
                    favorite_odds = home_odds
                    dog_team = self._normalize_team_name(away_team)
                    dog_odds = away_odds
                else:
                    favorite_team = self._normalize_team_name(away_team)
                    favorite_odds = away_odds
                    dog_team = self._normalize_team_name(home_team)
                    dog_odds = home_odds

                games.append({
                    'league': league.upper(),
                    'favorite': favorite_team,
                    'dog': dog_team,
                    'fav_odds': favorite_odds,
                    'dog_odds': dog_odds,
                    'game_time': game_time.astimezone(pytz.timezone('US/Central')).strftime('%Y-%m-%d %H:%M CST'),
                    'game_date': game_time.strftime('%Y-%m-%d'),
                    'source': 'pinnacle',
                    'raw_commence_time': game['commence_time'],
                    'parsed_game_time': game_time.isoformat()
                })
            
            return games
            
        except Exception as e:
            print(f"Error fetching Pinnacle data: {e}")
            return []
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to common abbreviations"""
        team_map = {
            # MLB
            'Arizona Diamondbacks': 'ARI',
            'Atlanta Braves': 'ATL', 
            'Baltimore Orioles': 'BAL',
            'Boston Red Sox': 'BOS',
            'Chicago White Sox': 'CWS',
            'Chicago Cubs': 'CHC',
            'Cincinnati Reds': 'CIN',
            'Cleveland Guardians': 'CLE',
            'Colorado Rockies': 'COL',
            'Detroit Tigers': 'DET',
            'Houston Astros': 'HOU',
            'Kansas City Royals': 'KC',
            'Los Angeles Angels': 'LAA',
            'Los Angeles Dodgers': 'LAD',
            'Miami Marlins': 'MIA',
            'Milwaukee Brewers': 'MIL',
            'Minnesota Twins': 'MIN',
            'New York Yankees': 'NYY',
            'New York Mets': 'NYM',
            'Oakland Athletics': 'OAK',
            'Philadelphia Phillies': 'PHI',
            'Pittsburgh Pirates': 'PIT',
            'San Diego Padres': 'SD',
            'San Francisco Giants': 'SF',
            'Seattle Mariners': 'SEA',
            'St Louis Cardinals': 'STL',
            'Tampa Bay Rays': 'TB',
            'Texas Rangers': 'TEX',
            'Toronto Blue Jays': 'TOR',
            'Washington Nationals': 'WSH',
            
            # NFL
            'Arizona Cardinals': 'ARI',
            'Atlanta Falcons': 'ATL',
            'Baltimore Ravens': 'BAL',
            'Buffalo Bills': 'BUF',
            'Carolina Panthers': 'CAR',
            'Chicago Bears': 'CHI',
            'Cincinnati Bengals': 'CIN',
            'Cleveland Browns': 'CLE',
            'Dallas Cowboys': 'DAL',
            'Denver Broncos': 'DEN',
            'Detroit Lions': 'DET',
            'Green Bay Packers': 'GB',
            'Houston Texans': 'HOU',
            'Indianapolis Colts': 'IND',
            'Jacksonville Jaguars': 'JAX',
            'Kansas City Chiefs': 'KC',
            'Las Vegas Raiders': 'LV',
            'Los Angeles Chargers': 'LAC',
            'Los Angeles Rams': 'LAR',
            'Miami Dolphins': 'MIA',
            'Minnesota Vikings': 'MIN',
            'New England Patriots': 'NE',
            'New Orleans Saints': 'NO',
            'New York Giants': 'NYG',
            'New York Jets': 'NYJ',
            'Philadelphia Eagles': 'PHI',
            'Pittsburgh Steelers': 'PIT',
            'San Francisco 49ers': 'SF',
            'Seattle Seahawks': 'SEA',
            'Tampa Bay Buccaneers': 'TB',
            'Tennessee Titans': 'TEN',
            'Washington Commanders': 'WAS',
            
            # NCAAF - College Football Teams  
            'Ohio Bobcats': 'Ohio',
            'Rutgers Scarlet Knights': 'Rutgers',
            'Boise State Broncos': 'Boise St.',
            'South Florida Bulls': 'South Florida', 
            'Wyoming Cowboys': 'Wyoming',
            'Akron Zips': 'Akron',
            'East Carolina Pirates': 'East Carolina',
            'NC State Wolfpack': 'North Carolina St.',
            'UCF Knights': 'UCF',
            'Jacksonville State Gamecocks': 'Jacksonville St.',
            
            # Additional NCAAF Teams for 2025-08-30 matches
            'Purdue Boilermakers': 'Purdue',
            'Ball State Cardinals': 'Ball St.',
            'Ohio State Buckeyes': 'Ohio St.',
            'Texas Longhorns': 'TEX',
            'Tennessee Volunteers': 'TEN', 
            'Syracuse Orange': 'Syracuse',
            'Kentucky Wildcats': 'Kentucky',
            'Toledo Rockets': 'Toledo',
            'Indiana Hoosiers': 'Indiana',
            'Old Dominion Monarchs': 'Old Dominion',
            'Alabama Crimson Tide': 'Alabama',
            'Florida State Seminoles': 'Florida St.',
            'Temple Owls': 'Temple',
            'UMass Minutemen': 'UMass',
            'Virginia Cavaliers': 'Virginia',
            'Coastal Carolina Chanticleers': 'Coastal Carolina',
            'Clemson Tigers': 'Clemson',
            'LSU Tigers': 'LSU',
            'Utah State Aggies': 'Utah St.',
            'UTEP Miners': 'UTEP',
            'Georgia Tech Yellow Jackets': 'Georgia Tech',
            'Colorado Buffaloes': 'COL',
            'Auburn Tigers': 'Auburn',
            'Baylor Bears': 'Baylor',
            'UNLV Rebels': 'UNLV',
            'Sam Houston State Bearkats': 'Sam Houston',
            'San Jose State Spartans': 'San Jose St.',
            'Central Michigan Chippewas': 'Central Michigan',
            'Maryland Terrapins': 'Maryland',
            'Florida Atlantic Owls': 'Florida Atlantic',
            'Mississippi State Bulldogs': 'Mississippi St.',
            'Southern Mississippi Golden Eagles': 'Southern Miss',
            'Tulane Green Wave': 'Tulane',
            'Northwestern Wildcats': 'Northwestern',
            
            # Comprehensive NCAAF team mappings for all dates
            'Notre Dame Fighting Irish': 'Notre Dame',
            'Miami Hurricanes': 'Miami (FL)',
            'South Carolina Gamecocks': 'South Carolina',
            'Virginia Tech Hokies': 'Virginia Tech',
            'Texas State Bobcats': 'Texas St.',
            'Eastern Michigan Eagles': 'Eastern Michigan',
            'Louisiana Ragin Cajuns': 'Louisiana',
            'Rice Owls': 'Rice',
            'Texas A&M Aggies': 'Texas A&M',
            'UTSA Roadrunners': 'UTSA',
            'Georgia Southern Eagles': 'Georgia Southern',
            'Fresno State Bulldogs': 'Fresno St.',
            'Arizona Wildcats': 'ARI',
            'Hawaii Rainbow Warriors': 'Hawai\'i',
            'Oregon State Beavers': 'Oregon St.',
            'California Golden Bears': 'California',
            'Washington Huskies': 'WAS',
            'Colorado State Rams': 'Colorado St.',
            'Utah Utes': 'Utah',
            'UCLA Bruins': 'UCLA',
            'Michigan Wolverines': 'Michigan',
            'Michigan State Spartans': 'Michigan St.',
            'Western Michigan Broncos': 'Western Michigan',
            'Wisconsin Badgers': 'Wisconsin',
            'Miami (OH) RedHawks': 'Miami (OH)',
            'Minnesota Golden Gophers': 'MIN',
            'Buffalo Bulls': 'BUF',
            'Wake Forest Demon Deacons': 'Wake Forest',
            'Kennesaw State Owls': 'Kennesaw St.',
            'Nebraska Cornhuskers': 'Nebraska',
            'Cincinnati Bearcats': 'CIN',
            'Appalachian State Mountaineers': 'Appalachian St.',
            'Charlotte 49ers': 'Charlotte'
        }
        
        return team_map.get(team_name, team_name)
    
    def print_games_table(self, games: List[Dict]):
        """Print games in a clean table format"""
        if not games:
            print("No games found")
            return
        
        df = pd.DataFrame(games)
        
        # Sort by date first, then by dog odds (highest to lowest)
        df = df.sort_values(['game_date', 'dog_odds'], ascending=[True, False])
        
        df = df[['league', 'game_date', 'favorite', 'dog', 'fav_odds', 'dog_odds', 'game_time']]
        df.columns = ['League', 'Date', 'Favorite', 'Dog', 'Fav Odds', 'Dog Odds', 'Game Time']
        
        print(f"\nPINNACLE GAMES ({len(games)} found) - Sorted by Dog Odds")
        print("=" * 85)
        print(df.to_string(index=False))
        print()

if __name__ == "__main__":
    # Test the client
    client = PinnacleClient()
    
    for league in ['ncaaf']:
        print(f"\nTesting {league.upper()}...")
        games = client.get_games(league=league, remove_live_games=True)
        client.print_games_table(games)