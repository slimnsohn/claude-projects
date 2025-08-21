#!/usr/bin/env python3
"""
Extract Yahoo Fantasy player rankings - preseason and end-of-season.
This script tries different API endpoints to find player ranking data.
"""

from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import os
from collections import defaultdict

def test_player_ranking_endpoints():
    """
    Test various Yahoo API endpoints to find player ranking data.
    """
    print("=== TESTING PLAYER RANKING ENDPOINTS ===\n")
    
    # Initialize connection
    oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
    
    # Test with 2024 league
    league_key = '454.l.44006'
    league = yahoo_fantasy_api.league.League(oauth, league_key)
    
    print(f"Testing league: {league_key}")
    
    # 1. Test percent_owned data in free agents (might include rankings)
    print("1. Free Agents Detailed Analysis:")
    try:
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        for pos in positions[:2]:  # Test first 2 positions
            free_agents = league.free_agents(pos)
            print(f"   {pos} Free Agents: {len(free_agents)} found")
            
            if free_agents and len(free_agents) > 0:
                # Look at first few free agents in detail
                for i, player in enumerate(free_agents[:3]):
                    print(f"     Player {i+1}:")
                    for key, value in player.items():
                        print(f"       {key}: {value}")
                    
                    # Try to get detailed player info
                    try:
                        player_id = player['player_id']
                        details = league.player_details(player_id)
                        if details and len(details) > 0:
                            player_data = details[0]
                            print(f"       Detailed info keys: {list(player_data.keys())}")
                            
                            # Look for any ranking-related data
                            for key, value in player_data.items():
                                if 'rank' in key.lower() or 'tier' in key.lower() or 'projected' in key.lower():
                                    print(f"       *** {key}: {value}")
                    except Exception as e:
                        print(f"       Error getting details: {e}")
                    
                    if i >= 2:  # Only check first 3
                        break
            
            if pos == 'SG':  # Only test first 2 positions
                break
                
    except Exception as e:
        print(f"   Error testing free agents: {e}")
    
    # 2. Test player search functionality
    print("\n2. Player Search Analysis:")
    try:
        # Search for well-known players
        test_players = ['LeBron', 'Steph', 'Durant']
        for search_term in test_players:
            results = league.player_search(search_term)
            print(f"   Search '{search_term}': {len(results)} results")
            
            if results and len(results) > 0:
                first_result = results[0]
                print(f"     First result keys: {list(first_result.keys())}")
                
                # Look for ranking data in search results
                for key, value in first_result.items():
                    if 'rank' in key.lower() or 'tier' in key.lower() or 'projected' in key.lower() or 'season' in key.lower():
                        print(f"     *** {key}: {value}")
                
                # Get full details for this player
                try:
                    player_id = first_result['player_id']
                    details = league.player_details(player_id)
                    if details and len(details) > 0:
                        player_data = details[0]
                        
                        # Look through all player data for ranking info
                        print(f"     Full player data keys: {list(player_data.keys())}")
                        
                        # Check stats structure
                        if 'player_stats' in player_data:
                            stats_data = player_data['player_stats']
                            print(f"     Player stats structure: {list(stats_data.keys())}")
                            
                            # Look at stats array
                            if 'stats' in stats_data:
                                stats_array = stats_data['stats']
                                print(f"     Found {len(stats_array)} individual stats")
                                
                                # Look for ranking-related stats
                                for stat in stats_array:
                                    if isinstance(stat, dict) and 'stat' in stat:
                                        stat_info = stat['stat']
                                        stat_id = stat_info.get('stat_id', '')
                                        value = stat_info.get('value', '')
                                        
                                        # Check if this might be a ranking stat
                                        if any(keyword in str(stat_id).lower() for keyword in ['rank', 'tier', 'proj']):
                                            print(f"     *** Potential ranking stat - ID: {stat_id}, Value: {value}")
                        
                        # Check if there are multiple stat periods/seasons
                        for key, value in player_data.items():
                            if 'season' in key.lower() or 'preseason' in key.lower():
                                print(f"     *** Season-related data - {key}: {value}")
                                
                except Exception as e:
                    print(f"     Error getting player details: {e}")
                    
            break  # Only test first search term for now
            
    except Exception as e:
        print(f"   Error testing player search: {e}")
    
    # 3. Test if we can access different stat types or periods
    print("\n3. Testing Different Stat Types/Periods:")
    try:
        # Get draft results to test with actual drafted players
        draft_results = league.draft_results()
        if draft_results and len(draft_results) > 0:
            # Test first drafted player
            first_pick = draft_results[0]
            player_id = first_pick['player_id']
            
            print(f"   Testing with player ID {player_id} (first draft pick)")
            
            # Try different ways to get player stats
            details = league.player_details(player_id)
            if details and len(details) > 0:
                player_data = details[0]
                name = player_data.get('name', {}).get('full', 'Unknown')
                print(f"   Player: {name}")
                
                # Look at all keys for anything that might be rankings
                all_keys = list(player_data.keys())
                print(f"   All player data keys: {all_keys}")
                
                # Check specific structures that might contain rankings
                for key in ['player_stats', 'player_points', 'season_stats', 'preseason_stats']:
                    if key in player_data:
                        print(f"   Found {key}: {type(player_data[key])}")
                        if isinstance(player_data[key], dict):
                            print(f"     {key} keys: {list(player_data[key].keys())}")
                
    except Exception as e:
        print(f"   Error testing stat types: {e}")
    
    # 4. Test if league has different endpoints for rankings
    print("\n4. Testing League-Level Ranking Endpoints:")
    try:
        # Check if league object has any ranking-related methods
        league_methods = [method for method in dir(league) if not method.startswith('_')]
        ranking_methods = [method for method in league_methods if 'rank' in method.lower()]
        
        print(f"   Available league methods: {len(league_methods)}")
        print(f"   Ranking-related methods: {ranking_methods}")
        
        # Try some common ranking method names
        potential_methods = ['player_rankings', 'rankings', 'preseason_rankings', 'season_rankings']
        for method_name in potential_methods:
            if hasattr(league, method_name):
                try:
                    result = getattr(league, method_name)()
                    print(f"   *** Found {method_name}: {type(result)}")
                    if isinstance(result, list) and len(result) > 0:
                        print(f"     Sample: {result[0]}")
                except Exception as e:
                    print(f"   Error calling {method_name}: {e}")
        
    except Exception as e:
        print(f"   Error testing league methods: {e}")

