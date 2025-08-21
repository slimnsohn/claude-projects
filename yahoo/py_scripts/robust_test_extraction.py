"""
Robust test extraction with better error handling
"""

from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import time
from pathlib import Path

def test_single_league(league_key, year):
    """Test extraction from a single league with robust error handling"""
    print(f"\nTesting {year} ({league_key})")
    print("-" * 40)
    
    try:
        oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
        
        # Test basic API access first
        print("1. Testing OAuth connection...")
        if not oauth.token_is_valid():
            print("   Token expired, refreshing...")
            oauth.refresh_access_token()
        print("   SUCCESS: OAuth connected")
        
        # Test league initialization
        print("2. Testing league initialization...")
        league = yahoo_fantasy_api.league.League(oauth, league_key)
        print("   SUCCESS: League object created")
        
        # Test individual API calls
        results = {}
        
        print("3. Testing league settings...")
        try:
            settings = league.settings()
            results['settings'] = True
            print(f"   SUCCESS: League name = {settings.get('name', 'Unknown')}")
        except Exception as e:
            results['settings'] = False
            print(f"   ERROR: {str(e)}")
        
        print("4. Testing teams...")
        try:
            teams = league.teams()
            results['teams'] = True
            print(f"   SUCCESS: Found {len(teams)} teams")
        except Exception as e:
            results['teams'] = False
            print(f"   ERROR: {str(e)}")
        
        print("5. Testing draft results...")
        try:
            draft_results = league.draft_results()
            results['draft'] = True
            print(f"   SUCCESS: Found {len(draft_results)} draft picks")
        except Exception as e:
            results['draft'] = False
            print(f"   ERROR: {str(e)}")
        
        print("6. Testing standings...")
        try:
            standings = league.standings()
            results['standings'] = True
            print(f"   SUCCESS: Found {len(standings)} standings entries")
        except Exception as e:
            results['standings'] = False
            print(f"   ERROR: {str(e)}")
        
        # Summary
        successful_calls = sum(results.values())
        total_calls = len(results)
        print(f"\nSUMMARY: {successful_calls}/{total_calls} API calls successful")
        
        return results
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return {}

def test_recent_years():
    """Test the most recent years that should definitely work"""
    
    recent_leagues = {
        '2024': '454.l.44006',
        '2023': '428.l.32747', 
        '2022': '418.l.104779',
        '2021': '410.l.124782',
        '2020': '402.l.121244'
    }
    
    print("ROBUST YAHOO API TEST")
    print("=" * 50)
    print("Testing recent years to identify working patterns...")
    
    all_results = {}
    
    for year, league_key in recent_leagues.items():
        results = test_single_league(league_key, year)
        all_results[year] = results
        
        # Wait between tests to avoid rate limiting
        print("   Waiting 5 seconds before next test...")
        time.sleep(5)
    
    # Final analysis
    print("\n" + "=" * 50)
    print("FINAL ANALYSIS:")
    print("=" * 50)
    
    for year, results in all_results.items():
        if results:
            successful = sum(results.values())
            total = len(results)
            status = "WORKING" if successful >= 2 else "PARTIAL" if successful >= 1 else "FAILED"
            print(f"{year}: {status} ({successful}/{total} calls successful)")
            
            if results.get('draft', False) and results.get('teams', False):
                print(f"      -> {year} has core data needed for analysis")
        else:
            print(f"{year}: FAILED (no data)")
    
    # Recommendations
    working_years = [year for year, results in all_results.items() 
                    if results.get('draft', False) and results.get('teams', False)]
    
    if working_years:
        print(f"\nRECOMMENDATION:")
        print(f"Start data extraction with these {len(working_years)} working years:")
        for year in working_years:
            print(f"  - {year}")
        print(f"\nThen expand to other years once system is proven.")
    else:
        print(f"\nWARNING: No years are fully working.")
        print(f"This suggests API access issues that need to be resolved.")

if __name__ == "__main__":
    test_recent_years()