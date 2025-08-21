from yahoo_oauth import OAuth2
import requests
import json

# Initialize OAuth
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
            print(f"Error {response.status_code} for {endpoint}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception for {endpoint}: {e}")
        return None

print("=== DIRECT YAHOO FANTASY API EXPLORATION ===\n")

league_key = "402.l.121244"

# 1. League standings with detailed stats
print("1. LEAGUE STANDINGS WITH STATS:")
standings_data = make_api_call(f"league/{league_key}/standings")
if standings_data:
    print(f"Standings data keys: {list(standings_data.keys())}")

# 2. League players (all available players)
print("\n2. LEAGUE PLAYERS:")
players_data = make_api_call(f"league/{league_key}/players")
if players_data:
    print(f"Players data available")

# 3. League transactions
print("\n3. LEAGUE TRANSACTIONS:")
transactions_data = make_api_call(f"league/{league_key}/transactions")
if transactions_data:
    print("Transactions data retrieved")

# 4. League scoreboard (weekly matchups)
print("\n4. LEAGUE SCOREBOARD:")
scoreboard_data = make_api_call(f"league/{league_key}/scoreboard")
if scoreboard_data:
    print("Scoreboard data retrieved")

# 5. Current game week info
print("\n5. GAME INFO:")
game_data = make_api_call("game/nba")
if game_data:
    print("Game data retrieved")

# 6. Player stats for specific weeks
print("\n6. PLAYER WEEKLY STATS TEST:")
# Try getting stats for Karl-Anthony Towns (player_id: 5432) for different weeks
player_id = "5432"
for week in [1, 10, 19]:  # Test different weeks
    stats_data = make_api_call(f"league/{league_key}/players;player_keys=402.p.{player_id}/stats;type=week;week={week}")
    if stats_data:
        print(f"  Week {week} stats for player {player_id}: Available")
    else:
        print(f"  Week {week} stats for player {player_id}: Not available")

# 7. Team rosters with stats
print("\n7. TEAM ROSTERS:")
teams_data = make_api_call(f"league/{league_key}/teams")
if teams_data and 'fantasy_content' in teams_data:
    teams_info = teams_data['fantasy_content']['league'][1]['teams']
    team_keys = [key for key in teams_info.keys() if key != 'count']
    
    # Get roster for first team
    if team_keys:
        first_team = team_keys[0]
        roster_data = make_api_call(f"team/{league_key}.t.{first_team}/roster")
        if roster_data:
            print(f"  Roster data for team {first_team}: Available")

# 8. Player season stats
print("\n8. PLAYER SEASON STATS:")
season_stats = make_api_call(f"league/{league_key}/players;player_keys=402.p.{player_id}/stats;type=season")
if season_stats:
    print(f"  Season stats for player {player_id}: Available")

print("\n=== DIRECT API EXPLORATION COMPLETE ===")