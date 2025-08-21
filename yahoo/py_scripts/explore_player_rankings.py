#!/usr/bin/env python3
"""
Explore Yahoo Fantasy API for player rankings data.
This script investigates what preseason and end-of-season ranking data is available.
"""

from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import os

def explore_player_rankings():
    """
    Explore different ways to get player rankings from Yahoo API.
    """
    print("=== EXPLORING YAHOO PLAYER RANKINGS ===\n")
    
    # Initialize connection
    oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
    
    # Test with different years
    test_years = [
        ('2024', '454.l.44006'),  # Current/recent year
        ('2023', '426.l.81330'),  # Previous year
        ('2020', '402.l.121244')  # Original year we have
    ]
    
    for year, league_key in test_years:
        print(f"=== TESTING {year} (League: {league_key}) ===")
        
        try:
            league = yahoo_fantasy_api.league.League(oauth, league_key)
            
            # 1. Test league settings - might contain ranking info
            print("1. League Settings Analysis:")
            try:
                settings = league.settings()
                print(f"   Settings keys: {list(settings.keys()) if isinstance(settings, dict) else 'Not a dict'}")
                
                # Look for ranking-related settings
                for key, value in settings.items() if isinstance(settings, dict) else []:
                    if 'rank' in key.lower() or 'season' in key.lower():
                        print(f"   {key}: {value}")
            except Exception as e:
                print(f"   Error getting settings: {e}")
            
            # 2. Test stat categories - might have ranking info
            print("2. Stat Categories Analysis:")
            try:
                stat_cats = league.stat_categories()
                print(f"   Found {len(stat_cats)} stat categories")
                for cat in stat_cats:
                    if isinstance(cat, dict):
                        cat_name = cat.get('display_name', cat.get('name', 'Unknown'))
                        if 'rank' in cat_name.lower():
                            print(f"   Ranking category: {cat}")
            except Exception as e:
                print(f"   Error getting stat categories: {e}")
            
            # 3. Test player details for ranking info
            print("3. Player Details Analysis:")
            try:
                draft_results = league.draft_results()
                if draft_results and len(draft_results) > 0:
                    # Test first few players
                    for i, pick in enumerate(draft_results[:3]):
                        player_id = pick['player_id']
                        print(f"   Testing Player ID {player_id}:")
                        
                        try:
                            player_info = league.player_details(player_id)
                            if player_info and len(player_info) > 0:
                                player_data = player_info[0]
                                name = player_data.get('name', {}).get('full', 'Unknown')
                                print(f"     Name: {name}")
                                
                                # Look for ranking data
                                for key, value in player_data.items():
                                    if 'rank' in key.lower() or 'season' in key.lower():
                                        print(f"     {key}: {value}")
                                
                                # Check if player_stats contains ranking info
                                if 'player_stats' in player_data:
                                    stats = player_data['player_stats']
                                    print(f"     player_stats keys: {list(stats.keys())}")
                                    
                                    # Look at coverage_type - might indicate preseason vs season
                                    if 'coverage_type' in stats:
                                        print(f"     Coverage type: {stats['coverage_type']}")
                                    
                                    if 'season' in stats:
                                        print(f"     Season info: {stats['season']}")
                        except Exception as e:
                            print(f"     Error getting player details: {e}")
                        
                        if i >= 2:  # Only test first 3 players
                            break
            except Exception as e:
                print(f"   Error getting draft results: {e}")
            
            # 4. Test free agents for ranking data
            print("4. Free Agents Ranking Analysis:")
            try:
                free_agents = league.free_agents('PG')
                if free_agents and len(free_agents) > 0:
                    print(f"   Found {len(free_agents)} free agents")
                    # Look at first free agent
                    first_fa = free_agents[0]
                    print(f"   Sample free agent keys: {list(first_fa.keys()) if isinstance(first_fa, dict) else 'Not a dict'}")
                    
                    # Look for ranking info
                    for key, value in first_fa.items() if isinstance(first_fa, dict) else []:
                        if 'rank' in key.lower():
                            print(f"   {key}: {value}")
            except Exception as e:
                print(f"   Error getting free agents: {e}")
            
            # 5. Test if there are different stat periods
            print("5. Testing Different Stat Periods:")
            try:
                # Try to see if we can get preseason vs regular season stats
                # This might require different API calls or parameters
                pass
            except Exception as e:
                print(f"   Error testing stat periods: {e}")
                
        except Exception as e:
            print(f"Error testing league {league_key}: {e}")
        
        print()  # Blank line between years
    
    # 6. Test historical data structure
    print("=== EXAMINING EXISTING DATA STRUCTURE ===")
    for year in ['2024', '2023', '2020']:
        print(f"Checking {year} data structure:")
        year_dir = f'league_data/{year}/raw_data'
        if os.path.exists(year_dir):
            files = os.listdir(year_dir)
            print(f"   Files: {files}")
            
            # Check if any existing files contain ranking data
            for filename in files:
                if filename.endswith('.json'):
                    filepath = os.path.join(year_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            
                        # Search for ranking-related keys
                        ranking_keys = []
                        if isinstance(data, dict):
                            for key in data.keys():
                                if 'rank' in key.lower():
                                    ranking_keys.append(key)
                        elif isinstance(data, list) and len(data) > 0:
                            if isinstance(data[0], dict):
                                for key in data[0].keys():
                                    if 'rank' in key.lower():
                                        ranking_keys.append(key)
                        
                        if ranking_keys:
                            print(f"   {filename} has ranking keys: {ranking_keys}")
                            
                    except Exception as e:
                        print(f"   Error reading {filename}: {e}")
        else:
            print(f"   Directory not found")
    
    print("\n=== PLAYER RANKINGS EXPLORATION COMPLETE ===")

if __name__ == "__main__":
    explore_player_rankings()