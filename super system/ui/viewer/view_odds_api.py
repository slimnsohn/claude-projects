#!/usr/bin/env python3
"""
Odds API Viewer - Display odds data in DataFrame format
Simple viewer for examining odds from The Odds API
"""

import sys
import os
from datetime import datetime, timezone
import pandas as pd
import pytz

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from market_data.odds_api.production.client import OddsAPIClient
from config.constants import Sport, BetType, Provider

def main():
    """Main function to display odds data"""
    
    ################## CONFIGURATION SECTION - UPDATE THESE ##################
    
    # Primary Configuration
    LEAGUE = 'nfl'              # Options: 'mlb', 'nfl', 'nba', 'nhl'
    MARKET_TYPE = 'ml'          # Options: 'ml' (moneyline), 'sp' (spreads), 'ou' (over/under)
    
    # Display Options
    MAX_DISPLAY_GAMES = 30       # Limit number of games shown (0 = show all games)
    VERBOSE = True              # Show detailed game-by-game breakdown
    
    # Filter Options  
    DAYS_AHEAD_WINDOW = 7       # Only show games within next N days (0 = no filter)
    EXCLUDE_LIVE_GAMES = True   # Skip games that have already started
    USE_ALL_BOOKS = False       # Use all available books vs selected subset
    
    # Book Selection (when USE_ALL_BOOKS = False)
    PREFERRED_BOOKS = [
        'fanduel', 'betonlineag', 'pinnacle'
    ]
    
    # Available Books - Use these exact names in PREFERRED_BOOKS array:
    # 'draftkings', 'fanduel', 'betmgm', 'caesars', 'williamhill_us', 
    # 'bovada', 'betrivers', 'betonlineag', 'betus', 'mybookieag', 
    # 'lowvig', 'pointsbetus', 'twinspires', 'circasports', 'barstool', 
    # 'wynnbet', 'superbook', 'unibet_us', 'betway', 'betfred', 
    # 'betparx', 'sugarhouse', 'foxbet', 'tipico_us', 'sisportsbook', 
    # 'intertops', 'betfair_ex_us', 'pinnacle', 'draftings'
    
    #######################################################################
    
    print(f"Odds API Viewer - {LEAGUE.upper()} {MARKET_TYPE.upper()} Markets")
    print("=" * 60)
    
    try:
        # Initialize client
        client = OddsAPIClient()
        print(f"[OK] Connected to Odds API")
        
        # Fetch games
        print(f"[INFO] Fetching {LEAGUE} games...")
        games = client.get_games(LEAGUE)
        
        if not games:
            print(f"[WARN] No games found for {LEAGUE}")
            return
        
        print(f"[INFO] Processing {len(games)} games...")
        
        # Convert to DataFrame format
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
            
            # Process each bookmaker's odds for this game
            for odds_key, odds in game.odds.items():
                # Filter by market type
                if MARKET_TYPE == 'ml' and odds.bet_type != BetType.MONEYLINE:
                    continue
                elif MARKET_TYPE == 'sp' and odds.bet_type != BetType.SPREAD:
                    continue
                elif MARKET_TYPE == 'ou' and odds.bet_type != BetType.TOTAL:
                    continue
                
                if MARKET_TYPE == 'ml' and odds.bet_type == BetType.MONEYLINE:
                    # Determine favorite and underdog
                    if odds.home_ml and odds.away_ml:
                        if abs(odds.home_ml) > abs(odds.away_ml):
                            # Away team is favored (smaller absolute value = favorite)
                            fav_team = game.away_team
                            dog_team = game.home_team
                            fav_odds = odds.away_ml
                            dog_odds = odds.home_ml
                        else:
                            # Home team is favored
                            fav_team = game.home_team
                            dog_team = game.away_team
                            fav_odds = odds.home_ml
                            dog_odds = odds.away_ml
                        
                        # Extract bookmaker name from odds_key
                        bookmaker = odds.bookmaker if odds.bookmaker else odds_key.split('_')[-1]
                        
                        rows.append({
                            'book': bookmaker,
                            'teams': f"{game.away_team} @ {game.home_team}",
                            'fav_team': fav_team,
                            'dog_team': dog_team,
                            'fav_odds': fav_odds,
                            'dog_odds': dog_odds,
                            'league': LEAGUE,
                            'bet_type': 'ml',
                            'game_time': game_time_str,
                            'game_date': game_date_str
                        })
                
                elif MARKET_TYPE == 'sp' and odds.bet_type == BetType.SPREAD:
                    if odds.spread_line and odds.home_spread_odds and odds.away_spread_odds:
                        # Determine which team is favored by the spread
                        if odds.spread_line > 0:
                            # Home team favored
                            fav_team = game.home_team
                            dog_team = game.away_team
                            fav_odds = odds.home_spread_odds
                            dog_odds = odds.away_spread_odds
                            spread_text = f"{fav_team} -{odds.spread_line}"
                        else:
                            # Away team favored
                            fav_team = game.away_team
                            dog_team = game.home_team
                            fav_odds = odds.away_spread_odds
                            dog_odds = odds.home_spread_odds
                            spread_text = f"{fav_team} {odds.spread_line}"
                        
                        bookmaker = odds.bookmaker if odds.bookmaker else odds_key.split('_')[-1]
                        
                        rows.append({
                            'book': bookmaker,
                            'teams': f"{game.away_team} @ {game.home_team}",
                            'spread': spread_text,
                            'fav_team': fav_team,
                            'dog_team': dog_team,
                            'fav_odds': fav_odds,
                            'dog_odds': dog_odds,
                            'league': LEAGUE,
                            'bet_type': 'sp',
                            'game_time': game_time_str,
                            'game_date': game_date_str
                        })
                
                elif MARKET_TYPE == 'ou' and odds.bet_type == BetType.TOTAL:
                    if odds.total_line and odds.over_odds and odds.under_odds:
                        bookmaker = odds.bookmaker if odds.bookmaker else odds_key.split('_')[-1]
                        
                        rows.append({
                            'book': bookmaker,
                            'teams': f"{game.away_team} @ {game.home_team}",
                            'total': odds.total_line,
                            'over_odds': odds.over_odds,
                            'under_odds': odds.under_odds,
                            'league': LEAGUE,
                            'bet_type': 'ou',
                            'game_time': game_time_str,
                            'game_date': game_date_str
                        })
        
        if not rows:
            print(f"[WARN] No {MARKET_TYPE.upper()} odds found for {LEAGUE.upper()}")
            return
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Show all available books for debugging
        available_books = sorted(df['book'].unique())
        print(f"[DEBUG] All available books in current data ({len(available_books)} total):")
        for i, book in enumerate(available_books):
            if i % 6 == 0:
                print()  # New line every 6 books
            print(f"  '{book}'", end="")
        print()  # Final newline
        
        # Apply book filter if specified
        if not USE_ALL_BOOKS and PREFERRED_BOOKS:
            original_count = len(df)
            print(f"\n[DEBUG] Preferred books configured: {PREFERRED_BOOKS}")
            
            # Show which preferred books are found/missing
            found_books = [book for book in PREFERRED_BOOKS if book in available_books]
            missing_books = [book for book in PREFERRED_BOOKS if book not in available_books]
            
            if found_books:
                print(f"[DEBUG] Found preferred books: {found_books}")
            if missing_books:
                print(f"[DEBUG] Missing preferred books: {missing_books}")
            
            df = df[df['book'].isin(PREFERRED_BOOKS)].copy()
            print(f"[FILTER] Applied book filter: {len(df)} markets (from {original_count}) using {len(found_books)}/{len(PREFERRED_BOOKS)} preferred books")
        
        # Apply date filter if specified
        if DAYS_AHEAD_WINDOW > 0:
            from datetime import datetime, timedelta
            # Use Central Time for date filtering consistency
            central_tz = pytz.timezone('US/Central')
            today_central = datetime.now(central_tz)
            cutoff_date_central = today_central + timedelta(days=DAYS_AHEAD_WINDOW)
            
            # Convert dates to comparable format (YYYYMMDD as integers)
            today_int = int(today_central.strftime('%Y%m%d'))
            cutoff_int = int(cutoff_date_central.strftime('%Y%m%d'))
            
            # Filter DataFrame based on game_date column
            original_count = len(df)
            df['game_date_int'] = df['game_date'].astype(int)
            df = df[df['game_date_int'] <= cutoff_int].copy()
            df = df.drop('game_date_int', axis=1)  # Remove temporary column
            
            print(f"[FILTER] Applied {DAYS_AHEAD_WINDOW}-day filter: {len(df)} markets (from {original_count})")
        
        # Sort by game time, then by book
        df = df.sort_values(['game_time', 'book']).reset_index(drop=True)
        
        print(f"\n[SUCCESS] Found {len(df)} {MARKET_TYPE.upper()} markets")
        print("=" * 60)
        
        # Group by game and display
        displayed_games = 0
        
        if MARKET_TYPE == 'ml':
            for game_key, group in df.groupby(['teams', 'game_time']):
                if MAX_DISPLAY_GAMES > 0 and displayed_games >= MAX_DISPLAY_GAMES:
                    break
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'fav_team', 'dog_team', 'fav_odds', 'dog_odds', 'league', 'bet_type', 'game_time', 'game_date']
                group_reset = group[display_cols].reset_index(drop=True)
                print(group_reset.to_string(index=True))
                displayed_games += 1
        
        elif MARKET_TYPE == 'sp':
            for game_key, group in df.groupby(['teams', 'game_time']):
                if MAX_DISPLAY_GAMES > 0 and displayed_games >= MAX_DISPLAY_GAMES:
                    break
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'spread', 'fav_team', 'dog_team', 'fav_odds', 'dog_odds', 'league', 'bet_type', 'game_time', 'game_date']
                group_reset = group[display_cols].reset_index(drop=True)
                print(group_reset.to_string(index=True))
                displayed_games += 1
        
        elif MARKET_TYPE == 'ou':
            for game_key, group in df.groupby(['teams', 'game_time']):
                if MAX_DISPLAY_GAMES > 0 and displayed_games >= MAX_DISPLAY_GAMES:
                    break
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'total', 'over_odds', 'under_odds', 'league', 'bet_type', 'game_time', 'game_date']
                group_reset = group[display_cols].reset_index(drop=True)
                print(group_reset.to_string(index=True))
                displayed_games += 1
        
        # Summary stats
        print(f"\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"Total Markets: {len(df)}")
        print(f"Unique Games: {len(df.groupby('teams'))}")
        print(f"Unique Books: {len(df['book'].unique())}")
        if 'book' in df.columns:
            print(f"Books: {', '.join(sorted(df['book'].unique()))}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()