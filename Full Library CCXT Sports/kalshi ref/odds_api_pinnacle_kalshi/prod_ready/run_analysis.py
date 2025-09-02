#!/usr/bin/env python3
"""
MAIN ANALYSIS SCRIPT - Your Primary Tool for Mispricing Detection

Run this script to find mispricing opportunities between Pinnacle and Kalshi.
Clean, simple interface with all the power of the underlying system.

Usage:
    python run_analysis.py                  # Run MLB analysis (default)
    python run_analysis.py --sport nfl      # Run NFL analysis  
    python run_analysis.py --all-sports     # Run analysis on all available sports
    python run_analysis.py --help           # Show all options
"""

import sys
import os
import argparse
from datetime import datetime

# Add path for organized imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.main_system import MispricingSystem
from config.sports_config import get_available_sports, get_current_season_sports, get_supported_sports_display

def main():
    """Main analysis function with clean command line interface"""
    parser = argparse.ArgumentParser(
        description='Pinnacle-Kalshi Mispricing Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python run_analysis.py                    # MLB analysis (default)
  python run_analysis.py --sport nfl        # NFL analysis
  python run_analysis.py --sport nba        # NBA analysis
  python run_analysis.py --all-sports       # All available sports
  python run_analysis.py --current-season   # Only sports currently in season

Available Sports: {get_supported_sports_display()}
"""
    )
    
    parser.add_argument(
        '--sport', '-s',
        default='mlb',
        help=f'Sport to analyze. Options: {", ".join(get_available_sports())}'
    )
    
    parser.add_argument(
        '--all-sports', '-a',
        action='store_true',
        help='Run analysis on all available sports'
    )
    
    parser.add_argument(
        '--current-season', '-c',
        action='store_true',
        help='Run analysis only on sports currently in season'
    )
    
    parser.add_argument(
        '--max-opportunities', '-m',
        type=int,
        default=10,
        help='Maximum number of opportunities to display (default: 10)'
    )
    
    parser.add_argument(
        '--min-edge', '-e',
        type=float,
        help='Minimum edge percentage (e.g., 0.02 for 2%%). Uses sport default if not specified.'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output and save results to file'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("PINNACLE-KALSHI MISPRICING DETECTION SYSTEM")
    print("=" * 60)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize system
        config = {}
        if args.max_opportunities != 10:
            config['max_opportunities_to_report'] = args.max_opportunities
        if not args.verbose:
            config['save_results_to_file'] = False
        
        system = MispricingSystem(config)
        
        if args.verbose:
            print("System initialized successfully")
            print(f"Configuration: {system.get_system_status()['config']}")
            print()
        
        # Determine which sports to analyze
        if args.all_sports:
            sports_to_analyze = get_available_sports()
            print(f"Running analysis on all sports: {', '.join(s.upper() for s in sports_to_analyze)}")
        elif args.current_season:
            sports_to_analyze = get_current_season_sports()
            print(f"Running analysis on current season sports: {', '.join(s.upper() for s in sports_to_analyze)}")
        else:
            sports_to_analyze = [args.sport]
            print(f"Running analysis on: {args.sport.upper()}")
        
        print()
        
        # Run analysis
        if len(sports_to_analyze) > 1:
            # Multi-sport analysis
            results = system.run_multi_sport_analysis(sports_to_analyze)
            
            # Display combined results
            if results.get('top_opportunities'):
                print("TOP OPPORTUNITIES ACROSS ALL SPORTS:")
                print("=" * 60)
                for i, opp in enumerate(results['top_opportunities'][:args.max_opportunities], 1):
                    display_opportunity(opp, i)
            else:
                print("No opportunities found across all analyzed sports.")
            
        else:
            # Single sport analysis
            sport = sports_to_analyze[0]
            results = system.run_analysis(sport)
            
            if results['status'] == 'completed':
                # Display opportunities
                if results.get('opportunities'):
                    print("TARGET MISPRICING OPPORTUNITIES:")
                    print("=" * 60)
                    system.print_opportunities_summary(args.max_opportunities)
                else:
                    print("No mispricing opportunities found.")
                    print("This could be because:")
                    print("- No games are currently available")
                    print("- No matching games between Pinnacle and Kalshi")
                    print("- Market prices are too close (no significant edge)")
            else:
                print(f"ERROR Analysis failed: {results.get('error', 'Unknown error')}")
                if results.get('errors'):
                    for error in results['errors']:
                        print(f"   {error.get('error', error)}")
        
        # Display summary
        print(f"\n{'='*60}")
        print("ANALYSIS SUMMARY:")
        if len(sports_to_analyze) > 1:
            summary = results.get('combined_summary', {})
            print(f"Sports Analyzed: {', '.join(sports_to_analyze)}")
            print(f"Total Games Aligned: {summary.get('total_aligned_games', 0)}")
            print(f"Total Opportunities: {summary.get('total_opportunities', 0)}")
            if summary.get('best_overall_edge', 0) > 0:
                print(f"Best Edge Found: {summary['best_overall_edge']:.1%}")
        else:
            if results['status'] == 'completed':
                summary = results.get('summary', {})
                print(f"Sport: {summary.get('sport_analyzed', sport.upper())}")
                print(f"Pinnacle Games: {summary.get('total_pinnacle_games', 0)}")
                print(f"Kalshi Games: {summary.get('total_kalshi_games', 0)}")
                print(f"Aligned Games: {summary.get('successfully_aligned', 0)}")
                print(f"Opportunities: {summary.get('opportunities_found', 0)}")
                if summary.get('best_opportunity_edge', 0) > 0:
                    print(f"Best Edge: {summary['best_opportunity_edge']:.1%}")
                print(f"Analysis Duration: {summary.get('analysis_duration_seconds', 0):.1f}s")
        
        if args.verbose and results.get('status') == 'completed':
            print(f"\nResults saved to: {system.config.get('results_file_path', 'output/latest_results.json')}")
        
        print("\nSUCCESS Analysis complete!")
        
    except KeyboardInterrupt:
        print("\nWARNING  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR Analysis failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def display_opportunity(opp, index):
    """Display a single opportunity in clean format"""
    game_data = opp['game_data']
    pinnacle = game_data['pinnacle_data']
    kalshi = game_data['kalshi_data']
    discrepancy = opp['discrepancy']
    
    print(f"{index}. {pinnacle['away_team']} @ {pinnacle['home_team']}")
    print(f"   Game Time: {pinnacle.get('game_time_display', 'Unknown')}")
    print(f"   Edge: {discrepancy['max_edge']:.1%} | EV: {opp['profit_analysis']['expected_value']:.1%}")
    print(f"   Bet: {discrepancy['recommended_side']} team")
    print()

if __name__ == "__main__":
    main()