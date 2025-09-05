#!/usr/bin/env python3
"""
Aggregated Viewer - Display odds data from all providers in DataFrame format
Combines data from multiple sources for comparison
"""

import sys
import os
from datetime import datetime, timezone
import pandas as pd
import pytz

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from market_data.aggregator import MarketDataAggregator
from config.constants import Sport, BetType, Provider

def main():
    """Main function to display aggregated odds data"""
    
    ################## CONFIGURATION SECTION - UPDATE THESE ##################
    
    # Primary Configuration
    LEAGUE = 'mlb'              # Options: 'mlb', 'nfl', 'nba', 'nhl'
    MARKET_TYPE = 'ml'          # Options: 'ml' (moneyline), 'sp' (spreads), 'ou' (over/under)
    
    # Display Options
    MAX_DISPLAY_GAMES = 5       # Limit number of games shown (0 = show all games)
    VERBOSE = True              # Show detailed game-by-game breakdown
    SHOW_BEST_ODDS = True       # Display best odds summary at the end
    
    # Filter Options  
    DAYS_AHEAD_WINDOW = 7       # Only show games within next N days (0 = no filter)
    EXCLUDE_LIVE_GAMES = False  # Skip games that have already started
    PROVIDER_FILTER = []        # Filter by specific providers (empty = all providers)
    
    # Aggregation Options
    COMPARE_PROVIDERS = True    # Show provider comparison in output
    HIGHLIGHT_ARBITRAGE = True  # Highlight potential arbitrage opportunities
    MIN_PROVIDER_COUNT = 2      # Minimum providers required to show game
    
    #######################################################################
    
    print(f"Aggregated Viewer - {LEAGUE.upper()} {MARKET_TYPE.upper()} Markets")
    print("=" * 60)
    
    try:
        # Initialize aggregator
        aggregator = MarketDataAggregator()
        
        # Check provider status
        status = aggregator.get_provider_status()
        active_providers = [p.value for p, s in status.items() if s == "active"]
        print(f"[INFO] Active providers: {', '.join(active_providers)}")
        
        # Fetch games
        print(f"[INFO] Fetching {LEAGUE} games from all providers...")
        
        # Convert league string to Sport enum
        sport_map = {'nfl': Sport.NFL, 'mlb': Sport.MLB, 'nba': Sport.NBA, 'nhl': Sport.NHL}
        sport = sport_map.get(LEAGUE.lower(), Sport.NFL)
        
        games = aggregator.get_all_games(sport)
        
        if not games:
            print(f"[WARN] No games found for {LEAGUE}")
            return
        
        print(f"[INFO] Processing {len(games)} games (showing first {MAX_DISPLAY_GAMES})...")
        
        # Convert to DataFrame format
        rows = []
        bet_type_map = {'ml': BetType.MONEYLINE, 'sp': BetType.SPREAD, 'ou': BetType.TOTAL}
        target_bet_type = bet_type_map.get(MARKET_TYPE.lower(), BetType.MONEYLINE)
        
        # Set up Central Time zone
        central_tz = pytz.timezone('US/Central')
        
        for game_idx, game in enumerate(games[:MAX_DISPLAY_GAMES]):
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
                if odds.bet_type != target_bet_type:
                    continue
                
                if MARKET_TYPE == 'ml' and odds.bet_type == BetType.MONEYLINE:
                    # Determine favorite and underdog
                    if odds.home_ml and odds.away_ml:
                        # For American odds: more negative = favorite
                        if odds.home_ml < 0 and odds.away_ml > 0:
                            # Home favored
                            fav_team = game.home_team
                            dog_team = game.away_team
                            fav_odds = odds.home_ml
                            dog_odds = odds.away_ml
                        elif odds.away_ml < 0 and odds.home_ml > 0:
                            # Away favored  
                            fav_team = game.away_team
                            dog_team = game.home_team
                            fav_odds = odds.away_ml
                            dog_odds = odds.home_ml
                        else:
                            # Both negative or both positive - pick smaller absolute value as favorite
                            if abs(odds.home_ml) < abs(odds.away_ml):
                                fav_team = game.home_team
                                dog_team = game.away_team
                                fav_odds = odds.home_ml
                                dog_odds = odds.away_ml
                            else:
                                fav_team = game.away_team
                                dog_team = game.home_team
                                fav_odds = odds.away_ml
                                dog_odds = odds.home_ml
                        
                        # Extract bookmaker name from odds_key or use provider
                        bookmaker = odds.bookmaker if odds.bookmaker else odds.provider.value
                        
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
                        
                        bookmaker = odds.bookmaker if odds.bookmaker else odds.provider.value
                        
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
                        bookmaker = odds.bookmaker if odds.bookmaker else odds.provider.value
                        
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
        
        # Sort by game time, then by book
        df = df.sort_values(['game_time', 'book']).reset_index(drop=True)
        
        print(f"\n[SUCCESS] Found {len(df)} {MARKET_TYPE.upper()} markets")
        print("=" * 60)
        
        # Group by game and display
        if MARKET_TYPE == 'ml':
            for game_key, group in df.groupby(['teams', 'game_time']):
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'fav_team', 'dog_team', 'fav_odds', 'dog_odds', 'league', 'bet_type', 'game_time', 'game_date']
                print(group[display_cols].to_string(index=True))
        
        elif MARKET_TYPE == 'sp':
            for game_key, group in df.groupby(['teams', 'game_time']):
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'spread', 'fav_team', 'dog_team', 'fav_odds', 'dog_odds', 'league', 'bet_type', 'game_time', 'game_date']
                print(group[display_cols].to_string(index=True))
        
        elif MARKET_TYPE == 'ou':
            for game_key, group in df.groupby(['teams', 'game_time']):
                print(f"\n{game_key[0]} | {game_key[1]}")
                display_cols = ['book', 'teams', 'total', 'over_odds', 'under_odds', 'league', 'bet_type', 'game_time', 'game_date']
                print(group[display_cols].to_string(index=True))
        
        # Summary stats
        print(f"\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"Total Markets: {len(df)}")
        print(f"Unique Games: {len(df.groupby('teams'))}")
        print(f"Unique Books: {len(df['book'].unique())}")
        if 'book' in df.columns:
            print(f"Books: {', '.join(sorted(df['book'].unique()))}")
        
        # Show best odds for each game
        if SHOW_BEST_ODDS and MARKET_TYPE == 'ml':
            print(f"\nBEST ODDS SUMMARY:")
            print("-" * 40)
            for game_key, group in df.groupby(['teams']):
                teams_str = game_key
                
                # Find best odds for favorite and dog
                fav_team = group.iloc[0]['fav_team']
                dog_team = group.iloc[0]['dog_team']
                
                best_fav = group.loc[group['fav_odds'].abs().idxmin()]
                best_dog = group.loc[group['dog_odds'].idxmax()]
                
                print(f"{teams_str}:")
                print(f"  Best {fav_team}: {best_fav['fav_odds']} ({best_fav['book']})")
                print(f"  Best {dog_team}: {best_dog['dog_odds']} ({best_dog['book']})")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()