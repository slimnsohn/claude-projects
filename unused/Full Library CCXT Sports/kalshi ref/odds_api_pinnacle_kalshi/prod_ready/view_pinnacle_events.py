#!/usr/bin/env python3
"""
PINNACLE EVENTS VIEWER - View all events for a given league

Use this script to see all available events on Pinnacle for any supported league.
Shows raw data, normalized data, and filtering results.

Usage:
    python view_pinnacle_events.py                    # View MLB events (default)
    python view_pinnacle_events.py --sport nfl        # View NFL events
    python view_pinnacle_events.py --raw              # Show raw API response
    python view_pinnacle_events.py --no-filter        # Don't filter live games
    python view_pinnacle_events.py --help             # Show all options
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add path for organized imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.pinnacle_client import PinnacleClient
from config.sports_config import get_available_sports, get_supported_sports_display

def main():
    """Main Pinnacle events viewing function"""
    parser = argparse.ArgumentParser(
        description='Pinnacle Events Viewer - See all events for a league',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python view_pinnacle_events.py                    # View MLB events
  python view_pinnacle_events.py --sport nfl        # View NFL events
  python view_pinnacle_events.py --sport nba        # View NBA events
  python view_pinnacle_events.py --raw              # Show raw API data
  python view_pinnacle_events.py --no-filter        # Include live games
  python view_pinnacle_events.py --export           # Export to CSV

Available Sports: {get_supported_sports_display()}
"""
    )
    
    parser.add_argument(
        '--sport', '-s',
        default='mlb',
        help=f'Sport to view. Options: {", ".join(get_available_sports())}'
    )
    
    parser.add_argument(
        '--raw', '-r',
        action='store_true',
        help='Show raw API response data'
    )
    
    parser.add_argument(
        '--no-filter',
        action='store_true',
        help='Don\'t filter out live games'
    )
    
    parser.add_argument(
        '--export', '-e',
        action='store_true',
        help='Export results to CSV file'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of events to display'
    )
    
    parser.add_argument(
        '--buffer-minutes',
        type=int,
        default=15,
        help='Time buffer in minutes for filtering live games (default: 15)'
    )
    
    args = parser.parse_args()
    
    print(f"PINNACLE EVENTS VIEWER - {args.sport.upper()}")
    print("=" * 60)
    print(f"Data retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time buffer: {args.buffer_minutes} minutes")
    print()
    
    try:
        # Initialize Pinnacle client
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        api_key_path = os.path.join(project_root, 'keys', 'odds_api_key.txt')
        
        client = PinnacleClient(api_key_path)
        
        # Fetch raw data
        print("Fetching Pinnacle data...")
        raw_data = client.get_sports_odds(args.sport)
        
        if not raw_data.get('success'):
            print(f"ERROR: Failed to fetch data - {raw_data.get('error')}")
            return
        
        raw_games = raw_data.get('data', [])
        print(f"SUCCESS: Fetched {len(raw_games)} raw events from Pinnacle")
        print()
        
        # Show raw data if requested
        if args.raw:
            print("RAW API RESPONSE:")
            print("-" * 40)
            print(json.dumps(raw_data, indent=2, default=str))
            print()
            return
        
        # Apply filtering if not disabled
        if args.no_filter:
            normalized_games = client.normalize_pinnacle_data(raw_data, 0)  # No time filtering
            print("EVENTS (No filtering applied):")
        else:
            normalized_games = client.normalize_pinnacle_data(raw_data, args.buffer_minutes)
            filtered_count = len(raw_games) - len(normalized_games)
            print(f"EVENTS (Filtered out {filtered_count} live/starting games):")
        
        print("-" * 60)
        
        if len(normalized_games) == 0:
            print("No events found after filtering")
            return
        
        # Apply limit if specified
        display_games = normalized_games
        if args.limit and len(display_games) > args.limit:
            display_games = display_games[:args.limit]
            print(f"Showing first {args.limit} of {len(normalized_games)} events:")
            print()
        
        # Display events in table format
        print(f"{'#':<3} {'Away Team':<20} {'Home Team':<20} {'Game Time':<15} {'Away Odds':<10} {'Home Odds':<10}")
        print("-" * 90)
        
        for i, game in enumerate(display_games, 1):
            away_team = game['away_team'][:19] if len(game['away_team']) > 19 else game['away_team']
            home_team = game['home_team'][:19] if len(game['home_team']) > 19 else game['home_team']
            game_time = game.get('game_time_display', 'Unknown')[:14]
            away_odds = f"{game['away_odds']['american']:+d}" if game.get('away_odds') else 'N/A'
            home_odds = f"{game['home_odds']['american']:+d}" if game.get('home_odds') else 'N/A'
            
            print(f"{i:<3} {away_team:<20} {home_team:<20} {game_time:<15} {away_odds:<10} {home_odds:<10}")
        
        print()
        print(f"SUMMARY:")
        print(f"  Total events from API: {len(raw_games)}")
        print(f"  Events after filtering: {len(normalized_games)}")
        if args.limit:
            print(f"  Events displayed: {min(args.limit, len(normalized_games))}")
        
        # Export if requested
        if args.export:
            import pandas as pd
            
            # Prepare data for export
            export_data = []
            for game in normalized_games:
                export_data.append({
                    'away_team': game['away_team'],
                    'home_team': game['home_team'],
                    'game_time': game.get('game_time_display', 'Unknown'),
                    'away_odds_american': game['away_odds']['american'] if game.get('away_odds') else None,
                    'home_odds_american': game['home_odds']['american'] if game.get('home_odds') else None,
                    'away_odds_decimal': game['away_odds']['decimal'] if game.get('away_odds') else None,
                    'home_odds_decimal': game['home_odds']['decimal'] if game.get('home_odds') else None,
                    'away_implied_prob': game['away_odds']['implied_prob'] if game.get('away_odds') else None,
                    'home_implied_prob': game['home_odds']['implied_prob'] if game.get('home_odds') else None,
                    'sport': args.sport,
                    'book': 'pinnacle'
                })
            
            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pinnacle_{args.sport}_events_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"  Exported to: {filename}")
        
        print()
        print("SUCCESS: Pinnacle events viewing complete!")
        
    except KeyboardInterrupt:
        print("\nWARNING: Viewing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Failed to fetch events - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()