def extract_ranking_data_for_year(year, league_key):
    """
    Extract any available ranking data for a specific year.
    """
    print(f"\n=== EXTRACTING RANKING DATA FOR {year} ===")
    
    try:
        oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
        league = yahoo_fantasy_api.league.League(oauth, league_key)
        
        # Check if this is before or after season
        settings = league.settings()
        is_finished = settings.get('is_finished', False)
        season_status = "completed" if is_finished else "in progress"
        
        print(f"League status: {season_status}")
        
        ranking_data = {
            'year': year,
            'league_key': league_key,
            'season_status': season_status,
            'player_rankings': [],
            'extraction_notes': []
        }
        
        # Try to get ranking data from different sources
        
        # 1. Free agents with ownership percentages (proxy for popularity/rankings)
        print("Extracting free agent popularity data...")
        try:
            all_free_agents = []
            positions = ['PG', 'SG', 'SF', 'PF', 'C']
            
            for pos in positions:
                free_agents = league.free_agents(pos)
                for player in free_agents:
                    if 'percent_owned' in player:
                        all_free_agents.append({
                            'player_id': player['player_id'],
                            'name': player['name']['full'] if isinstance(player['name'], dict) else str(player['name']),
                            'position': pos,
                            'percent_owned': float(player['percent_owned']['value']) if isinstance(player['percent_owned'], dict) else float(player['percent_owned']),
                            'status': player.get('status', 'Unknown')
                        })
            
            # Sort by ownership percentage (highest = most popular)
            all_free_agents.sort(key=lambda x: x['percent_owned'], reverse=True)
            ranking_data['free_agent_popularity'] = all_free_agents[:50]  # Top 50
            ranking_data['extraction_notes'].append(f"Found {len(all_free_agents)} free agents with ownership data")
            
        except Exception as e:
            ranking_data['extraction_notes'].append(f"Error extracting free agent data: {e}")
        
        # 2. Try to get additional stats that might include rankings
        print("Checking for additional ranking stats...")
        try:
            draft_results = league.draft_results()
            
            for pick in draft_results[:10]:  # Test first 10 draft picks
                player_id = pick['player_id']
                details = league.player_details(player_id)
                
                if details and len(details) > 0:
                    player_data = details[0]
                    name = player_data.get('name', {}).get('full', 'Unknown')
                    
                    # Look for any stats that might be rankings
                    if 'player_stats' in player_data:
                        stats = player_data['player_stats'].get('stats', [])
                        
                        for stat in stats:
                            if isinstance(stat, dict) and 'stat' in stat:
                                stat_info = stat['stat']
                                stat_id = stat_info.get('stat_id', '')
                                
                                # Look for high stat IDs that might be rankings
                                if isinstance(stat_id, str) and stat_id.isdigit():
                                    stat_id_num = int(stat_id)
                                    if stat_id_num > 100:  # Rankings might be in higher ID ranges
                                        ranking_data['extraction_notes'].append(
                                            f"Player {name}: Found high stat ID {stat_id} = {stat_info.get('value', 'N/A')}"
                                        )
        
        except Exception as e:
            ranking_data['extraction_notes'].append(f"Error checking additional stats: {e}")
        
        # Save ranking data
        output_dir = f'league_data/{year}/raw_data'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'player_rankings.json')
        with open(output_file, 'w') as f:
            json.dump(ranking_data, f, indent=2)
        
        print(f"Ranking data saved to {output_file}")
        print(f"Notes: {ranking_data['extraction_notes']}")
        
        return ranking_data
        
    except Exception as e:
        print(f"Error extracting ranking data for {year}: {e}")
        return None

def main():
    """
    Main function to explore and extract player rankings.
    """
    print("=== YAHOO FANTASY PLAYER RANKINGS EXTRACTION ===\n")
    
    # First, explore what's available
    test_player_ranking_endpoints()
    
    # Then try to extract ranking data for a few test years
    test_years = [
        ('2024', '454.l.44006'),
        ('2020', '402.l.121244')
    ]
    
    for year, league_key in test_years:
        extract_ranking_data_for_year(year, league_key)
    
    print("\n=== RANKING EXTRACTION COMPLETE ===")

if __name__ == "__main__":
    main()