from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import pprint

# Initialize connection
oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
league = yahoo_fantasy_api.league.League(oauth, '402.l.121244')

print("=== YAHOO FANTASY API DATA EXPLORATION ===\n")

# 1. LEAGUE INFORMATION
print("1. LEAGUE SETTINGS:")
settings = league.settings()
pprint.pprint(settings)
print()

# 2. TEAMS INFORMATION  
print("2. TEAMS:")
teams = league.teams()
for team_key, team_data in list(teams.items())[:3]:  # Show first 3 teams
    print(f"Team Key: {team_key}")
    pprint.pprint(team_data)
    print()

# 3. DRAFT RESULTS
print("3. DRAFT RESULTS SAMPLE:")
draft_results = league.draft_results()
print(f"Total draft picks: {len(draft_results)}")
for i, pick in enumerate(draft_results[:5]):  # Show first 5 picks
    print(f"Pick {i+1}: {pick}")
print()

# 4. STANDINGS
print("4. STANDINGS:")
standings = league.standings()
for i, team in enumerate(standings[:3]):  # Show first 3 standings
    print(f"Position {i+1}: {team}")
print()

# 5. PLAYER INFORMATION
print("5. TESTING PLAYER DETAILS:")
try:
    # Get player details for the first drafted player
    first_pick = draft_results[0]
    player_id = first_pick.get('player_id')
    if player_id:
        player_details = league.player_details(player_id)
        print(f"Player {player_id} details:")
        pprint.pprint(player_details)
except Exception as e:
    print(f"Player details error: {e}")
print()

# 6. WEEK/STATS INFORMATION
print("6. TESTING WEEK/STATS:")
try:
    # Try to get current week
    current_week = league.current_week()
    print(f"Current week: {current_week}")
except Exception as e:
    print(f"Current week error: {e}")

try:
    # Try to get a team's roster
    team_keys = list(teams.keys())
    if team_keys:
        first_team_key = team_keys[0]
        team = yahoo_fantasy_api.Team(oauth, first_team_key)
        roster = team.roster()
        print(f"Team roster sample (first 3 players):")
        for i, player in enumerate(roster[:3]):
            print(f"Player {i+1}: {player}")
except Exception as e:
    print(f"Team roster error: {e}")

# 7. FREE AGENTS / PLAYER POOL
print("\n7. TESTING FREE AGENTS:")
try:
    free_agents = league.free_agents('C')  # Centers
    print(f"Free agent centers sample (first 3):")
    for i, player in enumerate(free_agents[:3]):
        print(f"FA {i+1}: {player}")
except Exception as e:
    print(f"Free agents error: {e}")

print("\n=== EXPLORATION COMPLETE ===")