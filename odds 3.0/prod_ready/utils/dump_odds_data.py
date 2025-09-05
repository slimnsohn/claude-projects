#!/usr/bin/env python3
"""
Script to dump Pinnacle and Kalshi odds data in clean tabular format
Each game shows 2 rows: one for Pinnacle, one for Kalshi
"""

import pandas as pd
from datetime import datetime, timezone
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.main_system import MispricingSystem
from core.pinnacle_client import PinnacleClient
from core.kalshi_client import KalshiClientUpdated as KalshiClient

def dump_odds_data(sport='mlb', save_to_file=True):
    """
    Dump odds data from both Pinnacle and Kalshi in tabular format
    
    Args:
        sport: Sport to analyze ('mlb', 'nfl', 'nba', 'nhl', etc.)
        save_to_file: Whether to save to CSV files
    """
    print(f"DUMPING {sport.upper()} ODDS DATA")
    print("=" * 60)
    
    try:
        # Initialize clients
        pinnacle_client = PinnacleClient('../keys/odds_api_key.txt')
        kalshi_client = KalshiClient('../keys/kalshi_credentials.txt')
        
        # Get raw data
        print("Fetching Pinnacle data...")
        pinnacle_raw = pinnacle_client.get_sports_odds(sport)
        
        print("Fetching Kalshi data...")
        kalshi_raw = kalshi_client.search_sports_markets(sport)
        
        if not pinnacle_raw.get('success'):
            print(f"ERROR: Failed to fetch Pinnacle data: {pinnacle_raw.get('error')}")
            return
        
        if not kalshi_raw.get('success'):
            print(f"ERROR: Failed to fetch Kalshi data: {kalshi_raw.get('error')}")
            return
        
        # Normalize data
        print("Normalizing data...")
        pinnacle_games = pinnacle_client.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi_client.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"Pinnacle games: {len(pinnacle_games)}")
        print(f"Kalshi games: {len(kalshi_games)}")
        
        # Create data tables
        pinnacle_df = create_pinnacle_dataframe(pinnacle_games)
        kalshi_df = create_kalshi_dataframe(kalshi_games)
        
        # Display tables
        print(f"\n{'='*80}")
        print(f"PINNACLE {sport.upper()} ODDS ({len(pinnacle_games)} games)")
        print("=" * 80)
        if len(pinnacle_df) > 0:
            print(pinnacle_df.to_string(index=False))
        else:
            print("No Pinnacle games found")
        
        print(f"\n{'='*80}")
        print(f"KALSHI {sport.upper()} ODDS ({len(kalshi_games)} games)")
        print("=" * 80)
        if len(kalshi_df) > 0:
            print(kalshi_df.to_string(index=False))
        else:
            print("No Kalshi games found")
        
        # Create combined format (2 rows per game for common games)
        combined_df = create_combined_format(pinnacle_games, kalshi_games)
        
        print(f"\n{'='*100}")
        print(f"COMBINED FORMAT - {sport.upper()} ODDS COMPARISON")
        print("=" * 100)
        if len(combined_df) > 0:
            print(combined_df.to_string(index=False))
        else:
            print("No matching games found between Pinnacle and Kalshi")
        
        # Save to files if requested
        if save_to_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if len(pinnacle_df) > 0:
                pinnacle_file = f"pinnacle_{sport}_odds_{timestamp}.csv"
                pinnacle_df.to_csv(pinnacle_file, index=False)
                print(f"\nPinnacle data saved to: {pinnacle_file}")
            
            if len(kalshi_df) > 0:
                kalshi_file = f"kalshi_{sport}_odds_{timestamp}.csv"
                kalshi_df.to_csv(kalshi_file, index=False)
                print(f"Kalshi data saved to: {kalshi_file}")
            
            if len(combined_df) > 0:
                combined_file = f"combined_{sport}_odds_{timestamp}.csv"
                combined_df.to_csv(combined_file, index=False)
                print(f"Combined data saved to: {combined_file}")
        
        return {
            'pinnacle': pinnacle_df,
            'kalshi': kalshi_df,
            'combined': combined_df
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_pinnacle_dataframe(games):
    """Create clean DataFrame for Pinnacle games"""
    if not games:
        return pd.DataFrame()
    
    data = []
    for game in games:
        data.append({
            'Book': 'Pinnacle',
            'Game': f"{game['away_team']} @ {game['home_team']}",
            'Game_Time': game.get('game_time_display', 'Unknown'),
            'Away_Team': game['away_team'],
            'Home_Team': game['home_team'],
            'Away_Odds_American': game['away_odds']['american'],
            'Home_Odds_American': game['home_odds']['american'],
            'Away_Odds_Decimal': round(game['away_odds']['decimal'], 3),
            'Home_Odds_Decimal': round(game['home_odds']['decimal'], 3),
            'Away_Implied_Prob': f"{game['away_odds']['implied_probability']:.1%}",
            'Home_Implied_Prob': f"{game['home_odds']['implied_probability']:.1%}",
            'Game_ID': game['game_id'],
            'Source': game.get('source', 'pinnacle')
        })
    
    return pd.DataFrame(data)

def create_kalshi_dataframe(games):
    """Create clean DataFrame for Kalshi games"""
    if not games:
        return pd.DataFrame()
    
    data = []
    for game in games:
        data.append({
            'Book': 'Kalshi',
            'Game': f"{game['away_team']} @ {game['home_team']}",
            'Game_Time': game.get('game_time_display', 'Unknown'),
            'Away_Team': game['away_team'],
            'Home_Team': game['home_team'],
            'Away_Odds_American': game['away_odds']['american'],
            'Home_Odds_American': game['home_odds']['american'],
            'Away_Odds_Decimal': round(game['away_odds']['decimal'], 3),
            'Home_Odds_Decimal': round(game['home_odds']['decimal'], 3),
            'Away_Implied_Prob': f"{game['away_odds']['implied_probability']:.1%}",
            'Home_Implied_Prob': f"{game['home_odds']['implied_probability']:.1%}",
            'Game_ID': game['game_id'],
            'Source': game.get('source', 'kalshi')
        })
    
    return pd.DataFrame(data)

def create_combined_format(pinnacle_games, kalshi_games):
    """Create combined format matching your exact structure with 2 rows per game"""
    if not pinnacle_games or not kalshi_games:
        return pd.DataFrame()
    
    # Simple matching by team names
    combined_data = []
    
    for p_game in pinnacle_games:
        p_away = p_game['away_team'].upper()
        p_home = p_game['home_team'].upper()
        
        # Find matching Kalshi game
        for k_game in kalshi_games:
            k_away = k_game['away_team'].upper()
            k_home = k_game['home_team'].upper()
            
            # Check if teams match (either direction)
            if ((p_away == k_away and p_home == k_home) or 
                (p_away == k_home and p_home == k_away)):
                
                # Determine favorite/dog for each book
                p_fav, p_dog, p_fav_odds, p_dog_odds = determine_favorite_dog(
                    p_game['away_team'], p_game['home_team'],
                    p_game['away_odds']['american'], p_game['home_odds']['american']
                )
                
                k_fav, k_dog, k_fav_odds, k_dog_odds = determine_favorite_dog(
                    k_game['away_team'], k_game['home_team'],
                    k_game['away_odds']['american'], k_game['home_odds']['american']
                )
                
                # Format game time and date
                p_time, p_date = format_game_time_date(p_game.get('game_time_display', 'Unknown'))
                k_time, k_date = format_game_time_date(k_game.get('game_time_display', 'Unknown'))
                
                # Add Pinnacle row
                combined_data.append({
                    'book': 'pinnacle',
                    'teams': [p_game['away_team'], p_game['home_team']],
                    'fav_team': p_fav,
                    'dog_team': p_dog,
                    'fav_odds': p_fav_odds,
                    'dog_odds': p_dog_odds,
                    'league': 'mlb',
                    'bet_type': 'ml',
                    'game_time': p_time,
                    'game_date': p_date
                })
                
                # Add Kalshi row
                combined_data.append({
                    'book': 'kalshi',
                    'teams': [k_game['away_team'], k_game['home_team']],
                    'fav_team': k_fav,
                    'dog_team': k_dog,
                    'fav_odds': k_fav_odds,
                    'dog_odds': k_dog_odds,
                    'league': 'mlb',
                    'bet_type': 'ml',
                    'game_time': k_time,
                    'game_date': k_date
                })
                break
    
    return pd.DataFrame(combined_data)

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
    # Parse the display time like "2025-08-21 19:00" or "Aug 21, 19:00"
    try:
        if 'Unknown' in game_time_display:
            return 'Unknown', 'Unknown'
        
        # Handle different formats
        if '-' in game_time_display:  # 2025-08-21 19:00
            parts = game_time_display.split(' ')
            if len(parts) >= 2:
                date_part = parts[0]  # 2025-08-21
                time_part = parts[1]  # 19:00
                
                # Convert date to format like 20250822
                from datetime import datetime
                date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y%m%d')
                
                # Convert time to format like FRI_20:41
                day_name = date_obj.strftime('%a').upper()
                formatted_time = f"{day_name}_{time_part}"
                
                return formatted_time, formatted_date
        
        elif ',' in game_time_display:  # Aug 21, 19:00
            parts = game_time_display.split(', ')
            if len(parts) >= 2:
                date_part = parts[0]  # Aug 21
                time_part = parts[1]  # 19:00
                
                # Convert to datetime
                from datetime import datetime
                current_year = datetime.now().year
                date_str = f"{date_part} {current_year}"
                date_obj = datetime.strptime(date_str, '%b %d %Y')
                
                formatted_date = date_obj.strftime('%Y%m%d')
                day_name = date_obj.strftime('%a').upper()
                formatted_time = f"{day_name}_{time_part}"
                
                return formatted_time, formatted_date
        
        return 'Unknown', 'Unknown'
        
    except Exception:
        return 'Unknown', 'Unknown'

def main():
    """Main function with command line options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dump Pinnacle and Kalshi odds data')
    parser.add_argument('--sport', '-s', default='mlb', 
                       help='Sport to analyze (mlb, nfl, nba, nhl, etc.)')
    parser.add_argument('--no-save', action='store_true',
                       help='Don\'t save to CSV files')
    parser.add_argument('--pinnacle-only', action='store_true',
                       help='Only show Pinnacle data')
    parser.add_argument('--kalshi-only', action='store_true',
                       help='Only show Kalshi data')
    parser.add_argument('--combined-only', action='store_true',
                       help='Only show combined format')
    
    args = parser.parse_args()
    
    # Run the data dump
    result = dump_odds_data(
        sport=args.sport,
        save_to_file=not args.no_save
    )
    
    if result:
        print(f"\n{'='*60}")
        print("SUMMARY:")
        print(f"Pinnacle games: {len(result['pinnacle'])}")
        print(f"Kalshi games: {len(result['kalshi'])}")
        print(f"Matching games: {len(result['combined']) // 3}")  # Divide by 3 due to separator rows
    
    return result

if __name__ == "__main__":
    # If running directly, use command line args
    if len(sys.argv) > 1:
        main()
    else:
        # Default behavior - dump MLB data
        print("Usage examples:")
        print("  python dump_odds_data.py --sport mlb")
        print("  python dump_odds_data.py --sport nfl --no-save")
        print("  python dump_odds_data.py --sport nba --combined-only")
        print()
        print("Running default: MLB data dump...")
        dump_odds_data('mlb')