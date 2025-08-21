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

def explore_renewal_chain(league_key, visited=None):
    """Recursively explore the renewal chain"""
    if visited is None:
        visited = set()
    
    if league_key in visited:
        print(f"  Circular reference detected for {league_key}")
        return {}
    
    visited.add(league_key)
    
    print(f"Exploring: {league_key}")
    
    try:
        league_data = make_api_call(f"league/{league_key}")
        if not league_data or 'fantasy_content' not in league_data:
            print(f"  No data found for {league_key}")
            return {}
        
        league_info = league_data['fantasy_content']['league'][0]
        name = league_info.get('name', 'Unknown')
        season = league_info.get('season', 'Unknown')
        renew = league_info.get('renew', None)
        renewed = league_info.get('renewed', None)
        
        print(f"  Found: {name} (Season: {season})")
        print(f"  Renew: {renew}, Renewed: {renewed}")
        
        # Store current league
        result = {
            season: {
                'league_key': league_key,
                'name': name,
                'season': season,
                'renew': renew,
                'renewed': renewed
            }
        }
        
        # Explore predecessor (renew field)
        if renew:
            parts = renew.split('_')
            if len(parts) >= 2:
                prev_game_code = parts[0]
                prev_league_id = parts[1]
                prev_league_key = f"{prev_game_code}.l.{prev_league_id}"
                print(f"  Following predecessor: {prev_league_key}")
                
                predecessor_leagues = explore_renewal_chain(prev_league_key, visited.copy())
                result.update(predecessor_leagues)
        
        # Explore successor (renewed field)  
        if renewed:
            parts = renewed.split('_')
            if len(parts) >= 2:
                next_game_code = parts[0]
                next_league_id = parts[1]
                next_league_key = f"{next_game_code}.l.{next_league_id}"
                print(f"  Following successor: {next_league_key}")
                
                successor_leagues = explore_renewal_chain(next_league_key, visited.copy())
                result.update(successor_leagues)
        
        return result
        
    except Exception as e:
        print(f"  Error exploring {league_key}: {e}")
        return {}

def test_known_working_leagues():
    """Test the specific leagues we found"""
    known_leagues = [
        "410.l.124782",  # From renewed field
        "395.l.98368",   # From renew field  
        "410.l.121244",  # 2021 season we found
        "346.l.121244"   # 2015 season we found
    ]
    
    print("\n=== TESTING KNOWN WORKING LEAGUES ===")
    results = {}
    
    for league_key in known_leagues:
        print(f"\nTesting: {league_key}")
        try:
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                league_info = league_data['fantasy_content']['league'][0]
                name = league_info.get('name', 'Unknown')
                season = league_info.get('season', 'Unknown')
                print(f"  SUCCESS: {name} (Season: {season})")
                results[season] = {
                    'league_key': league_key,
                    'name': name,
                    'season': season
                }
            else:
                print(f"  FAILED: No data")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return results

# Main execution
print("EXPLORING COMPLETE LEAGUE CHAIN\n")

# Start from the current league and explore the entire chain
current_league_key = "402.l.121244"
all_leagues = explore_renewal_chain(current_league_key)

# Also test the known working leagues
known_leagues = test_known_working_leagues()
all_leagues.update(known_leagues)

# Also check the other direction from the 2019 league we found
print("\n=== EXPLORING FROM 2019 LEAGUE ===")
leagues_2019 = explore_renewal_chain("395.l.98368")
all_leagues.update(leagues_2019)

print("\n" + "="*60)
print("COMPLETE LEAGUE TIMELINE:")
print("="*60)

if all_leagues:
    # Sort by season year
    sorted_seasons = sorted(all_leagues.keys(), key=lambda x: int(x) if x.isdigit() else 0)
    
    for season in sorted_seasons:
        league = all_leagues[season]
        print(f"{season}: {league.get('name', 'Unknown')}")
        print(f"    League Key: {league.get('league_key', 'Unknown')}")
        if league.get('renew'):
            print(f"    Predecessor: {league.get('renew')}")
        if league.get('renewed'):
            print(f"    Successor: {league.get('renewed')}")
        print()
else:
    print("No leagues found")

print(f"Total seasons found: {len(all_leagues)}")