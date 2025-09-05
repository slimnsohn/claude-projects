#!/usr/bin/env python3
"""
Pinnacle Odds Display Tool
Simple tool to display Pinnacle odds for any league in clean format
Configure sport in main() function - no args needed for PyCharm
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pinnacle_client import PinnacleClient
from core.odds_converter import OddsConverter

def get_pinnacle_odds_display(sport='mlb', limit=None):
    """
    Get Pinnacle odds in clean display format
    
    Args:
        sport: Sport to fetch (mlb, nfl, nba, nhl, college_football, wnba, ufc)
        limit: Max number of games to show (None for all)
    
    Returns:
        DataFrame with clean odds display
    """
    print(f"Fetching {sport.upper()} odds from Pinnacle...")
    
    try:
        # Initialize client
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        api_key_path = os.path.join(project_root, 'keys', 'odds_api_key.txt')
        client = PinnacleClient(api_key_path)
        
        # Get raw data using the sports odds method
        raw_data = client.get_sports_odds(sport)
        
        if not raw_data.get('success'):
            print(f"ERROR: Failed to fetch {sport} data from Pinnacle")
            return pd.DataFrame()
        
        # Normalize the data (with minimal time buffer to include current games)
        normalized_games = client.normalize_pinnacle_data(raw_data, min_time_buffer_minutes=5)
        
        if not normalized_games:
            print(f"No {sport} games found on Pinnacle")
            return pd.DataFrame()
        
        print(f"Found {len(normalized_games)} {sport.upper()} games on Pinnacle")
        
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
                
                # Determine favorite/dog based on implied probability
                home_prob = home_odds.get('implied_probability', 0)
                away_prob = away_odds.get('implied_probability', 0)
                
                if home_prob > away_prob:
                    fav_team = home_team
                    dog_team = away_team
                    fav_odds = home_american
                    dog_odds = away_american
                else:
                    fav_team = away_team
                    dog_team = home_team
                    fav_odds = away_american
                    dog_odds = home_american
                
                # Create teams string
                teams = f"[{away_team}, {home_team}]"
                
                display_data.append({
                    'book': 'pinnacle',
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
        print(f"ERROR fetching Pinnacle odds: {e}")
        return pd.DataFrame()

def display_odds_table(df):
    """Display odds in clean table format"""
    if df.empty:
        print("No odds data to display")
        return
    
    print("\nPINNACLE ODDS:")
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
    
    print("PINNACLE ODDS DISPLAY TOOL")
    print("=" * 60)
    print(f"Sport: {SPORT.upper()}")
    print(f"Limit: {LIMIT if LIMIT else 'All games'}")
    print()
    
    # Get the odds
    odds_df = get_pinnacle_odds_display(sport=SPORT, limit=LIMIT)
    
    # Display the results
    display_odds_table(odds_df)
    
    # Export if requested
    if EXPORT_CSV and not odds_df.empty:
        filename = f"pinnacle_{SPORT}_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        odds_df.to_csv(filename, index=False)
        print(f"\nExported to: {filename}")
    
    print("\nSUCCESS: Pinnacle odds display complete!")

if __name__ == "__main__":
    main()