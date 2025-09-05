"""
View NFL Games from Pinnacle
Simple script to display Pinnacle NFL odds
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from core.pinnacle_client import PinnacleClient

def view_pinnacle_nfl():
    """Display NFL games from Pinnacle"""
    print("=" * 60)
    print("PINNACLE NFL GAMES")
    print("=" * 60)
    
    try:
        # Initialize Pinnacle client
        client = PinnacleClient("keys/odds_api_key.txt")
        
        # Get NFL odds
        result = client.get_sports_odds('nfl')
        
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
            return
        
        games = result.get('data', [])
        print(f"Found {len(games)} NFL games:\n")
        
        for i, game in enumerate(games, 1):
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            game_time = game.get('commence_time')
            
            print(f"{i}. {away_team} @ {home_team}")
            print(f"   Time: {game_time}")
            
            # Find Pinnacle odds
            for bookmaker in game.get('bookmakers', []):
                if bookmaker.get('key') == 'pinnacle':
                    for market in bookmaker.get('markets', []):
                        if market.get('key') == 'h2h':
                            outcomes = market.get('outcomes', [])
                            for outcome in outcomes:
                                team = outcome.get('name')
                                odds = outcome.get('price')
                                if team == home_team:
                                    print(f"   {home_team}: {odds:+d}")
                                elif team == away_team:
                                    print(f"   {away_team}: {odds:+d}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_pinnacle_nfl()