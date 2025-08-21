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
            print(f"API call failed: {response.status_code} for {endpoint}")
            return None
    except Exception as e:
        print(f"Exception in API call: {e}")
        return None

def comprehensive_user_history_check():
    """Most comprehensive check of user's complete history"""
    print("=== COMPREHENSIVE USER HISTORY CHECK ===")
    
    # Try different ways to get user history
    endpoints_to_try = [
        "users;use_login=1/games",  # All games
        "users;use_login=1/games;game_codes=nba",  # NBA only
        "users;use_login=1",  # Basic user info
    ]
    
    all_leagues_found = []
    
    for endpoint in endpoints_to_try:
        print(f"\nTrying endpoint: {endpoint}")
        
        user_data = make_api_call(endpoint)
        if user_data:
            print("  Got user data, parsing...")
            
            try:
                # Navigate the nested structure
                fantasy_content = user_data.get('fantasy_content', {})
                users = fantasy_content.get('users', {})
                
                if '0' in users:
                    user_info = users['0'].get('user', [])
                    
                    # Find the games section
                    games_data = None
                    for section in user_info:
                        if isinstance(section, dict) and 'games' in section:
                            games_data = section['games']
                            break
                    
                    if games_data:
                        print(f"  Found games data with {games_data.get('count', 'unknown')} games")
                        
                        for game_key, game_info in games_data.items():
                            if game_key == 'count':
                                continue
                            
                            if isinstance(game_info, dict) and 'game' in game_info:
                                game_details = game_info['game']
                                if isinstance(game_details, list) and len(game_details) >= 2:
                                    game_meta = game_details[0]
                                    game_leagues = game_details[1]
                                    
                                    season = game_meta.get('season', '')
                                    game_code = game_meta.get('code', '')
                                    
                                    if game_code == 'nba':
                                        print(f"    Found NBA season: {season}")
                                        
                                        if 'leagues' in game_leagues:
                                            leagues = game_leagues['leagues']
                                            for league_key, league_info in leagues.items():
                                                if league_key == 'count':
                                                    continue
                                                
                                                if isinstance(league_info, dict) and 'league' in league_info:
                                                    league_data = league_info['league']
                                                    league_name = league_data.get('name', '')
                                                    full_league_key = league_data.get('league_key', '')
                                                    
                                                    all_leagues_found.append({
                                                        'season': season,
                                                        'league_key': full_league_key,
                                                        'name': league_name,
                                                        'source': endpoint
                                                    })
                                                    
                                                    print(f"      League: {league_name} ({full_league_key})")
                    else:
                        print("  No games data found")
                        
            except Exception as e:
                print(f"  Error parsing user data: {e}")
        else:
            print("  No data returned")
    
    return all_leagues_found

def check_all_known_bzznatch_variations():
    """Check for variations of Bzznatch team name in recent leagues"""
    print(f"\n=== CHECKING BZZNATCH VARIATIONS IN KNOWN LEAGUES ===")
    
    known_leagues = [
        "402.l.121244",  # 2020
        "395.l.98368",   # 2019  
        "385.l.42210",   # 2018
        "375.l.111279"   # 2017
    ]
    
    bzznatch_variations = []
    
    for league_key in known_leagues:
        print(f"\nChecking {league_key}:")
        try:
            league = yahoo_fantasy_api.league.League(oauth, league_key)
            teams = league.teams()
            
            for team_key, team_data in teams.items():
                team_name = team_data.get('name', '')
                print(f"  {team_name}")
                
                if 'bzz' in team_name.lower() or 'natch' in team_name.lower():
                    print(f"    ^ BZZNATCH VARIATION FOUND!")
                    bzznatch_variations.append({
                        'league': league_key,
                        'team_name': team_name,
                        'team_key': team_key
                    })
        except Exception as e:
            print(f"  Error: {e}")
    
    return bzznatch_variations

