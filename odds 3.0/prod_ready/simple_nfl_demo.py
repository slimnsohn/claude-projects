"""
Simple NFL Demo - All-in-One Script
Demonstrates core NFL functionality: Pinnacle, Kalshi, and Aligned Games
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from core.pinnacle_client import PinnacleClient
from core.kalshi_client import KalshiClientUpdated as KalshiClient
from core.main_system import MispricingSystem

def main():
    """Run complete NFL demo"""
    print("=" * 70)
    print("NFL ODDS COMPARISON SYSTEM - SIMPLE DEMO")
    print("=" * 70)
    print()
    
    try:
        # 1. Show Pinnacle NFL Games
        print("1. PINNACLE NFL GAMES")
        print("-" * 30)
        pinnacle_client = PinnacleClient("keys/odds_api_key.txt")
        pinnacle_result = pinnacle_client.get_sports_odds('nfl')
        
        if pinnacle_result.get('success'):
            games = pinnacle_result.get('data', [])
            print(f"Found {len(games)} Pinnacle NFL games")
            
            for i, game in enumerate(games[:3], 1):  # Show first 3
                home_team = game.get('home_team')
                away_team = game.get('away_team')
                
                print(f"  {i}. {away_team} @ {home_team}")
                
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
                                        print(f"     {home_team}: {odds:+d}")
                                    elif team == away_team:
                                        print(f"     {away_team}: {odds:+d}")
            
            if len(games) > 3:
                print(f"  ... and {len(games) - 3} more games")
        else:
            print(f"  Error: {pinnacle_result.get('error')}")
        
        print()
        
        # 2. Show Kalshi NFL Markets
        print("2. KALSHI NFL MARKETS")
        print("-" * 30)
        kalshi_client = KalshiClient("keys/kalshi_credentials.txt")
        kalshi_result = kalshi_client.search_sports_markets('nfl')
        
        if kalshi_result.get('success'):
            markets = kalshi_result.get('data', [])
            print(f"Found {len(markets)} Kalshi NFL markets")
            
            for i, market in enumerate(markets[:3], 1):  # Show first 3
                title = market.get('title')
                ticker = market.get('ticker')
                yes_bid = market.get('yes_bid', 0)
                no_bid = market.get('no_bid', 0)
                
                print(f"  {i}. {title}")
                print(f"     Ticker: {ticker}")
                if yes_bid or no_bid:
                    print(f"     Pricing: YES {yes_bid}% / NO {no_bid}%")
                
            if len(markets) > 3:
                print(f"  ... and {len(markets) - 3} more markets")
        else:
            print(f"  Error: {kalshi_result.get('error')}")
        
        print()
        
        # 3. Show Aligned Games (games with both lines)
        print("3. ALIGNED GAMES (Both Pinnacle & Kalshi)")
        print("-" * 50)
        system = MispricingSystem()
        analysis_result = system.run_analysis('nfl')
        
        if analysis_result.get('status') == 'completed':
            aligned_games = analysis_result.get('aligned_games', [])
            opportunities = analysis_result.get('opportunities', [])
            summary = analysis_result.get('summary', {})
            
            print(f"Summary:")
            print(f"  Pinnacle Games: {summary.get('total_pinnacle_games', 0)}")
            print(f"  Kalshi Markets: {summary.get('total_kalshi_games', 0)}")
            print(f"  Aligned Games: {summary.get('successfully_aligned', 0)}")
            print(f"  Opportunities: {summary.get('opportunities_found', 0)}")
            print()
            
            if aligned_games:
                print("Games with both Pinnacle and Kalshi lines:")
                for i, game in enumerate(aligned_games, 1):
                    pinnacle = game['pinnacle_data']
                    kalshi = game['kalshi_data']
                    confidence = game.get('match_confidence', 0)
                    
                    print(f"  {i}. {pinnacle['away_team']} @ {pinnacle['home_team']}")
                    print(f"     Match Confidence: {confidence:.1%}")
                    print(f"     Pinnacle: {pinnacle['home_team']} {pinnacle['home_odds']['american']:+d}, {pinnacle['away_team']} {pinnacle['away_odds']['american']:+d}")
                    print(f"     Kalshi: {kalshi['home_team']} {kalshi['home_odds']['american']:+d}, {kalshi['away_team']} {kalshi['away_odds']['american']:+d}")
                    print()
                
                if opportunities:
                    print("MISPRICING OPPORTUNITIES:")
                    for i, opp in enumerate(opportunities, 1):
                        discrepancy = opp['discrepancy']
                        game_data = opp['game_data']
                        
                        print(f"  {i}. {game_data['pinnacle_data']['away_team']} @ {game_data['pinnacle_data']['home_team']}")
                        print(f"     Recommended Side: {discrepancy['recommended_side']}")
                        print(f"     Max Edge: {discrepancy['max_edge']:.1%}")
                        print()
            else:
                print("No games found with both Pinnacle and Kalshi lines.")
                print("This could mean:")
                print("  - NFL season is not currently active")
                print("  - No matching games between platforms today")
                print("  - Different game scheduling between platforms")
        else:
            print("Analysis failed:")
            for error in analysis_result.get('errors', []):
                print(f"  Error: {error.get('error')}")
        
        print()
        print("=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()