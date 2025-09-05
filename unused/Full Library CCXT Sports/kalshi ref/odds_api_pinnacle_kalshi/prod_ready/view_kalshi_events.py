#!/usr/bin/env python3
"""
KALSHI EVENTS VIEWER - View all events for a given league

Use this script to see all available events on Kalshi for any supported league.
Shows raw market data, normalized data, and filtering results.

Usage:
    python view_kalshi_events.py                    # View MLB events (default)
    python view_kalshi_events.py --sport nfl        # View NFL events
    python view_kalshi_events.py --raw              # Show raw market data
    python view_kalshi_events.py --no-filter        # Don't filter live games
    python view_kalshi_events.py --help             # Show all options
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add path for organized imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient
from config.sports_config import get_available_sports, get_supported_sports_display

def main():
    """Main Kalshi events viewing function"""
    parser = argparse.ArgumentParser(
        description='Kalshi Events Viewer - See all events for a league',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python view_kalshi_events.py                    # View MLB events
  python view_kalshi_events.py --sport nfl        # View NFL events
  python view_kalshi_events.py --sport nba        # View NBA events
  python view_kalshi_events.py --raw              # Show raw market data
  python view_kalshi_events.py --no-filter        # Include live games
  python view_kalshi_events.py --export           # Export to CSV

Available Sports: {get_supported_sports_display()}
"""
    )
    
    parser.add_argument(
        '--sport', '-s',
        default='nfl',
        help=f'Sport to view. Options: {", ".join(get_available_sports())}'
    )
    
    parser.add_argument(
        '--raw', '-r',
        action='store_true',
        help='Show raw market data from Kalshi API'
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
    
    parser.add_argument(
        '--show-raw-markets',
        action='store_true',
        help='Show raw market tickers and titles before normalization'
    )
    
    args = parser.parse_args()
    
    print(f"KALSHI EVENTS VIEWER - {args.sport.upper()}")
    print("=" * 60)
    print(f"Data retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time buffer: {args.buffer_minutes} minutes")
    print()
    
    try:
        # Initialize Kalshi client
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        
        client = KalshiClient(creds_path)
        
        # Fetch raw data
        print("Fetching Kalshi markets...")
        raw_data = client.search_sports_markets(args.sport)
        
        if not raw_data.get('success'):
            print(f"ERROR: Failed to fetch data - {raw_data.get('error')}")
            return
        
        raw_markets = raw_data.get('data', [])
        print(f"SUCCESS: Found {len(raw_markets)} {args.sport.upper()} markets on Kalshi")
        print()
        
        # Show raw data if requested
        if args.raw:
            print("RAW MARKET DATA:")
            print("-" * 40)
            print(json.dumps(raw_data, indent=2, default=str))
            print()
            return
        
        # Show raw market tickers if requested
        if args.show_raw_markets:
            print("RAW MARKET TICKERS:")
            print("-" * 40)
            for i, market in enumerate(raw_markets[:20], 1):  # Show first 20
                print(f"{i:2d}. {market.get('ticker', 'N/A')}: {market.get('title', 'N/A')}")
                if market.get('close_time'):
                    print(f"     Close: {market['close_time']}")
                print()
            
            if len(raw_markets) > 20:
                print(f"... and {len(raw_markets) - 20} more markets")
            print()
        
        # Apply filtering if not disabled
        if args.no_filter:
            print("EVENTS (No filtering applied - showing all raw markets):")
            print("-" * 60)
            
            # Show all raw markets without normalization
            display_markets = raw_markets
            if args.limit and len(display_markets) > args.limit:
                display_markets = display_markets[:args.limit]
                print(f"Showing first {args.limit} of {len(raw_markets)} markets:")
                print()
            
            # Display raw markets
            print(f"{'#':<3} {'Ticker':<30} {'Title':<50} {'Close Time':<20}")
            print("-" * 105)
            
            for i, market in enumerate(display_markets, 1):
                ticker = market.get('ticker', 'N/A')[:29]
                title = market.get('title', 'N/A')[:49]
                close_time = market.get('close_time', 'N/A')[:19]
                
                print(f"{i:<3} {ticker:<30} {title:<50} {close_time:<20}")
            
            print()
            print(f"SUMMARY:")
            print(f"  Total markets found: {len(raw_markets)}")
            if args.limit:
                print(f"  Markets displayed: {min(args.limit, len(raw_markets))}")
                
            return  # Exit early for no-filter mode
        else:
            normalized_games = client.normalize_kalshi_data(raw_data, args.buffer_minutes)
            filtered_count = len(raw_markets) - len(normalized_games)
            print(f"EVENTS (Filtered out {filtered_count} live/starting markets):")
            print("-" * 60)
        
        if len(normalized_games) == 0:
            print("No events found after filtering")
            if not args.no_filter:
                print("This could be because:")
                print("- All games are live or starting soon")
                print("- Markets don't match expected game format")
                print("- Try using --no-filter to see all markets")
            return
        
        # Apply limit if specified
        display_games = normalized_games
        if args.limit and len(display_games) > args.limit:
            display_games = display_games[:args.limit]
            print(f"Showing first {args.limit} of {len(normalized_games)} events:")
            print()
        
        # Display events in table format
        print(f"{'#':<3} {'Away Team':<20} {'Home Team':<20} {'Game Time':<15} {'Yes Price':<15} {'No Price':<15}")
        print("-" * 105)
        
        for i, game in enumerate(display_games, 1):
            away_team = game['away_team'][:19] if len(game['away_team']) > 19 else game['away_team']
            home_team = game['home_team'][:19] if len(game['home_team']) > 19 else game['home_team']
            game_time = game.get('game_time_display', 'Unknown')[:14]
            
            # Kalshi uses yes/no pricing - include cents
            if game.get('home_odds'):
                home_american = game['home_odds']['american']
                home_cents = game['home_odds'].get('kalshi_cents', 0)
                home_yes = f"{home_american:+d} ({home_cents}c)"
            else:
                home_yes = 'N/A'
                
            if game.get('away_odds'):
                away_american = game['away_odds']['american']
                away_cents = game['away_odds'].get('kalshi_cents', 0)
                home_no = f"{away_american:+d} ({away_cents}c)"
            else:
                home_no = 'N/A'
            
            print(f"{i:<3} {away_team:<20} {home_team:<20} {game_time:<15} {home_yes:<15} {home_no:<15}")
        
        print()
        print(f"SUMMARY:")
        print(f"  Total markets from API: {len(raw_markets)}")
        print(f"  Events after normalization: {len(normalized_games)}")
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
                    'home_yes_american': game['home_odds']['american'] if game.get('home_odds') else None,
                    'away_yes_american': game['away_odds']['american'] if game.get('away_odds') else None,
                    'home_yes_cents': game['home_odds'].get('kalshi_cents', 0) if game.get('home_odds') else None,
                    'away_yes_cents': game['away_odds'].get('kalshi_cents', 0) if game.get('away_odds') else None,
                    'home_yes_decimal': game['home_odds']['decimal'] if game.get('home_odds') else None,
                    'away_yes_decimal': game['away_odds']['decimal'] if game.get('away_odds') else None,
                    'home_implied_prob': game['home_odds']['implied_prob'] if game.get('home_odds') else None,
                    'away_implied_prob': game['away_odds']['implied_prob'] if game.get('away_odds') else None,
                    'original_ticker': game.get('original_ticker', ''),
                    'sport': args.sport,
                    'book': 'kalshi'
                })
            
            df = pd.DataFrame(export_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kalshi_{args.sport}_events_{timestamp}.csv"
            df.to_csv(filename, index=False)
            print(f"  Exported to: {filename}")
        
        print()
        print("SUCCESS: Kalshi events viewing complete!")
        
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