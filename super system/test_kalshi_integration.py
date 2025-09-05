#!/usr/bin/env python3
"""
Test Kalshi Integration
Quick test to verify Kalshi client retrieves NFL games
"""

import sys
import os
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market_data.kalshi.production.client import KalshiClient
from config.constants import Sport

def main():
    print("Testing Kalshi Integration")
    print("=" * 50)
    
    # Initialize client
    client = KalshiClient()
    
    # Test fetching NFL games
    print("\n[TEST] Fetching NFL games from Kalshi...")
    games = client.get_games('nfl')
    
    if games:
        print(f"[SUCCESS] Found {len(games)} NFL games")
        
        # Show first few games
        for i, game in enumerate(games[:3]):
            print(f"\nGame {i+1}:")
            print(f"  Teams: {game.away_team} @ {game.home_team}")
            print(f"  Time: {game.start_time}")
            print(f"  ID: {game.game_id}")
            
            # Show odds if available
            if game.odds:
                for odds_key, odds in game.odds.items():
                    if odds.bet_type.value == 'moneyline':
                        print(f"  Odds: {game.home_team} {odds.home_ml:+d}, {game.away_team} {odds.away_ml:+d}")
    else:
        print("[WARN] No games found - check API configuration")
    
    # Test other sports (should return empty)
    print("\n[TEST] Testing non-NFL sports...")
    mlb_games = client.get_games('mlb')
    print(f"MLB games: {len(mlb_games)} (expected: 0)")
    
    print("\n[DONE] Kalshi integration test completed")

if __name__ == "__main__":
    main()