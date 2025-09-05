#!/usr/bin/env python3
"""
Kalshi Viewer - Display Kalshi market data in DataFrame format
Simple viewer for examining prediction markets from Kalshi
"""

import sys
import os
from datetime import datetime, timezone
import pandas as pd
import pytz

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from market_data.kalshi.production.client import KalshiClient
from config.constants import Sport, BetType, Provider

def main():
    """Main function to display Kalshi market data"""
    
    ################## CONFIGURATION SECTION - UPDATE THESE ##################
    
    # Primary Configuration
    LEAGUE = 'nfl'              # Options: 'nfl', 'mlb', 'nba', 'nhl'
    MARKET_TYPE = 'ml'          # Options: 'ml' (moneyline), 'sp' (spreads), 'ou' (over/under)
    
    # Display Options
    MAX_DISPLAY_GAMES = 5       # Limit number of games shown (0 = show all games)
    VERBOSE = True              # Show detailed game-by-game breakdown
    
    # Filter Options  
    DAYS_AHEAD_WINDOW = 7       # Only show games within next N days (0 = no filter)
    EXCLUDE_LIVE_GAMES = False  # Skip games that have already started
    SHOW_SAMPLE_DATA = True     # Show sample data when client not implemented
    
    # Kalshi-Specific Options
    MIN_PRICE_THRESHOLD = 10    # Minimum price percentage to show
    MAX_PRICE_THRESHOLD = 90    # Maximum price percentage to show
    
    #######################################################################
    
    print(f"Kalshi Viewer - {LEAGUE.upper()} {MARKET_TYPE.upper()} Markets")
    print("=" * 60)
    
    try:
        # Initialize client
        client = KalshiClient()
        print(f"[OK] Connected to Kalshi")
        
        # Fetch games
        print(f"[INFO] Fetching {LEAGUE} markets from Kalshi...")
        games = client.get_games(LEAGUE)
        
        if not games:
            print(f"[WARN] No markets found for {LEAGUE}")
            if LEAGUE.lower() != 'nfl':
                print(f"[INFO] Note: Kalshi currently only supports NFL games")
            return
        
        # Convert to DataFrame format (when implemented)
        rows = []
        
        # Set up Central Time zone
        central_tz = pytz.timezone('US/Central')
        
        for game in games:
            # Convert game time to Central Time
            game_time_central = game.start_time
            if game_time_central.tzinfo is None:
                # If naive datetime, assume UTC
                game_time_central = pytz.utc.localize(game_time_central)
            
            # Convert to Central Time
            game_time_central = game_time_central.astimezone(central_tz)
            
            game_time_str = game_time_central.strftime('%a_%H:%M').upper()
            game_date_str = game_time_central.strftime('%Y%m%d')
            
            # Process Kalshi market data
            for odds_key, odds in game.odds.items():
                # Filter by market type
                if MARKET_TYPE == 'ml' and odds.bet_type != BetType.MONEYLINE:
                    continue
                elif MARKET_TYPE == 'sp' and odds.bet_type != BetType.SPREAD:
                    continue
                elif MARKET_TYPE == 'ou' and odds.bet_type != BetType.TOTAL:
                    continue
                
                if MARKET_TYPE == 'ml' and odds.bet_type == BetType.MONEYLINE:
                    # Kalshi returns American odds format now after conversion
                    if odds.home_ml and odds.away_ml:
                        # Determine favorite (more negative number)
                        if odds.home_ml < odds.away_ml:
                            fav_team = game.home_team
                            dog_team = game.away_team
                            fav_odds = odds.home_ml
                            dog_odds = odds.away_ml
                        else:
                            fav_team = game.away_team
                            dog_team = game.home_team
                            fav_odds = odds.away_ml
                            dog_odds = odds.home_ml
                        
                        rows.append({
                            'book': 'kalshi',
                            'teams': f"{game.away_team} @ {game.home_team}",
                            'fav_team': fav_team,
                            'dog_team': dog_team,
                            'fav_odds': fav_odds,
                            'dog_odds': dog_odds,
                            'league': LEAGUE.lower(),
                            'bet_type': 'ml',
                            'game_time': game_time_str,
                            'game_date': game_date_str
                        })
        
        if not rows:
            print(f"[WARN] No {MARKET_TYPE.upper()} markets found for {LEAGUE.upper()}")
            return
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Sort by game time
        df = df.sort_values(['game_time']).reset_index(drop=True)
        
        print(f"\n[SUCCESS] Found {len(df)} {MARKET_TYPE.upper()} markets")
        print("=" * 60)
        
        # Group by game and display
        if MARKET_TYPE == 'ml':
            for game_key, group in df.groupby(['teams', 'game_time']):
                print(f"\nTeams: {game_key[0]} | Time: {game_key[1]}")
                display_cols = ['book', 'teams', 'fav_team', 'dog_team', 'fav_odds', 'dog_odds', 'league', 'bet_type', 'game_time', 'game_date']
                print(group[display_cols].to_string(index=True))
        
        # Summary stats
        print(f"\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"Total Markets: {len(df)}")
        print(f"Unique Games: {len(df.groupby('teams'))}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()