"""
Combined Kalshi-Pinnacle Client
Shows each game's odds from both platforms side by side
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pinnacle.client import PinnacleClient
from kalshi.client import KalshiClient
from typing import List, Dict
import pandas as pd

class CombinedClient:
    """Combined client showing Kalshi and Pinnacle odds side by side"""
    
    def __init__(self):
        """Initialize both clients"""
        self.pinnacle = PinnacleClient()
        self.kalshi = KalshiClient()
    
    def get_combined_games(self, league='mlb', remove_live_games=True) -> List[Dict]:
        """
        Get games from both platforms and match them up
        
        Args:
            league: League name ('mlb', 'nfl', 'nba', 'nhl')
            remove_live_games: Filter out live/started games
            
        Returns:
            List of combined game data with Kalshi and Pinnacle odds
        """
        print(f"Fetching {league.upper()} games from both platforms...")
        
        # Get games from both platforms
        pinnacle_games = self.pinnacle.get_games(league=league, remove_live_games=remove_live_games)
        kalshi_games = self.kalshi.get_games(league=league, remove_live_games=remove_live_games)
        
        print(f"Found {len(pinnacle_games)} Pinnacle games, {len(kalshi_games)} Kalshi games")
        
        # Match games by teams
        combined_games = self._match_games(pinnacle_games, kalshi_games)
        
        return combined_games
    
    def _match_games(self, pinnacle_games: List[Dict], kalshi_games: List[Dict]) -> List[Dict]:
        """Match games between both platforms by team names AND dates with strict date enforcement"""
        combined = []
        all_games = {}
        
        # Add Pinnacle games
        for game in pinnacle_games:
            teams_key = self._create_teams_key(game['favorite'], game['dog'])
            date_key = game['game_date']
            full_key = f"{teams_key}_{date_key}"
            
            if full_key not in all_games:
                all_games[full_key] = {
                    'favorite': game['favorite'],
                    'dog': game['dog'],
                    'game_date': game['game_date'],
                    'league': game['league'],
                    'pinnacle': game,
                    'kalshi': None
                }
        
        # Try to match Kalshi games with strict date matching
        for kalshi_game in kalshi_games:
            kalshi_teams_key = self._create_teams_key(kalshi_game['favorite'], kalshi_game['dog'])
            kalshi_date_key = kalshi_game['game_date']
            kalshi_full_key = f"{kalshi_teams_key}_{kalshi_date_key}"
            
            matched = False
            
            # Try direct match first (same teams, same date)
            if kalshi_full_key in all_games:
                all_games[kalshi_full_key]['kalshi'] = kalshi_game
                matched = True
            else:
                # Try reverse match (fav/dog swapped, same date)
                reverse_teams_key = self._create_teams_key(kalshi_game['dog'], kalshi_game['favorite'])
                reverse_full_key = f"{reverse_teams_key}_{kalshi_date_key}"
                
                if reverse_full_key in all_games:
                    all_games[reverse_full_key]['kalshi'] = kalshi_game
                    matched = True
                else:
                    # Try fuzzy date matching ONLY within ±1 day
                    from datetime import datetime, timedelta
                    try:
                        kalshi_date = datetime.strptime(kalshi_date_key, '%Y-%m-%d')
                        for delta_days in [-1, 1]:  # Check 1 day before and after
                            check_date = (kalshi_date + timedelta(days=delta_days)).strftime('%Y-%m-%d')
                            check_key = f"{kalshi_teams_key}_{check_date}"
                            reverse_check_key = f"{reverse_teams_key}_{check_date}"
                            
                            if check_key in all_games:
                                all_games[check_key]['kalshi'] = kalshi_game
                                matched = True
                                break
                            elif reverse_check_key in all_games:
                                all_games[reverse_check_key]['kalshi'] = kalshi_game
                                matched = True
                                break
                    except:
                        pass
            
            # If no match found, add as Kalshi-only game
            if not matched:
                all_games[kalshi_full_key] = {
                    'favorite': kalshi_game['favorite'],
                    'dog': kalshi_game['dog'],
                    'game_date': kalshi_game['game_date'],
                    'league': kalshi_game['league'],
                    'pinnacle': None,
                    'kalshi': kalshi_game
                }
        
        # Convert to list and sort
        for full_key, game_data in all_games.items():
            # Determine the best dog odds from available sources
            dog_odds = 0
            if game_data['pinnacle']:
                dog_odds = max(dog_odds, game_data['pinnacle']['dog_odds'])
            if game_data['kalshi']:
                kalshi_dog = game_data['kalshi']['dog_odds']
                if kalshi_dog < 1000:  # Filter out the extreme odds from conversion issues
                    dog_odds = max(dog_odds, kalshi_dog)
            
            game_data['best_dog_odds'] = dog_odds
            combined.append(game_data)
        
        # Sort by date first, then by best dog odds within each date
        combined.sort(key=lambda x: (x['game_date'], -x['best_dog_odds']))
        
        return combined
    
    def _create_teams_key(self, team1: str, team2: str) -> str:
        """Create a consistent key for team matching using normalized team names"""
        # Normalize team names using the same logic as individual clients
        norm_team1 = self._normalize_team_name(team1.strip())
        norm_team2 = self._normalize_team_name(team2.strip())
        teams = sorted([norm_team1, norm_team2])
        return f"{teams[0]}_{teams[1]}"
    
    def _normalize_team_name(self, team_name: str) -> str:
        """Normalize team names to consistent format - uses same logic as individual clients"""
        # Use the same NCAAF mappings as in the individual clients
        team_map = {
            # From both Pinnacle and Kalshi normalizations
            'Ohio Bobcats': 'Ohio', 'Ohio': 'Ohio',
            'Rutgers Scarlet Knights': 'Rutgers', 'Rutgers': 'Rutgers',
            'Boise State Broncos': 'Boise St.', 'Boise State': 'Boise St.', 'Boise St.': 'Boise St.',
            'South Florida Bulls': 'South Florida', 'South Florida': 'South Florida',
            'Wyoming Cowboys': 'Wyoming', 'Wyoming': 'Wyoming',
            'Akron Zips': 'Akron', 'Akron': 'Akron',
            'East Carolina Pirates': 'East Carolina', 'East Carolina': 'East Carolina',
            'NC State Wolfpack': 'North Carolina St.', 'North Carolina St.': 'North Carolina St.',
            'UCF Knights': 'UCF', 'UCF': 'UCF',
            'Jacksonville State Gamecocks': 'Jacksonville St.', 'Jacksonville State': 'Jacksonville St.', 'Jacksonville St.': 'Jacksonville St.',
            
            # Additional comprehensive mappings
            'Purdue Boilermakers': 'Purdue', 'Purdue': 'Purdue',
            'Ball State Cardinals': 'Ball St.', 'Ball St.': 'Ball St.',
            'Ohio State Buckeyes': 'Ohio St.', 'Ohio St.': 'Ohio St.',
            'Texas Longhorns': 'TEX', 'TEX': 'TEX',
            'Tennessee Volunteers': 'TEN', 'TEN': 'TEN',
            'Syracuse Orange': 'Syracuse', 'Syracuse': 'Syracuse',
            'Kentucky Wildcats': 'Kentucky', 'Kentucky': 'Kentucky',
            'Toledo Rockets': 'Toledo', 'Toledo': 'Toledo',
            'Indiana Hoosiers': 'Indiana', 'Indiana': 'Indiana',
            'Old Dominion Monarchs': 'Old Dominion', 'Old Dominion': 'Old Dominion',
            'Alabama Crimson Tide': 'Alabama', 'Alabama': 'Alabama',
            'Florida State Seminoles': 'Florida St.', 'Florida St.': 'Florida St.',
            'Temple Owls': 'Temple', 'Temple': 'Temple',
            'UMass Minutemen': 'UMass', 'UMass': 'UMass',
            'Virginia Cavaliers': 'Virginia', 'Virginia': 'Virginia',
            'Coastal Carolina Chanticleers': 'Coastal Carolina', 'Coastal Carolina': 'Coastal Carolina',
            'Clemson Tigers': 'Clemson', 'Clemson': 'Clemson',
            'LSU Tigers': 'LSU', 'LSU': 'LSU',
            'Utah State Aggies': 'Utah St.', 'Utah St.': 'Utah St.',
            'UTEP Miners': 'UTEP', 'UTEP': 'UTEP',
            'Georgia Tech Yellow Jackets': 'Georgia Tech', 'Georgia Tech': 'Georgia Tech',
            'Colorado Buffaloes': 'COL', 'COL': 'COL',
            'Auburn Tigers': 'Auburn', 'Auburn': 'Auburn',
            'Baylor Bears': 'Baylor', 'Baylor': 'Baylor',
            'UNLV Rebels': 'UNLV', 'UNLV': 'UNLV',
            'Sam Houston State Bearkats': 'Sam Houston', 'Sam Houston': 'Sam Houston',
            'San Jose State Spartans': 'San Jose St.', 'San Jose St.': 'San Jose St.',
            'Central Michigan Chippewas': 'Central Michigan', 'Central Michigan': 'Central Michigan',
            'Maryland Terrapins': 'Maryland', 'Maryland': 'Maryland',
            'Florida Atlantic Owls': 'Florida Atlantic', 'Florida Atlantic': 'Florida Atlantic',
            'Mississippi State Bulldogs': 'Mississippi St.', 'Mississippi St.': 'Mississippi St.',
            'Southern Mississippi Golden Eagles': 'Southern Miss', 'Southern Miss': 'Southern Miss',
            'Tulane Green Wave': 'Tulane', 'Tulane': 'Tulane',
            'Northwestern Wildcats': 'Northwestern', 'Northwestern': 'Northwestern',
            
            # Missing teams for Aug 31 and other dates
            'Notre Dame Fighting Irish': 'Notre Dame', 'Notre Dame': 'Notre Dame',
            'Miami Hurricanes': 'Miami (FL)', 'Miami (FL)': 'Miami (FL)',
            'South Carolina Gamecocks': 'South Carolina', 'South Carolina': 'South Carolina', 
            'Virginia Tech Hokies': 'Virginia Tech', 'Virginia Tech': 'Virginia Tech',
            
            # Additional comprehensive NCAAF mappings
            'Texas State Bobcats': 'Texas St.', 'Texas St.': 'Texas St.',
            'Eastern Michigan Eagles': 'Eastern Michigan', 'Eastern Michigan': 'Eastern Michigan',
            'Louisiana Ragin Cajuns': 'Louisiana', 'Louisiana': 'Louisiana',
            'Rice Owls': 'Rice', 'Rice': 'Rice',
            'Texas A&M Aggies': 'Texas A&M', 'Texas A&M': 'Texas A&M',
            'UTSA Roadrunners': 'UTSA', 'UTSA': 'UTSA',
            'Georgia Southern Eagles': 'Georgia Southern', 'Georgia Southern': 'Georgia Southern',
            'Fresno State Bulldogs': 'Fresno St.', 'Fresno St.': 'Fresno St.',
            'Arizona Wildcats': 'ARI', 'ARI': 'ARI',
            'Hawaii Rainbow Warriors': 'Hawai\'i', 'Hawai\'i': 'Hawai\'i',
            'Oregon State Beavers': 'Oregon St.', 'Oregon St.': 'Oregon St.',
            'California Golden Bears': 'California', 'California': 'California',
            'Washington Huskies': 'WAS', 'WAS': 'WAS',
            'Colorado State Rams': 'Colorado St.', 'Colorado St.': 'Colorado St.',
            'Utah Utes': 'Utah', 'Utah': 'Utah',
            'UCLA Bruins': 'UCLA', 'UCLA': 'UCLA',
            
            # More comprehensive coverage for other potential matches
            'Michigan Wolverines': 'Michigan', 'Michigan': 'Michigan',
            'Michigan State Spartans': 'Michigan St.', 'Michigan St.': 'Michigan St.',
            'Western Michigan Broncos': 'Western Michigan', 'Western Michigan': 'Western Michigan',
            'Wisconsin Badgers': 'Wisconsin', 'Wisconsin': 'Wisconsin',
            'Miami (OH) RedHawks': 'Miami (OH)', 'Miami (OH)': 'Miami (OH)',
            'Minnesota Golden Gophers': 'MIN', 'MIN': 'MIN',
            'Buffalo Bulls': 'BUF', 'BUF': 'BUF',
            'Wake Forest Demon Deacons': 'Wake Forest', 'Wake Forest': 'Wake Forest',
            'Kennesaw State Owls': 'Kennesaw St.', 'Kennesaw St.': 'Kennesaw St.',
            'Nebraska Cornhuskers': 'Nebraska', 'Nebraska': 'Nebraska',
            'Cincinnati Bearcats': 'CIN', 'CIN': 'CIN',
            'Appalachian State Mountaineers': 'Appalachian St.', 'Appalachian St.': 'Appalachian St.',
            'Charlotte 49ers': 'Charlotte', 'Charlotte': 'Charlotte',
            
            # Additional NCAAF mappings for current games
            'Arkansas Razorbacks': 'Arkansas', 'Arkansas': 'Arkansas',
            'Arkansas State Red Wolves': 'Arkansas St.', 'Arkansas St.': 'Arkansas St.',
            'Oklahoma State Cowboys': 'Oklahoma St.', 'Oklahoma St.': 'Oklahoma St.',
            'Oklahoma Sooners': 'Oklahoma', 'Oklahoma': 'Oklahoma',
            'Oregon Ducks': 'Oregon', 'Oregon': 'Oregon',
            'Georgia Tech Yellow Jackets': 'Georgia Tech', 'Georgia Tech': 'Georgia Tech',
            'Gardner-Webb Bulldogs': 'Gardner-Webb', 'Gardner-Webb': 'Gardner-Webb',
            'North Carolina A&T Aggies': 'North Carolina A&T', 'North Carolina A&T': 'North Carolina A&T',
            'UCF Knights': 'UCF', 'UCF': 'UCF',
            'Colorado Buffaloes': 'COL', 'COL': 'COL',
            'Delaware Blue Hens': 'Delaware', 'Delaware': 'Delaware',
            'Minnesota Golden Gophers': 'MIN', 'MIN': 'MIN',
            'Northwestern State Demons': 'Northwestern St.', 'Northwestern St.': 'Northwestern St.',
            'Central Michigan Chippewas': 'Central Michigan', 'Central Michigan': 'Central Michigan',
            'Pittsburgh Panthers': 'PIT', 'PIT': 'PIT',
            'California Golden Bears': 'California', 'California': 'California',
            'Texas Southern Tigers': 'Texas Southern', 'Texas Southern': 'Texas Southern',
            'Appalachian State Mountaineers': 'Appalachian St.', 'Appalachian St.': 'Appalachian St.',
            'Lindenwood Lions': 'Lindenwood', 'Lindenwood': 'Lindenwood',
            'Navy Midshipmen': 'Navy', 'Navy': 'Navy',
            'UAB Blazers': 'UAB', 'UAB': 'UAB',
            'Bowling Green Falcons': 'Bowling Green', 'Bowling Green': 'Bowling Green',
            'Cincinnati Bearcats': 'CIN', 'CIN': 'CIN',
            'Wake Forest Demon Deacons': 'Wake Forest', 'Wake Forest': 'Wake Forest',
            'Western Carolina Catamounts': 'Western Carolina', 'Western Carolina': 'Western Carolina',
            'BYU Cougars': 'BYU', 'BYU': 'BYU',
            'Stanford Cardinal': 'Stanford', 'Stanford': 'Stanford',
            'Purdue Boilermakers': 'Purdue', 'Purdue': 'Purdue',
            'Southern Illinois Salukis': 'Southern Illinois', 'Southern Illinois': 'Southern Illinois',
            'Colorado State Rams': 'Colorado St.', 'Colorado St.': 'Colorado St.',
            'Northern Colorado Bears': 'Northern Colorado', 'Northern Colorado': 'Northern Colorado',
            'McNeese Cowboys': 'McNeese', 'McNeese': 'McNeese',
            'Louisiana Ragin\' Cajuns': 'Louisiana', 'Louisiana': 'Louisiana',
            'Army Black Knights': 'Army', 'Army': 'Army',
            'Kansas State Wildcats': 'Kansas St.', 'Kansas St.': 'Kansas St.',
            'Campbell Camels': 'Campbell', 'Campbell': 'Campbell',
            'East Carolina Pirates': 'East Carolina', 'East Carolina': 'East Carolina',
            'Florida Gators': 'Florida', 'Florida': 'Florida',
            'South Florida Bulls': 'South Florida', 'South Florida': 'South Florida',
            'Howard Bison': 'Howard', 'Howard': 'Howard',
            'Temple Owls': 'Temple', 'Temple': 'Temple',
            'Miami (OH) RedHawks': 'Miami (OH)', 'Miami (OH)': 'Miami (OH)',
            'Rutgers Scarlet Knights': 'Rutgers', 'Rutgers': 'Rutgers',
            'Buffalo Bulls': 'BUF', 'BUF': 'BUF',
            'St. Francis (PA) Red Flash': 'St. Francis (PA)', 'St. Francis (PA)': 'St. Francis (PA)',
            'Coastal Carolina Chanticleers': 'Coastal Carolina', 'Coastal Carolina': 'Coastal Carolina',
            'Charleston Southern Buccaneers': 'Charleston Southern', 'Charleston Southern': 'Charleston Southern',
            'Wisconsin Badgers': 'Wisconsin', 'Wisconsin': 'Wisconsin',
            'Middle Tennessee Blue Raiders': 'Middle Tennessee', 'Middle Tennessee': 'Middle Tennessee',
            'Houston Cougars': 'Houston', 'Houston': 'Houston',
            'Rice Owls': 'Rice', 'Rice': 'Rice',
            'Memphis Tigers': 'Memphis', 'Memphis': 'Memphis',
            'Georgia State Panthers': 'Georgia St.', 'Georgia St.': 'Georgia St.',
            'North Carolina Tar Heels': 'North Carolina', 'North Carolina': 'North Carolina',
            'Marshall Thundering Herd': 'Marshall', 'Marshall': 'Marshall',
            'Missouri State Bears': 'Missouri St.', 'Missouri St.': 'Missouri St.',
            'Tulane Green Wave': 'Tulane', 'Tulane': 'Tulane',
            'South Alabama Jaguars': 'South Alabama', 'South Alabama': 'South Alabama',
            'Ole Miss Rebels': 'Ole Miss', 'Ole Miss': 'Ole Miss',
            'Kentucky Wildcats': 'Kentucky', 'Kentucky': 'Kentucky',
            'North Texas Mean Green': 'North Texas', 'North Texas': 'North Texas',
            'Western Michigan Broncos': 'Western Michigan', 'Western Michigan': 'Western Michigan',
            'Toledo Rockets': 'Toledo', 'Toledo': 'Toledo',
            'Western Kentucky Hilltoppers': 'Western Kentucky', 'Western Kentucky': 'Western Kentucky',
            'Syracuse Orange': 'Syracuse', 'Syracuse': 'Syracuse',
            'UConn Huskies': 'UConn', 'UConn': 'UConn',
            'Liberty Flames': 'Liberty', 'Liberty': 'Liberty',
            'Jacksonville State Gamecocks': 'Jacksonville St.', 'Jacksonville St.': 'Jacksonville St.',
            'Missouri Tigers': 'Missouri', 'Missouri': 'Missouri',
            'Kansas Jayhawks': 'Kansas', 'Kansas': 'Kansas',
            'Arizona State Sun Devils': 'Arizona St.', 'Arizona St.': 'Arizona St.',
            'Mississippi State Bulldogs': 'Mississippi St.', 'Mississippi St.': 'Mississippi St.',
            'Michigan Wolverines': 'Michigan', 'Michigan': 'Michigan',
            'Michigan State Spartans': 'Michigan St.', 'Michigan St.': 'Michigan St.',
            'Boston College Eagles': 'Boston College', 'Boston College': 'Boston College',
            'UTSA Roadrunners': 'UTSA', 'UTSA': 'UTSA',
            'Texas State Bobcats': 'Texas St.', 'Texas St.': 'Texas St.',
            'West Virginia Mountaineers': 'West Virginia', 'West Virginia': 'West Virginia',
            'Ohio Bobcats': 'Ohio', 'Ohio': 'Ohio',
            'Iowa State Cyclones': 'Iowa St.', 'Iowa St.': 'Iowa St.',
            'Iowa Hawkeyes': 'Iowa', 'Iowa': 'Iowa',
            'Illinois Fighting Illini': 'Illinois', 'Illinois': 'Illinois',
            'Duke Blue Devils': 'Duke', 'Duke': 'Duke',
            'Oregon State Beavers': 'Oregon St.', 'Oregon St.': 'Oregon St.',
            'Fresno State Bulldogs': 'Fresno St.', 'Fresno St.': 'Fresno St.',
            'NC State Wolfpack': 'North Carolina St.', 'North Carolina St.': 'North Carolina St.',
            'Virginia Cavaliers': 'Virginia', 'Virginia': 'Virginia',
            'SMU Mustangs': 'SMU', 'SMU': 'SMU',
            'Baylor Bears': 'Baylor', 'Baylor': 'Baylor',
            'Virginia Tech Hokies': 'Virginia Tech', 'Virginia Tech': 'Virginia Tech',
            'Vanderbilt Commodores': 'Vanderbilt', 'Vanderbilt': 'Vanderbilt',
            'Hawaii Rainbow Warriors': 'Hawai\'i', 'Hawai\'i': 'Hawai\'i',
            'Sam Houston Bearkats': 'Sam Houston', 'Sam Houston': 'Sam Houston',
            'Tulsa Golden Hurricane': 'Tulsa', 'Tulsa': 'Tulsa',
            'New Mexico State Aggies': 'New Mexico St.', 'New Mexico St.': 'New Mexico St.',
            'UCLA Bruins': 'UCLA', 'UCLA': 'UCLA',
            'UNLV Rebels': 'UNLV', 'UNLV': 'UNLV',
            'Washington State Cougars': 'Washington St.', 'Washington St.': 'Washington St.',
            'San Diego State Aztecs': 'San Diego St.', 'San Diego St.': 'San Diego St.',
            'Maryland Terrapins': 'Maryland', 'Maryland': 'Maryland',
            'Northern Illinois Huskies': 'Northern Illinois', 'Northern Illinois': 'Northern Illinois',
            'Louisville Cardinals': 'Louisville', 'Louisville': 'Louisville',
            'James Madison Dukes': 'James Madison', 'James Madison': 'James Madison'
        }
        
        return team_map.get(team_name, team_name)
    
    def _format_game_display(self, matchup: str, pinnacle_fav: int, pinnacle_dog: int, kalshi_fav: int, kalshi_dog: int, game_date: str, pinnacle_time: str = None, kalshi_time: str = None) -> str:
        """Format a game in the same style as the main display"""
        # Extract team names from matchup
        teams = matchup.split(' vs ')
        if len(teams) != 2:
            return f"Error formatting: {matchup}"
        
        favorite, dog = teams[0], teams[1]
        
        # Calculate implied percentages
        def calc_percentage(odds):
            if odds < 0:
                return int(abs(odds) / (abs(odds) + 100) * 100)
            else:
                return int(100 / (odds + 100) * 100)
        
        pin_fav_pct = calc_percentage(pinnacle_fav)
        pin_dog_pct = calc_percentage(pinnacle_dog)
        kal_fav_pct = calc_percentage(kalshi_fav)
        kal_dog_pct = calc_percentage(kalshi_dog)
        
        # Use provided times or fall back to date
        pin_display_time = pinnacle_time if pinnacle_time else game_date
        kal_display_time = kalshi_time if kalshi_time else game_date
        
        # Format the display
        result = f"{favorite} vs {dog}\n"
        result += f"------------------------------------------------------------\n"
        result += f"Pinnacle:  {favorite:>8}  {pinnacle_fav:+4d} ({pin_fav_pct}¢)  |  {dog:<12}  {pinnacle_dog:+4d} ({pin_dog_pct}¢)  |  {pin_display_time}\n"
        result += f"Kalshi:    {favorite:>8}  {kalshi_fav:+4d} ({kal_fav_pct}¢)  |  {dog:<12}  {kalshi_dog:+4d} ({kal_dog_pct}¢)  |  {kal_display_time} (active)"
        
        return result
    
    def _odds_to_cents(self, american_odds: int) -> int:
        """Convert American odds to Kalshi cents (0-100) accounting for fees"""
        if abs(american_odds) > 2500:  # Skip extreme odds
            return 0
        
        # Convert American odds to basic probability first
        if american_odds > 0:
            basic_probability = 100 / (american_odds + 100)
        else:
            basic_probability = abs(american_odds) / (abs(american_odds) + 100)
        
        # Since we now account for fees in the cents-to-odds conversion,
        # we need to reverse-engineer what the Kalshi price would be
        # This is an approximation since the fee structure is complex
        
        # For display purposes, we can use a simplified adjustment
        # The key insight is that our calibrated conversion accounts for fees,
        # so this reverse conversion should be approximate for display only
        
        return round(basic_probability * 100)
    
    def print_combined_table(self, games: List[Dict]):
        """Print games organized by date with side-by-side format"""
        if not games:
            print("No games found")
            return
        
        print(f"\nCOMBINED ODDS COMPARISON ({len(games)} games)")
        print("=" * 120)
        
        # Group games by date
        games_by_date = {}
        for game in games:
            game_date = game['game_date']
            if game_date not in games_by_date:
                games_by_date[game_date] = []
            games_by_date[game_date].append(game)
        
        # Print each date section
        for date in sorted(games_by_date.keys()):
            date_games = games_by_date[date]
            
            print(f"\n>> {date} ({len(date_games)} games)")
            print("=" * 120)
            
            for game in date_games:
                favorite = game['favorite']
                dog = game['dog']
                
                print(f"{favorite} vs {dog}")
                print("-" * 60)
                
                # Pinnacle row
                if game['pinnacle']:
                    pin_game = game['pinnacle']
                    pin_fav_odds = pin_game['fav_odds']
                    pin_dog_odds = pin_game['dog_odds']
                    pin_time = pin_game['game_time'].split(' ')[1] if ' ' in pin_game['game_time'] else pin_game['game_time']
                    
                    # Calculate cents for Pinnacle odds
                    pin_fav_cents = self._odds_to_cents(pin_fav_odds)
                    pin_dog_cents = self._odds_to_cents(pin_dog_odds)
                    
                    print(f"Pinnacle:  {favorite:>8} {pin_fav_odds:>6} ({pin_fav_cents}¢)  |  {dog:<8} {pin_dog_odds:>6} ({pin_dog_cents}¢)  |  {pin_time}")
                else:
                    print(f"Pinnacle:  {'N/A':>8} {'N/A':>6} {'':>6}  |  {'N/A':<8} {'N/A':>6} {'':>6}  |  N/A")
                
                # Kalshi row
                if game['kalshi']:
                    kal_game = game['kalshi']
                    kal_fav_odds = kal_game['fav_odds']
                    kal_dog_odds = kal_game['dog_odds']
                    kal_time = kal_game['game_time'].split(' ')[1] if ' ' in kal_game['game_time'] else kal_game['game_time']
                    kal_status = kal_game.get('status', 'unknown')
                    
                    # Use original cents from Kalshi if available, otherwise calculate
                    kal_fav_cents = kal_game.get('fav_cents', self._odds_to_cents(kal_fav_odds))
                    kal_dog_cents = kal_game.get('dog_cents', self._odds_to_cents(kal_dog_odds))
                    
                    print(f"Kalshi:    {favorite:>8} {kal_fav_odds:>6} ({kal_fav_cents}¢)  |  {dog:<8} {kal_dog_odds:>6} ({kal_dog_cents}¢)  |  {kal_time} ({kal_status})")
                else:
                    print(f"Kalshi:    {'N/A':>8} {'N/A':>6} {'':>6}  |  {'N/A':<8} {'N/A':>6} {'':>6}  |  N/A")
                
                
                # Calculate potential edge if both available
                if game['pinnacle'] and game['kalshi']:
                    pin_fav = game['pinnacle']['fav_odds']
                    kal_fav = game['kalshi']['fav_odds']
                    
                    # Only calculate if Kalshi odds look reasonable (not the extreme -9899 values)
                    if abs(kal_fav) < 1000 and abs(pin_fav) < 1000:
                        fav_diff = abs(pin_fav - kal_fav)
                        if fav_diff > 10:  # Meaningful difference
                            print(f"Edge:      Favorite odds difference: {fav_diff} points")
                
                print()  # Blank row between games
    
    def get_summary_stats(self, games: List[Dict]) -> Dict:
        """Get summary statistics including detailed edge information"""
        stats = {
            'total_games': len(games),
            'pinnacle_only': len([g for g in games if g['pinnacle'] and not g['kalshi']]),
            'kalshi_only': len([g for g in games if g['kalshi'] and not g['pinnacle']]),
            'both_platforms': len([g for g in games if g['pinnacle'] and g['kalshi']]),
            'potential_edges': 0,
            'edge_games': [],
            'crossed_opportunities': 0,
            'crossed_games': []
        }
        
        # Find games with potential arbitrage opportunities
        for game in games:
            if game['pinnacle'] and game['kalshi']:
                pin_fav = game['pinnacle']['fav_odds']
                kal_fav = game['kalshi']['fav_odds']
                pin_dog = game['pinnacle']['dog_odds'] 
                kal_dog = game['kalshi']['dog_odds']
                
                if abs(kal_fav) < 2500 and abs(pin_fav) < 2500:  # Reasonable odds range
                    fav_diff = abs(pin_fav - kal_fav)
                    dog_diff = abs(pin_dog - kal_dog)
                    max_diff = max(fav_diff, dog_diff)
                    
                    # Only show edges where Kalshi has better odds than Pinnacle
                    kalshi_fav_better = False
                    kalshi_dog_better = False
                    edge_diff = 0
                    better_side = ""
                    edge_info = ""
                    opposite_side_close = False
                    
                    # Check if Kalshi favorite odds are better (less negative = better for favorite)
                    if fav_diff > 15 and pin_fav < kal_fav:  # Pinnacle more negative = worse for bettor
                        # Check if the opposite side odds are within 20 points
                        # Compare Pinnacle dog to Kalshi favorite (the arbitrage pair)
                        opposite_diff = abs(pin_dog - abs(kal_fav))
                        if opposite_diff <= 20:
                            kalshi_fav_better = True
                            edge_diff = fav_diff
                            better_side = f"Kalshi {game['favorite']}"
                            edge_info = f"{pin_fav:+d} vs {kal_fav:+d}"
                            opposite_side_close = True
                    
                    # Check if Kalshi dog odds are better (more positive = better for dog)
                    if dog_diff > 15 and kal_dog > pin_dog:  # Kalshi more positive = better for bettor
                        # Check if the opposite side odds are within 20 points
                        # Compare Pinnacle favorite to Kalshi dog (the arbitrage pair)
                        opposite_diff = abs(abs(pin_fav) - kal_dog)
                        if opposite_diff <= 20:
                            if not kalshi_dog_better or dog_diff > fav_diff:  # Take the bigger edge
                                kalshi_dog_better = True
                                edge_diff = dog_diff
                                better_side = f"Kalshi {game['dog']}"
                                edge_info = f"{pin_dog:+d} vs {kal_dog:+d}"
                                opposite_side_close = True
                    
                    # Only add to edge opportunities if Kalshi has better odds AND opposite side is close
                    if (kalshi_fav_better or kalshi_dog_better) and opposite_side_close:
                        
                        edge_game = {
                            'matchup': f"{game['favorite']} vs {game['dog']}",
                            'game_date': game['game_date'],
                            'edge_diff': edge_diff,
                            'better_side': better_side,
                            'edge_info': edge_info,
                            'pinnacle_fav': pin_fav,
                            'kalshi_fav': kal_fav,
                            'pinnacle_dog': pin_dog,
                            'kalshi_dog': kal_dog
                        }
                        
                        stats['edge_games'].append(edge_game)
                        stats['potential_edges'] += 1
                
                # Check for crossed opportunities (arbitrage)
                # When you can bet opposite sides on different platforms for guaranteed profit
                # This happens when: best_team_a_odds + best_team_b_odds > 0 (in American odds)
                
                # Convert to positive odds for easier calculation
                def to_positive_odds(american_odds):
                    if american_odds < 0:
                        return 100 / (abs(american_odds) / 100)
                    else:
                        return american_odds
                
                # Find best odds for each team across platforms
                fav_best_odds = max(pin_fav, kal_fav) if pin_fav < 0 and kal_fav < 0 else min(abs(pin_fav), abs(kal_fav))
                dog_best_odds = max(pin_dog, kal_dog)
                
                # For crossed opportunity, we want:
                # Team A on Platform X + Team B on Platform Y to have positive expected value
                # This is rare but possible when platforms have significantly different odds
                
                # Check all combinations
                combinations = [
                    ("Pinnacle", game['favorite'], pin_fav, "Kalshi", game['dog'], kal_dog),
                    ("Pinnacle", game['dog'], pin_dog, "Kalshi", game['favorite'], kal_fav),
                    ("Kalshi", game['favorite'], kal_fav, "Pinnacle", game['dog'], pin_dog),
                    ("Kalshi", game['dog'], kal_dog, "Pinnacle", game['favorite'], pin_fav)
                ]
                
                for plat1, team1, odds1, plat2, team2, odds2 in combinations:
                    # Convert to implied probabilities
                    if odds1 < 0:
                        prob1 = abs(odds1) / (abs(odds1) + 100)
                    else:
                        prob1 = 100 / (odds1 + 100)
                    
                    if odds2 < 0:
                        prob2 = abs(odds2) / (abs(odds2) + 100)
                    else:
                        prob2 = 100 / (odds2 + 100)
                    
                    total_implied_prob = prob1 + prob2
                    
                    # Crossed opportunity exists when total implied probability < 1 (or < 0.98 accounting for fees)
                    if total_implied_prob < 0.98:
                        profit_margin = (1 - total_implied_prob) * 100
                        
                        crossed_game = {
                            'matchup': f"{game['favorite']} vs {game['dog']}",
                            'game_date': game['game_date'],
                            'bet1': f"{plat1} {team1} {odds1:+d}",
                            'bet2': f"{plat2} {team2} {odds2:+d}",
                            'profit_margin': profit_margin,
                            'total_prob': total_implied_prob
                        }
                        
                        stats['crossed_games'].append(crossed_game)
                        stats['crossed_opportunities'] += 1
                        break  # Only count each game once
        
        # Sort games by profit margin
        stats['edge_games'].sort(key=lambda x: x['edge_diff'], reverse=True)
        stats['crossed_games'].sort(key=lambda x: x['profit_margin'], reverse=True)
        
        return stats

def view_combined_games(league='mlb', remove_live_games=True, require_both_platforms=False):
    """Main function to view combined games"""
    print(f"\n{'='*120}")
    print(f"COMBINED KALSHI-PINNACLE {league.upper()} ODDS COMPARISON")
    print(f"Remove Live Games: {remove_live_games}")
    print(f"Require Both Platforms: {require_both_platforms}")
    print(f"{'='*120}")
    
    try:
        client = CombinedClient()
        games = client.get_combined_games(league=league, remove_live_games=remove_live_games)
        
        # Filter out any games with finalized Kalshi status
        games = [game for game in games if not (game['kalshi'] and game['kalshi'].get('status') in ['finalized', 'settled', 'resolved'])]
        
        # Filter to only games with both platforms if requested
        if require_both_platforms:
            games = [game for game in games if game['pinnacle'] and game['kalshi']]
            print(f"Filtered to {len(games)} games with both platforms")
        
        client.print_combined_table(games)
        
        # Print summary
        stats = client.get_summary_stats(games)
        print(f"{'='*120}")
        print("SUMMARY:")
        print(f"Total Games: {stats['total_games']}")
        print(f"Pinnacle Only: {stats['pinnacle_only']}")
        print(f"Kalshi Only: {stats['kalshi_only']}")
        print(f"Both Platforms: {stats['both_platforms']}")
        print(f"Potential Edges: {stats['potential_edges']}")
        print(f"Crossed Opportunities: {stats['crossed_opportunities']}")
        
        # Show detailed edge information
        if stats['potential_edges'] > 0:
            print()
            print("EDGE OPPORTUNITIES:")
            print("=" * 120)
            for i, edge in enumerate(stats['edge_games'], 1):
                print(f"\n>> {i}. {edge['better_side']} - {edge['edge_diff']} point edge")
                print("=" * 120)
                formatted_display = client._format_game_display(
                    edge['matchup'], 
                    edge['pinnacle_fav'], 
                    edge['pinnacle_dog'],
                    edge['kalshi_fav'], 
                    edge['kalshi_dog'],
                    edge['game_date']
                )
                print(formatted_display)
                print()
        
        # Show crossed opportunities (arbitrage)
        if stats['crossed_opportunities'] > 0:
            print()
            print("CROSSED OPPORTUNITIES (ARBITRAGE):")
            for i, crossed in enumerate(stats['crossed_games'], 1):
                print(f"{i}. {crossed['matchup']} ({crossed['game_date']})")
                print(f"   Bet: {crossed['bet1']} AND {crossed['bet2']}")
                print(f"   Guaranteed profit: {crossed['profit_margin']:.2f}% (Total prob: {crossed['total_prob']:.3f})")
        elif stats['both_platforms'] > 0:
            print()
            print("CROSSED OPPORTUNITIES: None found (normal - these are rare)")
        
        print(f"{'='*120}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # ====== EDIT THESE VARIABLES ======
    LEAGUE = 'ncaaf'                  # 'mlb', 'nfl', 'nba', 'nhl', 'ncaaf', 'ncaab'
    REMOVE_LIVE_GAMES = True          # True = only future games, False = include live/closed
    REQUIRE_BOTH_PLATFORMS = True # True = only show games with both Kalshi and Pinnacle odds
    # ===================================
    
    view_combined_games(
        league=LEAGUE, 
        remove_live_games=REMOVE_LIVE_GAMES,
        require_both_platforms=REQUIRE_BOTH_PLATFORMS
    )