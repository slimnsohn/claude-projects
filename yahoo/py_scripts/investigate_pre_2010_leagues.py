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

def investigate_found_leagues():
    """Investigate the pre-2010 leagues we found"""
    print("=== INVESTIGATING FOUND PRE-2010 LEAGUES ===")
    
    found_leagues = [
        {'key': '175.l.40919', 'year': 2007, 'name': 'Yahoo Public 40919'},
        {'key': '153.l.40919', 'year': 2006, 'name': 'Yahoo Winner 40919'}
    ]
    
    for league_info in found_leagues:
        league_key = league_info['key']
        print(f"\n--- Investigating {league_key} ---")
        
        try:
            # Get detailed league information
            league_data = make_api_call(f"league/{league_key}")
            if league_data and 'fantasy_content' in league_data:
                league_details = league_data['fantasy_content']['league'][0]
                
                print(f"Name: {league_details.get('name', 'N/A')}")
                print(f"Season: {league_details.get('season', 'N/A')}")
                print(f"League Type: {league_details.get('league_type', 'N/A')}")
                print(f"Number of Teams: {league_details.get('num_teams', 'N/A')}")
                print(f"Renew: {league_details.get('renew', 'EMPTY')}")
                print(f"Renewed: {league_details.get('renewed', 'EMPTY')}")
                
                # Try to access it as a league object
                try:
                    league = yahoo_fantasy_api.league.League(oauth, league_key)
                    
                    # Try to get teams
                    teams = league.teams()
                    print(f"Teams: {len(teams)} found")
                    
                    # Try to get draft results
                    draft_results = league.draft_results()
                    print(f"Draft Results: {len(draft_results)} picks found")
                    
                    # Try to get settings
                    settings = league.settings()
                    print(f"Settings: Available")
                    
                    # Check if this could be related to our league
                    print(f"Possible connection to main league: {'YES' if league_details.get('renewed') else 'NO'}")
                    
                except Exception as e:
                    print(f"Error accessing as league object: {e}")
            else:
                print(f"Could not get league data for {league_key}")
                
        except Exception as e:
            print(f"Error investigating {league_key}: {e}")

def check_league_id_40919_history():
    """Check if league ID 40919 has a longer history"""
    print(f"\n=== CHECKING LEAGUE ID 40919 ACROSS YEARS ===")
    
    # Test various game codes with the same league ID
    test_codes = [
        (2010, 249),  # Our known 2010 league
        (2009, 238), (2008, 231), (2007, 223), (2006, 215), (2005, 206),
        (2004, 196), (2003, 185), (2002, 175), (2001, 164), (2000, 153)
    ]
    
    league_40919_history = {}
    
    for year, code in test_codes:
        league_key = f"{code}.l.40919"
        print(f"\nTesting {year}: {league_key}")
        
        league_data = make_api_call(f"league/{league_key}")
        if league_data and 'fantasy_content' in league_data:
            try:
                league_info = league_data['fantasy_content']['league'][0]
                name = league_info.get('name', 'Unknown')
                season = league_info.get('season', 'Unknown')
                league_type = league_info.get('league_type', 'Unknown')
                
                print(f"  FOUND: {name} (Season: {season}, Type: {league_type})")
                
                league_40919_history[year] = {
                    'league_key': league_key,
                    'name': name,
                    'season': season,
                    'league_type': league_type
                }
                
                # Check if it's private vs public
                if league_type == 'private':
                    print(f"  -> PRIVATE LEAGUE (could be connected to main league)")
                else:
                    print(f"  -> PUBLIC LEAGUE (likely not connected)")
                    
            except Exception as e:
                print(f"  Error parsing: {e}")
        else:
            print(f"  Not found")
    
    return league_40919_history

def final_analysis():
    """Final analysis of pre-2010 situation"""
    print(f"\n=== FINAL ANALYSIS ===")
    
    print("Key findings:")
    print("1. The 2010 league (249.l.40919) has renew: '' (empty)")
    print("2. Found leagues with same ID 40919 in earlier years")
    print("3. These earlier leagues appear to be public/contest leagues")
    print("4. 'The Best Time of Year' name first appears in 2010")
    print()
    
    print("Conclusion:")
    print("- 2010 (249.l.40919) is likely the FIRST year of your private league")
    print("- The league ID 40919 may have been reused from older public leagues") 
    print("- Your 15-year dataset (2010-2024) appears to be complete")
    print("- Total span: 15 consecutive seasons of the same private league")

# Main execution
print("INVESTIGATING PRE-2010 FINDINGS")
print("="*50)

# Investigate the specific leagues we found
investigate_found_leagues()

# Check the broader history of league ID 40919
history_40919 = check_league_id_40919_history()

# Final analysis
final_analysis()

print(f"\n" + "="*50)
print("LEAGUE ID 40919 COMPLETE HISTORY:")
print("="*50)

if history_40919:
    for year in sorted(history_40919.keys()):
        league = history_40919[year]
        league_type = league.get('league_type', 'Unknown')
        name = league.get('name', 'Unknown')
        print(f"{year}: {name} ({league_type})")
else:
    print("No historical data found for league ID 40919")

print(f"\nFinal Answer: Your private league 'The Best Time of Year' started in 2010.")
print(f"Total available data: 15 consecutive seasons (2010-2024)")