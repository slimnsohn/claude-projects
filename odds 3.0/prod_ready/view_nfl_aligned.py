"""
View NFL Games with Both Pinnacle and Kalshi Lines
Shows games that are available on both platforms
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from core.main_system import MispricingSystem

def view_aligned_nfl():
    """Display NFL games with both Pinnacle and Kalshi odds"""
    print("=" * 60)
    print("NFL GAMES WITH BOTH PINNACLE & KALSHI LINES")
    print("=" * 60)
    
    try:
        # Initialize system
        system = MispricingSystem()
        
        # Run analysis to get aligned games
        result = system.run_analysis('nfl')
        
        if not result.get('status') == 'completed':
            print("Analysis failed:")
            for error in result.get('errors', []):
                print(f"  Error: {error.get('error')}")
            return
        
        aligned_games = result.get('aligned_games', [])
        opportunities = result.get('opportunities', [])
        
        print(f"Found {len(aligned_games)} aligned NFL games:\n")
        
        if len(aligned_games) == 0:
            print("No games found with both Pinnacle and Kalshi lines.")
            print("\nPinnacle games:", result.get('summary', {}).get('total_pinnacle_games', 0))
            print("Kalshi markets:", result.get('summary', {}).get('total_kalshi_games', 0))
            return
        
        for i, game in enumerate(aligned_games, 1):
            pinnacle = game['pinnacle_data']
            kalshi = game['kalshi_data']
            confidence = game.get('match_confidence', 0)
            
            print(f"{i}. {pinnacle['away_team']} @ {pinnacle['home_team']}")
            print(f"   Game Time: {pinnacle.get('game_time_display', 'Unknown')}")
            print(f"   Match Confidence: {confidence:.1%}")
            print()
            print("   PINNACLE ODDS:")
            print(f"     {pinnacle['home_team']}: {pinnacle['home_odds']['american']:+d}")
            print(f"     {pinnacle['away_team']}: {pinnacle['away_odds']['american']:+d}")
            print()
            print("   KALSHI ODDS:")
            print(f"     {kalshi['home_team']}: {kalshi['home_odds']['american']:+d}")
            print(f"     {kalshi['away_team']}: {kalshi['away_odds']['american']:+d}")
            print()
            print("-" * 40)
            print()
        
        # Show opportunities if any
        if opportunities:
            print("MISPRICING OPPORTUNITIES:")
            print("=" * 40)
            for i, opp in enumerate(opportunities, 1):
                discrepancy = opp['discrepancy']
                profit = opp['profit_analysis']
                game_data = opp['game_data']
                
                print(f"{i}. {game_data['pinnacle_data']['away_team']} @ {game_data['pinnacle_data']['home_team']}")
                print(f"   Recommended Side: {discrepancy['recommended_side']}")
                print(f"   Max Edge: {discrepancy['max_edge']:.1%}")
                print(f"   Expected Value: {profit['expected_value']:.1%}")
                print()
        else:
            print("No significant mispricing opportunities found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    view_aligned_nfl()