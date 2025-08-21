from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json

# Initialize connection
oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
league = yahoo_fantasy_api.league.League(oauth, '402.l.121244')

print("=== PLAYER STATS AND RANKINGS EXPLORATION ===\n")

# Get some player IDs from draft results for testing
draft_results = league.draft_results()
print(f"Draft contains {len(draft_results)} picks")

# Test different stat types
print("\n1. TESTING PLAYER SEASON STATS:")
try:
    # Get first few drafted players
    for i, pick in enumerate(draft_results[:3]):
        player_id = pick['player_id']
        print(f"\nPlayer ID {player_id} (Pick {i+1}):")
        
        # Get player basic info
        try:
            player_info = league.player_details(player_id)
            if player_info and len(player_info) > 0:
                name = player_info[0]['name']['full']
                team = player_info[0].get('editorial_team_abbr', 'N/A')
                position = player_info[0].get('display_position', 'N/A')
                print(f"  Name: {name}")
                print(f"  Team: {team}, Position: {position}")
                
                # Look at season stats
                if 'player_stats' in player_info[0]:
                    stats = player_info[0]['player_stats']['stats']
                    print(f"  Season stats ({len(stats)} categories):")
                    for stat in stats[:5]:  # First 5 stats
                        stat_id = stat['stat']['stat_id']
                        value = stat['stat']['value']
                        print(f"    Stat ID {stat_id}: {value}")
                        
        except Exception as e:
            print(f"  Error getting details: {e}")
            
except Exception as e:
    print(f"Error in player stats test: {e}")

# Test league-wide player rankings
print("\n2. TESTING PLAYER RANKINGS/SEARCH:")
try:
    # Search for specific players
    search_results = league.player_search('LeBron')
    print(f"Search for 'LeBron': {len(search_results)} results")
    if search_results:
        for i, player in enumerate(search_results[:2]):
            print(f"  Result {i+1}: {player}")
except Exception as e:
    print(f"Player search error: {e}")

# Test stat categories
print("\n3. TESTING STAT CATEGORIES:")
try:
    stat_categories = league.stat_categories()
    print(f"Stat categories available: {len(stat_categories)}")
    for i, cat in enumerate(stat_categories[:10]):  # First 10
        print(f"  {i+1}: {cat}")
except Exception as e:
    print(f"Stat categories error: {e}")

# Test weekly stats
print("\n4. TESTING WEEKLY PLAYER STATS:")
try:
    # Get a team and try to get weekly stats for one of its players
    teams = league.teams()
    first_team_key = list(teams.keys())[0]
    team = yahoo_fantasy_api.Team(oauth, first_team_key)
    
    # Get team stats for a week
    team_stats = team.stats()
    print(f"Team stats available: {type(team_stats)}")
    if isinstance(team_stats, dict):
        print(f"  Stats keys: {list(team_stats.keys())}")
    
except Exception as e:
    print(f"Weekly stats error: {e}")

print("\n5. TESTING PLAYER POOL/FREE AGENTS:")
try:
    # Test different positions
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    for pos in positions[:2]:  # Test first 2 positions
        free_agents = league.free_agents(pos)
        print(f"Free agents at {pos}: {len(free_agents)} found")
        if free_agents:
            print(f"  Sample: {free_agents[0]}")
        
except Exception as e:
    print(f"Free agents error: {e}")

print("\n=== PLAYER STATS EXPLORATION COMPLETE ===")