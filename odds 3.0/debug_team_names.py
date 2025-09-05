"""
Debug script to see actual team names from both Pinnacle and Kalshi
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from core.pinnacle_client import PinnacleClientUpdated
from core.kalshi_client import KalshiClientUpdated

def debug_team_names():
    """Show actual team names from both platforms"""
    print("=== DEBUGGING TEAM NAMES ===")
    
    # Get Pinnacle data
    print("\n1. PINNACLE TEAM NAMES:")
    pinnacle = PinnacleClientUpdated()
    pin_games = pinnacle.get_upcoming_games('nfl')[:5]  # First 5 games
    
    for i, game in enumerate(pin_games, 1):
        print(f"  {i}. {game['away_team']} @ {game['home_team']}")
    
    print(f"\nPinnacle total games: {len(pin_games)}")
    
    # Get Kalshi data  
    print("\n2. KALSHI TEAM NAMES:")
    kalshi = KalshiClientUpdated()
    kal_games = kalshi.get_upcoming_games('nfl')[:5]  # First 5 games
    
    for i, game in enumerate(kal_games, 1):
        print(f"  {i}. {game['away_team']} @ {game['home_team']}")
    
    print(f"\nKalshi total games: {len(kal_games)}")

if __name__ == "__main__":
    debug_team_names()