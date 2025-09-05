"""
Simple script to view all games from both Pinnacle and Kalshi
Clean table output showing teams, odds, and game times
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pinnacle.client import PinnacleClient
from kalshi.client import KalshiClient

def view_games(league='mlb', remove_live_games=True):
    """View games from both platforms"""
    
    print(f"\n{'='*100}")
    print(f"VIEWING ALL {league.upper()} GAMES")
    print(f"Remove Live Games: {remove_live_games}")
    print(f"{'='*100}")
    
    # Test Pinnacle
    print(f"\n>> PINNACLE {league.upper()} GAMES")
    print("-" * 50)
    try:
        pinnacle = PinnacleClient()
        pinnacle_games = pinnacle.get_games(league=league, remove_live_games=remove_live_games)
        pinnacle.print_games_table(pinnacle_games)
    except Exception as e:
        print(f"Error with Pinnacle: {e}")
    
    # Test Kalshi  
    print(f"\n>> KALSHI {league.upper()} GAMES")
    print("-" * 50)
    try:
        kalshi = KalshiClient()
        kalshi_games = kalshi.get_games(league=league, remove_live_games=remove_live_games)
        kalshi.print_games_table(kalshi_games)
    except Exception as e:
        print(f"Error with Kalshi: {e}")
    
    print(f"\n{'='*100}")
    print("SUMMARY:")
    try:
        print(f"Pinnacle {league.upper()}: {len(pinnacle_games)} games")
        print(f"Kalshi {league.upper()}: {len(kalshi_games)} games")
    except:
        print("Error generating summary")
    print(f"{'='*100}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='View games from Pinnacle and Kalshi')
    parser.add_argument('--league', default='mlb', help='League to check (mlb, nfl, nba, nhl)')
    parser.add_argument('--include-live', action='store_true', help='Include live/finished games')
    
    args = parser.parse_args()
    
    # Default behavior: show MLB with live games filtered out
    remove_live = not args.include_live
    
    view_games(league=args.league, remove_live_games=remove_live)