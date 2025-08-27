#!/usr/bin/env python3
"""
Kalshi Odds Display Tool
Simple tool to display Kalshi odds for any league in clean format
Configure sport in main() function - no args needed for PyCharm
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.kalshi_client import KalshiClientUpdated as KalshiClient
from core.odds_converter import OddsConverter

def get_kalshi_odds_display(sport='mlb', limit=None):
    """
    Get Kalshi odds in clean display format
    
    Args:
        sport: Sport to fetch (mlb, nfl, nba, nhl, college_football, wnba, ufc)
        limit: Max number of games to show (None for all)
    
    Returns:
        DataFrame with clean odds display
    """
    print(f"Fetching {sport.upper()} odds from Kalshi...")
    
    try:
        # Initialize client
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Get raw data using the efficient search
        raw_data = client.search_sports_markets(sport)
        
        if not raw_data.get('success'):
            print(f"ERROR: Failed to fetch {sport} data from Kalshi")
            return pd.DataFrame()
        
        # Normalize the data (with minimal time buffer to include current games)
        normalized_games = client.normalize_kalshi_data(raw_data, min_time_buffer_minutes=5)
        
        if not normalized_games:
            print(f"No {sport} games found on Kalshi")
            return pd.DataFrame()
        
        print(f"Found {len(normalized_games)} {sport.upper()} games on Kalshi")
        
        # Convert to clean display format
        display_data = []
        
        for game in normalized_games:
            try:
                # Get basic info
                away_team = game.get('away_team', 'Unknown')
                home_team = game.get('home_team', 'Unknown')
                game_time = game.get('game_time_display', 'Unknown')
                game_date = game.get('game_date', 'Unknown')
                
                # Get odds info
                home_odds = game.get('home_odds', {})
                away_odds = game.get('away_odds', {})
                
                if not home_odds or not away_odds:
                    continue
                
                home_american = home_odds.get('american', 0)
                away_american = away_odds.get('american', 0)
                home_cents = home_odds.get('kalshi_cents', 0)
                away_cents = away_odds.get('kalshi_cents', 0)
                
                # Determine favorite/dog based on implied probability
                home_prob = home_odds.get('implied_prob', 0)
                away_prob = away_odds.get('implied_prob', 0)
                
                if home_prob > away_prob:
                    fav_team = home_team
                    dog_team = away_team
                    fav_odds = f"{home_american:+d} ({home_cents}c)"
                    dog_odds = f"{away_american:+d} ({away_cents}c)"
                else:
                    fav_team = away_team
                    dog_team = home_team
                    fav_odds = f"{away_american:+d} ({away_cents}c)"
                    dog_odds = f"{home_american:+d} ({home_cents}c)"
                
                # Create teams string
                teams = f"[{away_team}, {home_team}]"
                
                display_data.append({
                    'book': 'kalshi',
                    'teams': teams,
                    'fav_team': fav_team,
                    'dog_team': dog_team,
                    'fav_odds': fav_odds,
                    'dog_odds': dog_odds,
                    'league': sport.lower(),
                    'bet_type': 'ml',
                    'game_time': game_time,
                    'game_date': game_date
                })
                
            except Exception as e:
                print(f"Error processing game: {e}")
                continue
        
        if not display_data:
            print(f"No valid {sport} odds data to display")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(display_data)
        
        # Apply limit if specified
        if limit and len(df) > limit:
            print(f"Showing first {limit} of {len(df)} games:")
            df = df.head(limit)
        
        return df
        
    except Exception as e:
        print(f"ERROR fetching Kalshi odds: {e}")
        return pd.DataFrame()

def display_odds_table(df):
    """Display odds in clean table format"""
    if df.empty:
        print("No odds data to display")
        return
    
    print("\nKALSHI ODDS:")
    print("=" * 120)
    
    # Format the display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 20)
    
    # Print the table
    print(df.to_string(index=True))
    
    print(f"\nTotal games: {len(df)}")
    print(f"Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """
    MAIN FUNCTION - Configure your settings here for PyCharm
    Change these settings as needed:
    """
    
    # CONFIGURE THESE SETTINGS:
    SPORT = 'mlb'           # Options: mlb, nfl, nba, nhl, college_football, wnba, ufc
    LIMIT = 20              # Number of games to show (None for all)
    EXPORT_CSV = False      # Set to True to export to CSV
    
    print("KALSHI ODDS DISPLAY TOOL")
    print("=" * 60)
    print(f"Sport: {SPORT.upper()}")
    print(f"Limit: {LIMIT if LIMIT else 'All games'}")
    print()
    
    # Get the odds
    odds_df = get_kalshi_odds_display(sport=SPORT, limit=LIMIT)
    
    # Display the results
    display_odds_table(odds_df)
    
    # Export if requested
    if EXPORT_CSV and not odds_df.empty:
        filename = f"kalshi_{SPORT}_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        odds_df.to_csv(filename, index=False)
        print(f"\nExported to: {filename}")
    
    print("\nSUCCESS: Kalshi odds display complete!")

if __name__ == "__main__":
    main()