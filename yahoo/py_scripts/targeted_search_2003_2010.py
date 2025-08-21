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

def get_current_manager_info():
    """Get manager info from current leagues to help identify them in older leagues"""
    print("=== GETTING CURRENT MANAGER INFO FOR REFERENCE ===")
    
    current_leagues = ["402.l.121244", "454.l.44006"]  # 2020 and 2024
    all_managers = {}
    
    for league_key in current_leagues:
        try:
            league = yahoo_fantasy_api.league.League(oauth, league_key)
            teams = league.teams()
            
            print(f"\nManagers in {league_key}:")
            for team_key, team_data in teams.items():
                team_name = team_data.get('name', 'Unknown')
                if 'managers' in team_data:
                    for manager_info in team_data['managers']:
                        manager_data = manager_info.get('manager', {})
                        email = manager_data.get('email', '')
                        nickname = manager_data.get('nickname', '')
                        
                        print(f"  {team_name}: {nickname} ({email})")
                        
                        if email:
                            all_managers[email] = {
                                'nickname': nickname,
                                'team_name': team_name,
                                'league': league_key
                            }
                            
        except Exception as e:
            print(f"Error getting managers from {league_key}: {e}")
    
    return all_managers

def check_specific_league_patterns():
    """Check specific league ID patterns that might contain our league"""
    print(f"\n=== CHECKING SPECIFIC LEAGUE PATTERNS ===")
    
    game_codes = {
        2009: 238, 2008: 231, 2007: 223, 2006: 215, 
        2005: 206, 2004: 196, 2003: 185
    }
    
    # Test specific league ID patterns that might be related
    # Based on our known IDs: 40919, 40720, 42210, 98368, 121244, 124782
    test_patterns = [
        # Around the 40000 range
        range(40000, 45000, 100),
        # Around the 98000 range  
        range(95000, 102000, 100),
        # Around the 121000 range
        range(118000, 125000, 100),
        # Sequential patterns from known IDs
        [40919 - i for i in range(1, 20)],  # Before 40919
        [40719, 40819, 40919, 41019, 41119],  # Around 40919
    ]
    
    found_leagues = {}
    
    for year, game_code in game_codes.items():
        print(f"\n--- Testing {year} (Code: {game_code}) ---")
        
        leagues_tested = 0
        max_tests = 50  # Limit tests per year
        
        for pattern in test_patterns:
            for league_id in pattern:
                if leagues_tested >= max_tests:
                    break
                    
                league_key = f"{game_code}.l.{league_id}"
                leagues_tested += 1
                
                try:
                    league_data = make_api_call(f"league/{league_key}")
                    if league_data and 'fantasy_content' in league_data:
                        league_info = league_data['fantasy_content']['league'][0]
                        name = league_info.get('name', '')
                        league_type = league_info.get('league_type', '')
                        num_teams = league_info.get('num_teams', 0)
                        
                        # Look for promising candidates
                        if (league_type == 'private' and 
                            num_teams == 10 and 
                            ('best time' in name.lower() or 
                             'time of year' in name.lower() or
                             name == 'The Best Time of Year')):
                            
                            print(f"  PROMISING: {league_key} - '{name}' ({num_teams} teams)")
                            
                            # Try to get team info to check for Bzznatch
                            try:
                                league = yahoo_fantasy_api.league.League(oauth, league_key)
                                teams = league.teams()
                                team_names = [team_data.get('name', '') for team_data in teams.values()]
                                
                                print(f"    Team names: {team_names[:5]}...")
                                
                                # Check for Bzznatch or similar
                                bzznatch_found = any('bzz' in team_name.lower() or 'natch' in team_name.lower() 
                                                   for team_name in team_names)
                                
                                if bzznatch_found:
                                    print(f"    *** BZZNATCH PATTERN FOUND! ***")
                                    
                                found_leagues[year] = {
                                    'league_key': league_key,
                                    'name': name,
                                    'team_names': team_names,
                                    'bzznatch_found': bzznatch_found
                                }
                                
                            except Exception as e:
                                print(f"    Could not get teams: {e}")
                                
                except Exception as e:
                    pass  # Skip errors
            
            if leagues_tested >= max_tests:
                break
        
        print(f"  Tested {leagues_tested} leagues")
    
    return found_leagues

