#!/usr/bin/env python3
"""
ODDS VIEWER SCRIPT - Clean Interface for Viewing Game Odds

Use this script to view and export odds data from Pinnacle and Kalshi.
Outputs in your preferred format with clean tables.

Usage:
    python view_odds.py                      # View MLB odds (default)
    python view_odds.py --sport nfl          # View NFL odds
    python view_odds.py --export             # Export to CSV
    python view_odds.py --format combined    # Show combined format (2 rows per game)
    python view_odds.py --help               # Show all options
"""

import sys
import os
import argparse
from datetime import datetime

# Add path for organized imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.quick_odds_dump import quick_dump_odds
from utils.dump_odds_data import dump_odds_data
from config.sports_config import get_available_sports, get_supported_sports_display

def main():
    """Main odds viewing function with clean interface"""
    parser = argparse.ArgumentParser(
        description='Pinnacle-Kalshi Odds Viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python view_odds.py                        # View MLB odds
  python view_odds.py --sport nfl            # View NFL odds  
  python view_odds.py --export               # Export to CSV files
  python view_odds.py --format combined      # Show your preferred format
  python view_odds.py --pinnacle-only        # Show only Pinnacle odds
  python view_odds.py --kalshi-only          # Show only Kalshi odds

Available Sports: {get_supported_sports_display()}

Output Formats:
  - quick: Your preferred format ([teams], fav_team, dog_team, etc.)
  - detailed: Full breakdown with all odds formats
  - combined: 2 rows per matching game (Pinnacle + Kalshi)
"""
    )
    
    parser.add_argument(
        '--sport', '-s',
        default='mlb',
        help=f'Sport to view. Options: {", ".join(get_available_sports())}'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['quick', 'detailed', 'combined'],
        default='quick',
        help='Output format (default: quick - your preferred format)'
    )
    
    parser.add_argument(
        '--export', '-e',
        action='store_true',
        help='Export to CSV files'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Don\'t save CSV files (display only)'
    )
    
    parser.add_argument(
        '--pinnacle-only',
        action='store_true',
        help='Show only Pinnacle odds'
    )
    
    parser.add_argument(
        '--kalshi-only',
        action='store_true',
        help='Show only Kalshi odds'
    )
    
    parser.add_argument(
        '--combined-only',
        action='store_true',
        help='Show only combined format (matching games)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=20,
        help='Limit number of games to display (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print(f"{args.sport.upper()} ODDS VIEWER")
    print("=" * 50)
    print(f"Data retrieved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Format: {args.format}")
    print()
    
    try:
        if args.format == 'quick' or not args.export:
            # Use quick dump for your preferred format
            print("ODDS ODDS DATA (Your Preferred Format):")
            print("-" * 50)
            df = quick_dump_odds(args.sport)
            
            if df is not None and len(df) > 0:
                # Limit results if requested
                if args.limit and len(df) > args.limit:
                    print(f"Showing first {args.limit} of {len(df)} games:")
                    df_display = df.head(args.limit)
                else:
                    df_display = df
                
                print(df_display.to_string(index=True))
                print(f"\nTotal games found: {len(df)}")
                
                if args.export and not args.no_save:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{args.sport}_odds_quick_{timestamp}.csv"
                    df.to_csv(filename, index=False)
                    print(f"SAVED Exported to: {filename}")
            else:
                print("No odds data found")
                
        else:
            # Use detailed dump for comprehensive view
            print("DATA COMPREHENSIVE ODDS DATA:")
            print("-" * 50)
            
            # Set up options based on arguments
            save_files = args.export and not args.no_save
            
            if args.pinnacle_only:
                print("(Pinnacle only)")
            elif args.kalshi_only:
                print("(Kalshi only)")
            elif args.combined_only:
                print("(Combined format only)")
            
            result = dump_odds_data(
                sport=args.sport,
                save_to_file=save_files
            )
            
            if result:
                print(f"\nSUMMARY:")
                print(f"Pinnacle games: {len(result['pinnacle'])}")
                print(f"Kalshi games: {len(result['kalshi'])}")
                if 'combined' in result:
                    # Account for separator rows
                    combined_games = len([r for r in result['combined'].to_dict('records') if r.get('Book') != '---'])
                    print(f"Matching games: {combined_games // 2}")  # 2 rows per game
                
                if save_files:
                    print("SAVED Files exported successfully!")
        
        print("\nSUCCESS Odds viewing complete!")
        
    except KeyboardInterrupt:
        print("\nWARNING  Viewing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR Error viewing odds: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()