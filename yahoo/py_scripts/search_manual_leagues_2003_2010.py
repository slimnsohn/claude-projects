from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import time

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

def search_leagues_by_name_and_year(target_years, target_name="The Best Time of Year"):
    """Search for leagues with specific name across years"""
    print(f"=== SEARCHING FOR '{target_name}' LEAGUES 2003-2010 ===")
    
    # Yahoo NBA game codes for target years
    game_codes = {
        2010: 249,  # We know this one works
        2009: 238,
        2008: 231, 
        2007: 223,
        2006: 215,
        2005: 206,
        2004: 196,
        2003: 185
    }
    
    found_leagues = {}
    
    for year in target_years:
        if year not in game_codes:
            continue
            
        game_code = game_codes[year]
        print(f"\n--- Searching {year} (Game Code: {game_code}) ---")
        
        # Test a range of league IDs for this year
        # Yahoo typically assigns IDs in ranges, so we'll test common patterns
        league_id_ranges = [
            range(1, 1000, 50),        # Early leagues: 1, 51, 101, etc.
            range(1000, 10000, 100),   # Mid-range: 1000, 1100, 1200, etc.
            range(10000, 50000, 500),  # Higher IDs: 10000, 10500, etc.
            range(50000, 100000, 1000) # Even higher: 50000, 51000, etc.
        ]
        
        leagues_checked = 0
        max_checks_per_year = 200  # Limit to avoid too many API calls
        
        for id_range in league_id_ranges:
            for league_id in id_range:
                if leagues_checked >= max_checks_per_year:
                    break
                    
                league_key = f"{game_code}.l.{league_id}"
                leagues_checked += 1
                
                if leagues_checked % 50 == 0:
                    print(f"  Checked {leagues_checked} leagues...")
                
                league_data = make_api_call(f"league/{league_key}")
                if league_data and 'fantasy_content' in league_data:
                    try:
                        league_info = league_data['fantasy_content']['league'][0]
                        name = league_info.get('name', '')
                        season = league_info.get('season', '')
                        league_type = league_info.get('league_type', '')
                        
                        # Check for exact name match
                        if name == target_name and league_type == 'private':
                            print(f"  FOUND EXACT MATCH: {league_key} - {name} (Season: {season})")
                            found_leagues[year] = {
                                'league_key': league_key,
                                'name': name,
                                'season': season,
                                'league_type': league_type
                            }
                            break  # Found one for this year, move to next year
                        
                        # Also check for partial matches or similar names
                        elif 'best time' in name.lower() or 'time of year' in name.lower():
                            print(f"  PARTIAL MATCH: {league_key} - {name} (Season: {season})")
                            
                    except Exception as e:
                        pass  # Skip malformed responses
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.1)
            
            if year in found_leagues:
                break  # Found league for this year, stop searching
        
        print(f"  Searched {leagues_checked} leagues for {year}")
    
    return found_leagues

def search_by_manager_names():
    """Search for leagues containing known manager names"""
    print(f"\n=== SEARCHING BY KNOWN MANAGER NAMES ===")
    
    # Known team names from our 2020 data
    known_teams = ["Bzzzzznatch", "hersheysquirt", "forever Young", "Dirty South Asia", 
                   "Team Hoof Hearted", "The Krappers", "White Chocolate"]
    
    game_codes = {2009: 238, 2008: 231, 2007: 223, 2006: 215, 2005: 206, 2004: 196, 2003: 185}
    
    # Test a smaller, more targeted range focusing on mid-range IDs
    test_league_ids = list(range(20000, 60000, 1000))  # Sample every 1000 IDs
    
    found_by_managers = {}
    
    for year, game_code in game_codes.items():
        print(f"\n--- Checking {year} for known managers ---")
        checked = 0
        max_check = 40  # Limit per year
        
        for league_id in test_league_ids:
            if checked >= max_check:
                break
                
            league_key = f"{game_code}.l.{league_id}"
            checked += 1
            
            try:
                league = yahoo_fantasy_api.league.League(oauth, league_key)
                teams = league.teams()
                
                if teams and len(teams) >= 8:  # Should have decent number of teams
                    team_names = [team_data.get('name', '') for team_data in teams.values()]
                    
                    # Check for matches with known team names
                    matches = 0
                    for known_team in known_teams:
                        for team_name in team_names:
                            if known_team.lower() in team_name.lower():
                                matches += 1
                    
                    if matches >= 2:  # At least 2 matching team names
                        print(f"  POTENTIAL MATCH: {league_key}")
                        print(f"    Matches: {matches}")
                        print(f"    Team names: {team_names[:5]}")  # Show first 5 teams
                        
                        league_settings = league.settings()
                        league_name = league_settings.get('name', 'Unknown')
                        
                        found_by_managers[year] = {
                            'league_key': league_key,
                            'name': league_name,
                            'matches': matches,
                            'team_names': team_names
                        }
                        
            except Exception as e:
                pass  # League doesn't exist or can't access
            
            time.sleep(0.1)  # Small delay
    
    return found_by_managers

# Main execution
print("SEARCHING FOR MANUAL LEAGUES 2003-2010")
print("="*60)

target_years = [2009, 2008, 2007, 2006, 2005, 2004, 2003]

# Method 1: Search by exact league name
name_matches = search_leagues_by_name_and_year(target_years)

# Method 2: Search by known manager/team names  
manager_matches = search_by_manager_names()

# Summary
print(f"\n" + "="*60)
print("SEARCH RESULTS SUMMARY:")
print("="*60)

print("\n1. EXACT NAME MATCHES:")
if name_matches:
    for year in sorted(name_matches.keys(), reverse=True):
        league = name_matches[year]
        print(f"  {year}: {league['name']} ({league['league_key']})")
else:
    print("  No exact name matches found")

print("\n2. MANAGER/TEAM NAME MATCHES:")
if manager_matches:
    for year in sorted(manager_matches.keys(), reverse=True):
        league = manager_matches[year]
        print(f"  {year}: {league['name']} ({league['league_key']}) - {league['matches']} matches")
else:
    print("  No manager name matches found")

all_matches = {}
all_matches.update(name_matches)
all_matches.update(manager_matches)

print(f"\nTOTAL ADDITIONAL LEAGUES FOUND: {len(all_matches)}")

if all_matches:
    print("\nRecommendation: Test these league keys to extract draft data:")
    for year in sorted(all_matches.keys(), reverse=True):
        league = all_matches[year]
        print(f"  {year}: league_key = '{league['league_key']}'")
else:
    print("\nConclusion: No additional leagues found for 2003-2010.")
    print("Your complete dataset remains: 2010-2024 (15 seasons)")

print(f"\nNote: This search tested a sample of possible league IDs.")
print(f"There may be other leagues that weren't found in this search.")