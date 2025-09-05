#!/usr/bin/env python3

"""
Test just the WSU vs SDSU game to see the exact odds
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from kalshi.client import KalshiClient

def test_wsu_game():
    """Test just the WSU game"""
    
    print("Testing WSU vs SDSU specifically...")
    
    client = KalshiClient()
    games = client.get_games(league='ncaaf', remove_live_games=True)
    
    # Find the WSU game
    wsu_game = None
    for game in games:
        if 'Washington St.' in game.get('favorite', '') or 'Washington St.' in game.get('dog', ''):
            if 'San Diego St.' in game.get('favorite', '') or 'San Diego St.' in game.get('dog', ''):
                wsu_game = game
                break
    
    if wsu_game:
        print(f"Found WSU game:")
        print(f"  Favorite: {wsu_game['favorite']} ({wsu_game['fav_odds']})")
        print(f"  Dog: {wsu_game['dog']} ({wsu_game['dog_odds']})")
        print(f"  Date: {wsu_game['game_date']}")
        
        # Convert odds back to cents for verification
        def american_to_cents_approx(odds):
            if odds < 0:
                return abs(odds) / (abs(odds) + 100) * 100
            else:
                return 100 / (odds + 100) * 100
                
        fav_cents = american_to_cents_approx(wsu_game['fav_odds'])
        dog_cents = american_to_cents_approx(wsu_game['dog_odds'])
        
        print(f"  Approximate cents: {wsu_game['favorite']} ~{fav_cents:.0f}¢, {wsu_game['dog']} ~{dog_cents:.0f}¢")
        
        # Expected from Kalshi web: WSU 53¢, SDSU 48¢
        print(f"  Expected from web: Washington St. 53¢, San Diego St. 48¢")
        
    else:
        print("WSU vs SDSU game not found")
        
        # Show all Washington St games
        print("\nAll Washington St games:")
        for game in games:
            if 'Washington' in game.get('favorite', '') or 'Washington' in game.get('dog', ''):
                print(f"  {game['favorite']} vs {game['dog']}")

if __name__ == "__main__":
    test_wsu_game()