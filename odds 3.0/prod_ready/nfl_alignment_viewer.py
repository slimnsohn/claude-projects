"""
NFL Game Alignment Viewer - Shows games matched between Pinnacle and Kalshi
Uses improved team name standardization for better matching
"""

from slim_game_viewer_fixed import SlimPinnacleClient, SlimKalshiClient
from improved_game_aligner import ImprovedGameAligner
from datetime import datetime

def view_aligned_nfl():
    """Display NFL games aligned between Pinnacle and Kalshi"""
    print("=" * 80)
    print("NFL GAME ALIGNMENT - PINNACLE vs KALSHI")
    print("=" * 80)
    
    try:
        # Initialize clients
        print("Fetching data from both platforms...")
        pinnacle = SlimPinnacleClient()
        kalshi = SlimKalshiClient()
        
        # Get game data
        print("Getting Pinnacle NFL games...")
        pin_games = pinnacle.get_games('nfl')
        print(f"Found {len(pin_games)} Pinnacle games")
        
        print("Getting Kalshi NFL games...")
        kal_games = kalshi.get_games('nfl') 
        print(f"Found {len(kal_games)} Kalshi games")
        
        if not pin_games:
            print("No Pinnacle games found!")
            return
            
        if not kal_games:
            print("No Kalshi games found!")
            return
        
        # Use improved alignment
        aligner = ImprovedGameAligner(time_threshold_hours=168)  # 7 days
        aligned_games = aligner.align_games(pin_games, kal_games)
        
        print("\\n" + "=" * 80)
        print(f"ALIGNMENT RESULTS: {len(aligned_games)} MATCHED GAMES")
        print("=" * 80)
        
        if not aligned_games:
            print("\\nNO GAMES COULD BE ALIGNED!")
            print("\\nThis might be due to:")
            print("- Different time periods (Pinnacle shows current season, Kalshi shows future)")
            print("- Team name mismatches")
            print("- No overlapping games between platforms")
            
            print("\\nPinnacle sample games:")
            for i, game in enumerate(pin_games[:3], 1):
                print(f"  {i}. {game['away']} @ {game['home']} ({game['game_time']})")
                
            print("\\nKalshi sample games:")
            for i, game in enumerate(kal_games[:3], 1):
                print(f"  {i}. {game['away']} @ {game['home']} ({game['game_time']})")
            
            return
        
        # Display aligned games
        for i, aligned in enumerate(aligned_games, 1):
            pin_game = aligned['pinnacle_data']
            kal_game = aligned['kalshi_data']
            confidence = aligned['match_confidence']
            reason = aligned['match_reason']
            
            print(f"\\n{i}. MATCH #{aligned['match_id']} (Confidence: {confidence:.1%})")
            print(f"   Reason: {reason}")
            print("-" * 40)
            
            print("PINNACLE:")
            print(f"  {pin_game['away']} @ {pin_game['home']}")
            print(f"  Game Time: {pin_game.get('game_time', 'Unknown')}")
            if pin_game.get('away_odds') and pin_game.get('home_odds'):
                print(f"  Odds: {pin_game['away']} {pin_game['away_odds']:+d}, {pin_game['home']} {pin_game['home_odds']:+d}")
            
            print("\\nKALSHI:")
            print(f"  {kal_game['away']} @ {kal_game['home']}")
            print(f"  Game Time: {kal_game.get('game_time', 'Unknown')}")
            if kal_game.get('away_odds') and kal_game.get('home_odds'):
                print(f"  Odds: {kal_game['away']} {kal_game['away_odds']:+d}, {kal_game['home']} {kal_game['home_odds']:+d}")
            
            # Show team code mapping
            if 'team_codes' in aligned:
                codes = aligned['team_codes']
                print("\\nTEAM MAPPING:")
                print(f"  Pinnacle: {codes['pinnacle_away']}-{codes['pinnacle_home']}")
                print(f"  Kalshi:   {codes['kalshi_away']}-{codes['kalshi_home']}")
            
            if i >= 10:  # Limit display to first 10
                remaining = len(aligned_games) - i
                if remaining > 0:
                    print(f"\\n... and {remaining} more aligned games")
                break
        
        # Summary
        print("\\n" + "=" * 80)
        print("SUMMARY:")
        print(f"  Pinnacle games: {len(pin_games)}")
        print(f"  Kalshi games: {len(kal_games)}")
        print(f"  Successfully aligned: {len(aligned_games)} ({len(aligned_games)/len(pin_games)*100:.1f}% of Pinnacle games)")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    view_aligned_nfl()