def check_user_league_history():
    """Check user's complete league history for any missed leagues"""
    print(f"\n=== CHECKING USER'S COMPLETE HISTORY ===")
    
    try:
        # Get all NBA games for user
        user_data = make_api_call("users;use_login=1/games;game_codes=nba")
        
        if user_data and 'fantasy_content' in user_data:
            users = user_data['fantasy_content']['users']
            if '0' in users and 'user' in users['0']:
                user_info = users['0']['user']
                if len(user_info) > 1 and 'games' in user_info[1]:
                    games = user_info[1]['games']
                    
                    pre_2010_leagues = []
                    
                    for game_id, game_data in games.items():
                        if game_id == 'count':
                            continue
                            
                        if 'game' in game_data:
                            game_info = game_data['game'][0]
                            season = game_info.get('season', '')
                            
                            if season.isdigit() and int(season) < 2010:
                                print(f"Found pre-2010 game: Season {season}")
                                
                                if 'leagues' in game_data['game'][1]:
                                    leagues = game_data['game'][1]['leagues']
                                    for league_id, league_data in leagues.items():
                                        if league_id != 'count' and 'league' in league_data:
                                            league_info = league_data['league']
                                            league_key = league_info.get('league_key', '')
                                            league_name = league_info.get('name', '')
                                            
                                            pre_2010_leagues.append({
                                                'season': season,
                                                'league_key': league_key,
                                                'name': league_name
                                            })
                                            
                                            print(f"  {season}: {league_name} ({league_key})")
                    
                    return pre_2010_leagues
        
    except Exception as e:
        print(f"Error checking user history: {e}")
    
    return []

# Main execution
print("TARGETED SEARCH FOR 2003-2010 LEAGUES")
print("="*50)

# Get current manager info for reference
managers = get_current_manager_info()

# Check specific patterns that might contain our leagues  
pattern_matches = check_specific_league_patterns()

# Check user's complete history
user_history = check_user_league_history()

# Summary
print(f"\n" + "="*50)
print("TARGETED SEARCH RESULTS:")
print("="*50)

print(f"\n1. CURRENT MANAGERS (for reference):")
for email, info in managers.items():
    print(f"  {info['nickname']} ({email}) - {info['team_name']}")

print(f"\n2. PATTERN-BASED MATCHES:")
if pattern_matches:
    for year in sorted(pattern_matches.keys(), reverse=True):
        league = pattern_matches[year]
        bzz_status = "✓ BZZNATCH FOUND" if league.get('bzznatch_found') else ""
        print(f"  {year}: {league['name']} ({league['league_key']}) {bzz_status}")
        if league.get('team_names'):
            print(f"       Teams: {', '.join(league['team_names'][:3])}...")
else:
    print("  No pattern matches found")

print(f"\n3. USER HISTORY MATCHES:")
if user_history:
    for league in user_history:
        print(f"  {league['season']}: {league['name']} ({league['league_key']})")
else:
    print("  No historical leagues found in user data")

# Final recommendation
all_found = len(pattern_matches) + len(user_history)
if all_found > 0:
    print(f"\n🎯 RECOMMENDATION:")
    print(f"Test these {all_found} league keys to see if they contain your pre-2010 data:")
    
    all_leagues = {}
    all_leagues.update({f"pattern_{k}": v for k, v in pattern_matches.items()})
    for i, league in enumerate(user_history):
        all_leagues[f"history_{i}"] = league
    
    for key, league in all_leagues.items():
        league_key = league.get('league_key', '')
        name = league.get('name', '')
        season = league.get('season', key.split('_')[1])
        print(f"  {season}: {league_key} ('{name}')")
        
else:
    print(f"\n❌ CONCLUSION:")
    print(f"No additional leagues found for 2003-2010.")
    print(f"Your complete dataset likely remains: 2010-2024 (15 seasons)")
    print(f"The league may have truly started in 2010, or the earlier leagues")
    print(f"may not be accessible through the current API.")