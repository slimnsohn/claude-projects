#!/usr/bin/env python3

"""
Test the fixed ticker-based extraction
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from kalshi.client import KalshiClient

def test_fixed_extraction():
    """Test the fixed extraction using the actual client"""
    
    print("Testing fixed WSU vs SDSU extraction...")
    
    client = KalshiClient()
    
    # Get just this one game
    games = client.get_games(league='ncaaf', remove_live_games=True)
    
    # Find WSU game
    for game in games:
        if ('Washington St.' in game.get('favorite', '') or 'Washington St.' in game.get('dog', '')) and \
           ('San Diego St.' in game.get('favorite', '') or 'San Diego St.' in game.get('dog', '')):
            
            print(f"FOUND WSU GAME:")
            print(f"  Favorite: {game['favorite']} ({game['fav_odds']})")
            print(f"  Dog: {game['dog']} ({game['dog_odds']})")
            
            # Convert back to cents
            def american_to_cents(odds):
                if odds < 0:
                    return abs(odds) / (abs(odds) + 100) * 100
                else:
                    return 100 / (odds + 100) * 100
            
            fav_cents = american_to_cents(game['fav_odds'])
            dog_cents = american_to_cents(game['dog_odds'])
            
            print(f"  In cents: {game['favorite']} ~{fav_cents:.0f}¢, {game['dog']} ~{dog_cents:.0f}¢")
            print(f"  Expected: Washington St. 53¢ (favorite), San Diego St. 48¢ (dog)")
            
            # Check if it matches
            wsu_cents = fav_cents if 'Washington' in game['favorite'] else dog_cents
            sdsu_cents = fav_cents if 'San Diego' in game['favorite'] else dog_cents
            
            print(f"  Actual: Washington St. {wsu_cents:.0f}¢, San Diego St. {sdsu_cents:.0f}¢")
            
            wsu_correct = abs(wsu_cents - 53) < 2
            sdsu_correct = abs(sdsu_cents - 48) < 2
            
            if wsu_correct and sdsu_correct:
                print(f"  ✅ CORRECT!")
            else:
                print(f"  ❌ STILL WRONG")
                
            break
    else:
        print("WSU game not found")

if __name__ == "__main__":
    test_fixed_extraction()