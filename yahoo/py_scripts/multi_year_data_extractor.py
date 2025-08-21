from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import pandas as pd
from datetime import datetime

# Initialize connection
oauth = OAuth2(None, None, from_file='jsons/oauth2.json')

# Complete league timeline discovered
LEAGUES = {
    '2010': '249.l.40919',
    '2011': '265.l.40720', 
    '2012': '304.l.62665',
    '2013': '322.l.90972',
    '2014': '342.l.129190',
    '2015': '353.l.93240',
    '2016': '364.l.90263',
    '2017': '375.l.111279',
    '2018': '385.l.42210',
    '2019': '395.l.98368',
    '2020': '402.l.121244',  # Original league we had
    '2021': '410.l.124782',
    '2022': '418.l.104779',
    '2023': '428.l.32747',
    '2024': '454.l.44006'
}

def extract_league_data(league_key, season):
    """Extract comprehensive data from a single league"""
    print(f"\n=== EXTRACTING {season} DATA ({league_key}) ===")
    
    try:
        league = yahoo_fantasy_api.league.League(oauth, league_key)
        data = {'season': season, 'league_key': league_key}
        
        # 1. League Settings
        try:
            settings = league.settings()
            data['settings'] = settings
            print(f"  League Name: {settings.get('name', 'N/A')}")
            print(f"  Draft Type: {settings.get('draft_type', 'N/A')}")
            print(f"  Scoring Type: {settings.get('scoring_type', 'N/A')}")
        except Exception as e:
            print(f"  Settings error: {e}")
            data['settings'] = None
        
        # 2. Teams
        try:
            teams = league.teams()
            data['teams'] = teams
            print(f"  Teams: {len(teams)} found")
        except Exception as e:
            print(f"  Teams error: {e}")
            data['teams'] = None
        
        # 3. Draft Results
        try:
            draft_results = league.draft_results()
            data['draft_results'] = draft_results
            print(f"  Draft: {len(draft_results)} picks")
        except Exception as e:
            print(f"  Draft error: {e}")
            data['draft_results'] = None
        
        # 4. Standings
        try:
            standings = league.standings()
            data['standings'] = standings
            print(f"  Standings: {len(standings)} teams")
        except Exception as e:
            print(f"  Standings error: {e}")
            data['standings'] = None
        
        # 5. Stat Categories
        try:
            stat_cats = league.stat_categories()
            data['stat_categories'] = stat_cats
            print(f"  Stat categories: {len(stat_cats)} found")
        except Exception as e:
            print(f"  Stat categories error: {e}")
            data['stat_categories'] = None
        
        return data
        
    except Exception as e:
        print(f"  FAILED to access league: {e}")
        return {'season': season, 'league_key': league_key, 'error': str(e)}

def save_league_data(data, season):
    """Save league data to JSON file"""
    filename = f"league_data_{season}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Saved to {filename}")

def create_draft_summary():
    """Create a summary of all draft data found"""
    print("\n=== CREATING DRAFT SUMMARY ===")
    
    draft_summary = []
    for season, league_key in LEAGUES.items():
        try:
            league = yahoo_fantasy_api.league.League(oauth, league_key)
            draft_results = league.draft_results()
            
            if draft_results:
                draft_summary.append({
                    'season': season,
                    'league_key': league_key,
                    'total_picks': len(draft_results),
                    'sample_pick': draft_results[0] if draft_results else None
                })
                print(f"  {season}: {len(draft_results)} picks")
            else:
                print(f"  {season}: No draft data")
                
        except Exception as e:
            print(f"  {season}: Error - {e}")
    
    return draft_summary

# Main execution
print("EXTRACTING DATA FROM ALL 15 SEASONS")
print("="*50)

# Test a few key seasons first (to avoid rate limits)
test_seasons = ['2024', '2020', '2015', '2010']

all_data = {}
for season in test_seasons:
    if season in LEAGUES:
        league_key = LEAGUES[season]
        data = extract_league_data(league_key, season)
        all_data[season] = data
        
        # Save individual season data
        save_league_data(data, season)

# Create draft summary for all years
draft_summary = create_draft_summary()

# Save the draft summary
with open('draft_summary_all_years.json', 'w') as f:
    json.dump(draft_summary, f, indent=2, default=str)

print(f"\n" + "="*50)
print("EXTRACTION COMPLETE")
print("="*50)
print(f"Successfully extracted data from {len(all_data)} seasons")
print("Files created:")
for season in all_data.keys():
    print(f"  - league_data_{season}.json")
print("  - draft_summary_all_years.json")

print(f"\nTotal seasons available: {len(LEAGUES)} (2010-2024)")
print("All league keys discovered:")
for season, key in LEAGUES.items():
    print(f"  {season}: {key}")