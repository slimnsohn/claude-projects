#!/usr/bin/env python3
"""
Quick script to dump odds data in your exact format
Shows both Pinnacle and Kalshi data even if no live games
"""

import pandas as pd
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pinnacle_client import PinnacleClient
from core.kalshi_client import KalshiClientUpdated as KalshiClient

def quick_dump_odds(sport='mlb'):
    """Quick dump of odds data in your exact format"""
    print(f"QUICK {sport.upper()} ODDS DUMP")
    print("=" * 50)
    
    try:
        # Initialize clients
        pinnacle_client = PinnacleClient('../keys/odds_api_key.txt')
        kalshi_client = KalshiClient('../keys/kalshi_credentials.txt')
        
        # Get Pinnacle data
        print("Fetching Pinnacle data...")
        pinnacle_raw = pinnacle_client.get_sports_odds(sport)
        pinnacle_games = pinnacle_client.normalize_pinnacle_data(pinnacle_raw, 15)
        
        # Get Kalshi data (with no time buffer to get all games for demo)
        print("Fetching Kalshi data...")
        kalshi_raw = kalshi_client.search_sports_markets(sport)
        kalshi_games_all = kalshi_client.normalize_kalshi_data(kalshi_raw, 0)  # No filter for demo
        
        print(f"Pinnacle games: {len(pinnacle_games)}")
        print(f"Kalshi games (unfiltered): {len(kalshi_games_all)}")
        
        # Create the exact format you want
        all_data = []
        
        # Process Pinnacle games
        for game in pinnacle_games:
            fav_team, dog_team, fav_odds, dog_odds = determine_favorite_dog(
                game['away_team'], game['home_team'],
                game['away_odds']['american'], game['home_odds']['american']
            )
            
            game_time, game_date = format_game_time_date(game.get('game_time_display', 'Unknown'))
            
            all_data.append({
                'book': 'pinnacle',
                'teams': [game['away_team'], game['home_team']],
                'fav_team': fav_team,
                'dog_team': dog_team,
                'fav_odds': fav_odds,
                'dog_odds': dog_odds,
                'league': sport,
                'bet_type': 'ml',
                'game_time': game_time,
                'game_date': game_date
            })
        
        # Process Kalshi games (take first few for demo)
        for game in kalshi_games_all[:min(len(kalshi_games_all), 3)]:
            fav_team, dog_team, fav_odds, dog_odds = determine_favorite_dog(
                game['away_team'], game['home_team'],
                game['away_odds']['american'], game['home_odds']['american']
            )
            
            game_time, game_date = format_game_time_date(game.get('game_time_display', 'Unknown'))
            
            all_data.append({
                'book': 'kalshi',
                'teams': [game['away_team'], game['home_team']],
                'fav_team': fav_team,
                'dog_team': dog_team,
                'fav_odds': fav_odds,
                'dog_odds': dog_odds,
                'league': sport,
                'bet_type': 'ml',
                'game_time': game_time,
                'game_date': game_date
            })
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        print(f"\n{sport.upper()} ODDS DATA (Your Format):")
        print("=" * 80)
        if len(df) > 0:
            print(df.to_string(index=True))
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{sport}_odds_dump_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"\nSaved to: {filename}")
        else:
            print("No data found")
        
        return df
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def determine_favorite_dog(away_team, home_team, away_odds, home_odds):
    """Determine favorite and dog based on American odds"""
    # Negative odds = favorite, positive odds = dog
    if away_odds < 0 and home_odds > 0:
        return away_team, home_team, away_odds, home_odds
    elif home_odds < 0 and away_odds > 0:
        return home_team, away_team, home_odds, away_odds
    elif away_odds < 0 and home_odds < 0:
        # Both negative, smaller absolute value is favorite
        if abs(away_odds) < abs(home_odds):
            return away_team, home_team, away_odds, home_odds
        else:
            return home_team, away_team, home_odds, away_odds
    else:
        # Both positive, smaller value is favorite
        if away_odds < home_odds:
            return away_team, home_team, away_odds, home_odds
        else:
            return home_team, away_team, home_odds, away_odds

def format_game_time_date(game_time_display):
    """Format game time and date to match your format"""
    try:
        if 'Unknown' in game_time_display:
            return 'Unknown', 'Unknown'
        
        # Handle different formats
        if '-' in game_time_display and ' ' in game_time_display:  # 2025-08-21 19:00
            parts = game_time_display.split(' ')
            if len(parts) >= 2:
                date_part = parts[0]  # 2025-08-21
                time_part = parts[1]  # 19:00
                
                # Convert date to format like 20250822
                from datetime import datetime
                date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y%m%d')
                
                # Convert time to format like FRI_20:41
                day_name = date_obj.strftime('%a').upper()[:3]
                formatted_time = f"{day_name}_{time_part}"
                
                return formatted_time, formatted_date
        
        elif ',' in game_time_display:  # Aug 22, 22:41
            parts = game_time_display.split(', ')
            if len(parts) >= 2:
                date_part = parts[0]  # Aug 22
                time_part = parts[1]  # 22:41
                
                # Convert to datetime
                from datetime import datetime
                current_year = datetime.now().year
                date_str = f"{date_part} {current_year}"
                date_obj = datetime.strptime(date_str, '%b %d %Y')
                
                formatted_date = date_obj.strftime('%Y%m%d')
                day_name = date_obj.strftime('%a').upper()[:3]
                formatted_time = f"{day_name}_{time_part}"
                
                return formatted_time, formatted_date
        
        return 'Unknown', 'Unknown'
        
    except Exception as e:
        print(f"Date format error: {e}")
        return 'Unknown', 'Unknown'

if __name__ == "__main__":
    quick_dump_odds('mlb')