#!/usr/bin/env python3
"""
Sports Analytics Platform - Main Entry Point

This module demonstrates basic usage of the sports analytics platform,
including fetching games from multiple providers, comparing odds,
and finding arbitrage opportunities.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market_data.aggregator import MarketDataAggregator
from config.constants import Sport, BetType, Provider
from models import Game, Odds

def setup_logging():
    """Setup basic logging configuration"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def print_game_summary(game: Game):
    """Print a formatted summary of a game"""
    print(f"\n{'='*60}")
    print(f"GAME: {game.away_team} @ {game.home_team}")
    print(f"Start Time: {game.start_time.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"Time Until: {game.time_until_start()}")
    if game.venue:
        print(f"Venue: {game.venue}")
    
    # Show provider IDs
    if game.provider_ids:
        provider_info = ", ".join([f"{p.value}: {pid}" for p, pid in game.provider_ids.items()])
        print(f"Provider IDs: {provider_info}")
    
    print(f"Available Odds: {len(game.odds)} markets")

def print_odds_comparison(game: Game, aggregator: MarketDataAggregator):
    """Print odds comparison for different bet types"""
    print(f"\n--- ODDS COMPARISON for {game.away_team} @ {game.home_team} ---")
    
    # Moneyline odds
    ml_odds = aggregator.get_best_odds(game, BetType.MONEYLINE)
    if ml_odds:
        print(f"\nBest Moneyline Odds:")
        if 'home' in ml_odds:
            odds = ml_odds['home']
            print(f"  {game.home_team}: {odds.home_ml:+d} ({odds.provider.value})")
        if 'away' in ml_odds:
            odds = ml_odds['away']
            print(f"  {game.away_team}: {odds.away_ml:+d} ({odds.provider.value})")
    
    # Spread odds
    spread_odds = aggregator.get_best_odds(game, BetType.SPREAD)
    if spread_odds:
        print(f"\nBest Spread Odds:")
        for key, odds in spread_odds.items():
            if 'home' in key:
                print(f"  {game.home_team} {odds.spread_line:+.1f}: {odds.home_spread_odds:+d} ({odds.provider.value})")
            elif 'away' in key:
                print(f"  {game.away_team} {odds.spread_line:+.1f}: {odds.away_spread_odds:+d} ({odds.provider.value})")
    
    # Total odds
    total_odds = aggregator.get_best_odds(game, BetType.TOTAL)
    if total_odds:
        print(f"\nBest Total Odds:")
        for key, odds in total_odds.items():
            if 'over' in key:
                print(f"  Over {odds.total_line}: {odds.over_odds:+d} ({odds.provider.value})")
            elif 'under' in key:
                print(f"  Under {odds.total_line}: {odds.under_odds:+d} ({odds.provider.value})")

def find_and_print_arbitrage(game: Game, aggregator: MarketDataAggregator):
    """Find and print arbitrage opportunities"""
    arb_ml = aggregator.find_arbitrage_opportunities(game, BetType.MONEYLINE)
    
    if arb_ml:
        print(f"\n[TARGET] ARBITRAGE OPPORTUNITY FOUND! [TARGET]")
        print(f"Game: {game.away_team} @ {game.home_team}")
        print(f"Profit Margin: {arb_ml['profit_margin']:.2%}")
        print(f"Total Probability: {arb_ml['total_probability']:.4f}")
        
        print(f"\nBet Distribution:")
        home_bet = arb_ml['home_bet']
        away_bet = arb_ml['away_bet']
        
        print(f"  {game.home_team}: {home_bet['stake_percentage']:.1%} on {home_bet['provider'].value} at {home_bet['odds']:+d}")
        print(f"  {game.away_team}: {away_bet['stake_percentage']:.1%} on {away_bet['provider'].value} at {away_bet['odds']:+d}")
        
        return True
    
    return False

def demo_basic_usage():
    """Demonstrate basic platform usage"""
    
    ################## CONFIGURATION SECTION - UPDATE THESE ##################
    
    # Primary Configuration
    SPORT = Sport.NFL            # Options: Sport.NFL, Sport.MLB, Sport.NBA, Sport.NHL
    MAX_DISPLAY_GAMES = 3        # Limit number of games shown (0 = show all games)
    DAYS_AHEAD_FILTER = 7        # Only show games within next N days (0 = no filter)
    
    # Display Options
    SHOW_ARBITRAGE = True        # Look for arbitrage opportunities
    SHOW_ODDS_COMPARISON = True  # Show detailed odds comparison
    VERBOSE = True               # Show detailed game summaries
    
    #######################################################################
    
    print(f"[{SPORT.value.upper()}] Sports Analytics Platform Demo")
    print("=" * 50)
    
    # Initialize aggregator
    print("\n[DATA] Initializing market data aggregator...")
    aggregator = MarketDataAggregator()
    
    # Check provider status
    status = aggregator.get_provider_status()
    print(f"\nProvider Status:")
    for provider, stat in status.items():
        print(f"  {provider.value}: {stat}")
    
    # Fetch games
    print(f"\n[{SPORT.value.upper()}] Fetching {SPORT.value.upper()} games...")
    try:
        all_games = aggregator.get_all_games(SPORT)
        
        if not all_games:
            print("[ERR] No games found. This might be due to:")
            print("  - Missing API keys in environment variables")
            print("  - No games scheduled")
            print("  - API connection issues")
            return
        
        print(f"[OK] Found {len(all_games)} total {SPORT.value.upper()} games")
        
        # Apply time filter if specified
        if DAYS_AHEAD_FILTER > 0:
            now = datetime.now()
            cutoff = now + timedelta(days=DAYS_AHEAD_FILTER)
            
            games = []
            for game in all_games:
                game_time = game.start_time
                # Handle timezone-aware comparison
                if game_time.tzinfo is not None:
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                    cutoff = now + timedelta(days=DAYS_AHEAD_FILTER)
                
                if game_time <= cutoff:
                    games.append(game)
            
            print(f"[FILTER] After {DAYS_AHEAD_FILTER}-day filter: {len(games)} games")
        else:
            games = all_games
            print("[FILTER] No time filter applied")
        
        # Determine how many games to display
        if MAX_DISPLAY_GAMES == 0:
            display_games = games  # Show all games
            print(f"[DISPLAY] Showing all {len(games)} games")
        else:
            display_games = games[:MAX_DISPLAY_GAMES]  # Show limited games
            print(f"[DISPLAY] Showing first {len(display_games)} of {len(games)} games")
        
        # Show games with details
        for i, game in enumerate(display_games):
            if VERBOSE:
                print_game_summary(game)
            
            if game.odds:
                if SHOW_ODDS_COMPARISON:
                    print_odds_comparison(game, aggregator)
                
                # Look for arbitrage opportunities
                if SHOW_ARBITRAGE:
                    found_arb = find_and_print_arbitrage(game, aggregator)
                    
                    if not found_arb:
                        print("\n[MONEY] No arbitrage opportunities found for this game")
            elif VERBOSE:
                print(f"[WARN] No odds available for {game.away_team} @ {game.home_team}")
        
        # Summary statistics
        print(f"\n[STATS] SUMMARY STATISTICS")
        print(f"Total Games Found: {len(all_games)}")
        print(f"Filtered Games: {len(games)}")
        print(f"Displayed Games: {len(display_games)}")
        
        games_with_odds = sum(1 for g in games if g.odds)
        print(f"Games with Odds: {games_with_odds}")
        
        total_markets = sum(len(g.odds) for g in games)
        print(f"Total Markets: {total_markets}")
        
        if games_with_odds > 0:
            avg_markets = total_markets / games_with_odds
            print(f"Average Markets per Game: {avg_markets:.1f}")
        
    except Exception as e:
        print(f"[ERR] Error fetching games: {e}")
        print("\nTroubleshooting:")
        print("1. Check that ODDS_API_KEY is set in your environment")
        print("2. Verify your API key is valid and has remaining quota")
        print("3. Check your internet connection")

def demo_single_provider():
    """Demonstrate fetching from a single provider"""
    print("\n[SEARCH] Single Provider Demo (Odds API only)")
    print("=" * 40)
    
    aggregator = MarketDataAggregator()
    
    try:
        # Fetch only from Odds API
        odds_api_games = aggregator.get_games_by_provider(Sport.NFL, Provider.ODDS_API)
        
        if odds_api_games:
            print(f"Found {len(odds_api_games)} games from Odds API")
            
            # Show first game
            game = odds_api_games[0]
            print_game_summary(game)
            
            # Show all odds for this game
            if game.odds:
                print(f"\nAll available odds:")
                for odds_key, odds in game.odds.items():
                    print(f"  {odds}")
        
        else:
            print("No games found from Odds API")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main entry point"""
    setup_logging()
    
    print("[START] Starting Sports Analytics Platform")
    print("=" * 50)
    
    # Check for required API keys using our config system
    from config.settings import ODDS_API_KEY
    
    if not ODDS_API_KEY:
        print("[ERR] Missing required API key: ODDS_API_KEY")
        print("\nPlease either:")
        print("1. Add your API key to config/odds_api_key.txt")
        print("2. Set ODDS_API_KEY environment variable")
        print("\nExample file format: api_key = 'your_key_here'")
        return 1
    else:
        print(f"[OK] API key loaded: {ODDS_API_KEY[:10]}...")
    
    try:
        # Run basic demo
        demo_basic_usage()
        
        # Uncomment to run single provider demo
        # demo_single_provider()
        
        print(f"\n[OK] Demo completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n[STOP]  Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n[ERR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)