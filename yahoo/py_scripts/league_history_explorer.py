from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import requests

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

def explore_league_renewal_info():
    """Check current league's renewal information"""
    print("=== EXPLORING LEAGUE RENEWAL CHAIN ===\n")
    
    current_league = yahoo_fantasy_api.league.League(oauth, '402.l.121244')
    settings = current_league.settings()
    
    print(f"Current League: {settings.get('name', 'N/A')} (Season: {settings.get('season', 'N/A')})")
    print(f"League Key: {settings.get('league_key', 'N/A')}")
    
    # Check for renewal information
    renew_info = settings.get('renew', None)
    renewed_info = settings.get('renewed', None)
    
    print(f"Renew field: {renew_info}")
    print(f"Renewed field: {renewed_info}")
    print()
    
    return renew_info, renewed_info

def test_league_keys_by_year():
    """Test different league keys based on game/year patterns"""
    print("=== TESTING LEAGUE KEYS BY YEAR ===\n")
    
    # Yahoo NBA game codes by year (these are known patterns)
    # Format: {year}.l.{league_id}
    game_codes = {
        2024: 428,  # Current season
        2023: 418,
        2022: 414, 
        2021: 410,
        2020: 402,  # We know this works
        2019: 395,
        2018: 385,
        2017: 375,
        2016: 364,
        2015: 354,
        2014: 346,
        2013: 334,
        2012: 328,
        2011: 321,
        2010: 313
    }
    
    league_id = "121244"  # Base league ID from current league
    found_leagues = {}
    
    for year, game_code in game_codes.items():
        league_key = f"{game_code}.l.{league_id}"
        print(f"Testing {year}: {league_key}")
        
        # Try to access league
        try:
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                league_info = league_data['fantasy_content']['league'][0]
                name = league_info.get('name', 'Unknown')
                season = league_info.get('season', 'Unknown')
                print(f"  FOUND: {name} (Season: {season})")
                found_leagues[year] = {
                    'league_key': league_key,
                    'name': name,
                    'season': season,
                    'game_code': game_code
                }
            else:
                print(f"  Not found")
        except Exception as e:
            print(f"  Error: {e}")
    
    return found_leagues

def explore_user_leagues():
    """Get all leagues for the authenticated user"""
    print("\n=== EXPLORING ALL USER LEAGUES ===\n")
    
    try:
        # Get all games/leagues for the user
        user_data = make_api_call("users;use_login=1/games;game_codes=nba/leagues")
        
        if user_data and 'fantasy_content' in user_data:
            print("Found user league data...")
            
            # Parse the nested structure
            users = user_data['fantasy_content']['users']
            if '0' in users and 'user' in users['0'] and len(users['0']['user']) > 1:
                games = users['0']['user'][1].get('games', {})
                
                all_leagues = {}
                for game_id, game_data in games.items():
                    if game_id == 'count':
                        continue
                        
                    if 'game' in game_data and len(game_data['game']) > 1:
                        game_info = game_data['game'][0]
                        season = game_info.get('season', 'Unknown')
                        
                        leagues = game_data['game'][1].get('leagues', {})
                        for league_id, league_data in leagues.items():
                            if league_id == 'count':
                                continue
                                
                            if 'league' in league_data:
                                league_info = league_data['league']
                                league_key = league_info.get('league_key', 'Unknown')
                                league_name = league_info.get('name', 'Unknown')
                                
                                print(f"Season {season}: {league_name} ({league_key})")
                                all_leagues[season] = {
                                    'league_key': league_key,
                                    'name': league_name,
                                    'season': season
                                }
                
                return all_leagues
        else:
            print("No user league data found")
            return {}
            
    except Exception as e:
        print(f"Error exploring user leagues: {e}")
        return {}

def check_predecessor_leagues(renew_info):
    """Check for predecessor leagues using renew information"""
    print(f"\n=== CHECKING PREDECESSOR LEAGUES ===\n")
    
    if not renew_info:
        print("No renew information available")
        return {}
        
    # Parse renew info (format appears to be "game_code_league_id")
    try:
        parts = renew_info.split('_')
        if len(parts) >= 2:
            prev_game_code = parts[0]
            prev_league_id = parts[1]
            prev_league_key = f"{prev_game_code}.l.{prev_league_id}"
            
            print(f"Checking predecessor: {prev_league_key}")
            
            league_data = make_api_call(f"league/{prev_league_key}")
            if league_data and 'fantasy_content' in league_data:
                league_info = league_data['fantasy_content']['league'][0]
                name = league_info.get('name', 'Unknown')
                season = league_info.get('season', 'Unknown')
                print(f"  FOUND PREDECESSOR: {name} (Season: {season})")
                
                # Check if this league also has renewal info (go further back)
                renew_field = league_info.get('renew', None)
                if renew_field:
                    print(f"  This league also has renewal info: {renew_field}")
                    return {season: {'league_key': prev_league_key, 'name': name, 'season': season, 'renew': renew_field}}
                else:
                    return {season: {'league_key': prev_league_key, 'name': name, 'season': season}}
            else:
                print(f"  Predecessor not accessible")
                return {}
    except Exception as e:
        print(f"Error checking predecessor: {e}")
        return {}

# Main execution
if __name__ == "__main__":
    print("DEEP DIVE: EXPLORING LEAGUE HISTORY\n")
    
    # Step 1: Check renewal information
    renew_info, renewed_info = explore_league_renewal_info()
    
    # Step 2: Test systematic league keys
    found_by_year = test_league_keys_by_year()
    
    # Step 3: Get all user leagues
    user_leagues = explore_user_leagues()
    
    # Step 4: Check predecessor leagues
    predecessor_leagues = check_predecessor_leagues(renew_info)
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY OF AVAILABLE LEAGUES:")
    print("="*50)
    
    all_found = {}
    all_found.update(found_by_year)
    all_found.update(user_leagues)
    all_found.update(predecessor_leagues)
    
    if all_found:
        for year in sorted(all_found.keys(), reverse=True):
            league = all_found[year]
            print(f"FOUND {year}: {league.get('name', 'Unknown')} ({league.get('league_key', 'Unknown')})")
    else:
        print("No additional leagues found")
    
    print(f"\nTotal leagues found: {len(all_found)}")