def test_specific_pre_2010_league_ids():
    """Test very specific league IDs that might be related"""
    print(f"\n=== TESTING SPECIFIC PRE-2010 LEAGUE IDS ===")
    
    game_codes = {2009: 238, 2008: 231, 2007: 223, 2006: 215, 2005: 206, 2004: 196, 2003: 185}
    
    # Very targeted IDs based on patterns from our known chain
    specific_ids = [
        # Sequential from our known 40919
        40918, 40917, 40916, 40915,
        # Other patterns from our chain
        98368, 98367, 98366, 98365,
        42210, 42209, 42208, 42207,
        121244, 121243, 121242, 121241,
        # Common early league IDs
        1, 2, 3, 4, 5, 10, 100, 1000
    ]
    
    found = []
    
    for year, game_code in game_codes.items():
        print(f"\nTesting {year} (code {game_code}):")
        
        for league_id in specific_ids:
            league_key = f"{game_code}.l.{league_id}"
            
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                try:
                    league_info = league_data['fantasy_content']['league'][0]
                    name = league_info.get('name', '')
                    league_type = league_info.get('league_type', '')
                    num_teams = league_info.get('num_teams', 0)
                    
                    if league_type == 'private' and num_teams == 10:
                        print(f"  PRIVATE 10-TEAM: {league_key} - '{name}'")
                        found.append({
                            'year': year,
                            'league_key': league_key,
                            'name': name
                        })
                        
                except Exception as e:
                    pass
    
    return found

# Main execution  
print("FINAL COMPREHENSIVE SEARCH FOR PRE-2010 DATA")
print("="*60)

# Method 1: Comprehensive user history
print("Method 1: User History Analysis")
user_leagues = comprehensive_user_history_check()

# Method 2: Check Bzznatch variations in known leagues
print("Method 2: Bzznatch Pattern Analysis") 
bzznatch_info = check_all_known_bzznatch_variations()

# Method 3: Test very specific league IDs
print("Method 3: Specific League ID Testing")
specific_leagues = test_specific_pre_2010_league_ids()

# Final Analysis
print(f"\n" + "="*60)
print("FINAL COMPREHENSIVE RESULTS:")
print("="*60)

print(f"\n1. USER HISTORY LEAGUES:")
if user_leagues:
    # Group by season
    by_season = {}
    for league in user_leagues:
        season = league['season']
        if season not in by_season:
            by_season[season] = []
        by_season[season].append(league)
    
    for season in sorted(by_season.keys()):
        print(f"\n  Season {season}:")
        for league in by_season[season]:
            print(f"    {league['name']} ({league['league_key']})")
else:
    print("  No leagues found in user history")

print(f"\n2. BZZNATCH TEAM VARIATIONS FOUND:")
if bzznatch_info:
    for var in bzznatch_variations:
        print(f"  {var['league']}: '{var['team_name']}'")
else:
    print("  No Bzznatch variations found")

print(f"\n3. SPECIFIC ID TEST RESULTS:")  
if specific_leagues:
    for league in specific_leagues:
        print(f"  {league['year']}: {league['name']} ({league['league_key']})")
else:
    print("  No specific leagues found")

# Final conclusion
total_found = len(user_leagues) + len(specific_leagues)
pre_2010_leagues = [l for l in user_leagues + specific_leagues if l.get('season', l.get('year', '2020')) < '2010']

print(f"\n" + "="*60)
print("CONCLUSION:")
print("="*60)

if pre_2010_leagues:
    print(f"SUCCESS: Found {len(pre_2010_leagues)} potential pre-2010 leagues!")
    print("These leagues should be tested for draft data:")
    for league in pre_2010_leagues:
        season = league.get('season', league.get('year', 'Unknown'))
        print(f"  {season}: {league['league_key']} ('{league['name']}')")
else:
    print("No pre-2010 leagues found.")
    print("Your complete dataset appears to be: 2010-2024 (15 seasons)")
    print("This could mean:")
    print("  1. The league truly started in 2010")
    print("  2. Pre-2010 leagues used different Yahoo accounts")  
    print("  3. Pre-2010 leagues are no longer accessible via API")
    print("  4. Pre-2010 leagues had different league names")

print(f"\nTotal leagues discovered: {total_found}")
print(f"Confirmed dataset: 2010-2024 (15 consecutive seasons)")