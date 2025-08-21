from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json

# Initialize connection
oauth = OAuth2(None, None, from_file='jsons/oauth2.json')

def make_api_call(endpoint):
    """Make a direct Yahoo Fantasy API call"""
    base_url = "https://fantasysports.yahooapis.com/fantasy/v2/"
    url = f"{base_url}{endpoint}"
    
    try:
        response = oauth.session.get(url, params={"format": "json"})
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def check_2010_league_details():
    """Re-examine the 2010 league for any predecessor hints"""
    print("=== RE-EXAMINING 2010 LEAGUE FOR PREDECESSORS ===")
    
    league_key = "249.l.40919"
    league_data = make_api_call(f"league/{league_key}")
    
    if league_data and 'fantasy_content' in league_data:
        league_info = league_data['fantasy_content']['league'][0]
        print(f"2010 League detailed info:")
        
        # Look at all fields for any clues
        for key, value in league_info.items():
            print(f"  {key}: {value}")
        
        # Check if there are any manager history clues
        try:
            league = yahoo_fantasy_api.league.League(oauth, league_key)
            teams = league.teams()
            print(f"\n2010 Teams info:")
            for team_key, team_data in list(teams.items())[:3]:  # First 3 teams
                print(f"Team {team_key}:")
                if 'previous_season_team_rank' in team_data:
                    print(f"  Previous season rank: {team_data['previous_season_team_rank']}")
                for key, value in team_data.items():
                    if 'previous' in key.lower() or 'history' in key.lower():
                        print(f"  {key}: {value}")
        except Exception as e:
            print(f"Error getting team details: {e}")

def test_pre_2010_game_codes():
    """Test Yahoo NBA game codes before 2010"""
    print("\n=== TESTING PRE-2010 GAME CODES ===")
    
    # Yahoo NBA game codes before 2010 (educated guesses based on patterns)
    pre_2010_codes = {
        2009: 238,  # Estimated
        2008: 231,  # Estimated 
        2007: 223,  # Estimated
        2006: 215,  # Estimated
        2005: 206,  # Estimated
        2004: 196,  # Estimated
        2003: 185,  # Estimated
        2002: 175,  # Estimated
        2001: 164,  # Estimated
        2000: 153,  # Estimated
    }
    
    # Test with our known league ID and related IDs
    base_league_ids = ["40919", "40720", "42210"]  # IDs from our chain
    
    found_leagues = {}
    
    for year, game_code in pre_2010_codes.items():
        print(f"\nTesting {year} (game code {game_code}):")
        
        for league_id in base_league_ids:
            league_key = f"{game_code}.l.{league_id}"
            print(f"  Trying: {league_key}")
            
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                try:
                    league_info = league_data['fantasy_content']['league'][0]
                    name = league_info.get('name', 'Unknown')
                    season = league_info.get('season', 'Unknown')
                    print(f"    FOUND: {name} (Season: {season})")
                    
                    found_leagues[year] = {
                        'league_key': league_key,
                        'name': name,
                        'season': season,
                        'game_code': game_code
                    }
                    break  # Found one for this year, move to next
                except Exception as e:
                    print(f"    Error parsing: {e}")
            else:
                print(f"    Not found")
    
    return found_leagues

def test_early_yahoo_fantasy():
    """Test very early Yahoo Fantasy periods"""
    print("\n=== TESTING EARLY YAHOO FANTASY PERIODS ===")
    
    # Yahoo Fantasy started around 1999-2000, but NBA API might be later
    very_early_codes = range(100, 250, 10)  # Test various codes
    
    # Try a few different league ID patterns
    test_league_ids = ["40919", "1", "100", "1000"]
    
    for game_code in very_early_codes:
        for league_id in test_league_ids:
            league_key = f"{game_code}.l.{league_id}"
            
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                try:
                    league_info = league_data['fantasy_content']['league'][0]
                    name = league_info.get('name', 'Unknown')
                    season = league_info.get('season', 'Unknown')
                    print(f"EARLY FIND: {league_key} - {name} (Season: {season})")
                except:
                    pass

def check_user_games_history():
    """Check if user has access to earlier games"""
    print("\n=== CHECKING USER'S COMPLETE GAME HISTORY ===")
    
    try:
        # Get ALL games for the user, not just NBA
        user_data = make_api_call("users;use_login=1/games")
        
        if user_data and 'fantasy_content' in user_data:
            print("Found complete user game history...")
            
            users = user_data['fantasy_content']['users']
            if '0' in users and 'user' in users['0']:
                user_info = users['0']['user']
                if len(user_info) > 1 and 'games' in user_info[1]:
                    games = user_info[1]['games']
                    
                    print(f"Total games found: {games.get('count', 'Unknown')}")
                    
                    for game_id, game_data in games.items():
                        if game_id == 'count':
                            continue
                            
                        if 'game' in game_data:
                            game_info = game_data['game'][0]
                            season = game_info.get('season', 'Unknown')
                            game_key = game_info.get('game_key', 'Unknown')
                            code = game_info.get('code', 'Unknown')
                            
                            # Look for NBA games before 2010
                            if code == 'nba' and season.isdigit() and int(season) < 2010:
                                print(f"PRE-2010 NBA GAME FOUND: Season {season}, Game Key: {game_key}")
                                
                                # Try to get leagues for this game
                                if 'leagues' in game_data['game'][1]:
                                    leagues = game_data['game'][1]['leagues']
                                    for league_id, league_data in leagues.items():
                                        if league_id != 'count' and 'league' in league_data:
                                            league_info = league_data['league']
                                            league_key = league_info.get('league_key', 'Unknown')
                                            league_name = league_info.get('name', 'Unknown')
                                            print(f"  League: {league_name} ({league_key})")
        
    except Exception as e:
        print(f"Error checking user history: {e}")

# Main execution
print("SEARCHING FOR PRE-2010 DATA")
print("="*50)

# Step 1: Re-examine 2010 league for clues
check_2010_league_details()

# Step 2: Test pre-2010 game codes systematically
pre_2010_leagues = test_pre_2010_game_codes()

# Step 3: Test very early Yahoo Fantasy
test_early_yahoo_fantasy()

# Step 4: Check user's complete game history
check_user_games_history()

# Summary
print("\n" + "="*50)
print("PRE-2010 SEARCH RESULTS:")
print("="*50)

if pre_2010_leagues:
    for year in sorted(pre_2010_leagues.keys(), reverse=True):
        league = pre_2010_leagues[year]
        print(f"FOUND {year}: {league.get('name', 'Unknown')} ({league.get('league_key', 'Unknown')})")
else:
    print("No pre-2010 leagues found")
    print("\nThis suggests 2010 (249.l.40919) is likely the first year of this league.")

print(f"\nConclusion: 2010 appears to be the starting point for 'The Best Time of Year' league.")