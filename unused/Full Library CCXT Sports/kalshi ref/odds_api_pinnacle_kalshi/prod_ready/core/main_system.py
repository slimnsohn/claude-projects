"""
Main Integration System - Mispricing Detection Between Pinnacle and Kalshi
Production-ready orchestration module for complete system operation
"""

import json
from datetime import datetime, timezone, timedelta
import pytz
from typing import Dict, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.timestamp_utils import format_display_time
from core.pinnacle_client import PinnacleClient
from core.kalshi_client import KalshiClientUpdated as KalshiClient
from core.odds_converter import OddsConverter
from core.data_aligner import GameMatcher, MispricingDetector
from config.sports_config import get_sport_config, get_available_sports, get_supported_sports_display

class MispricingSystem:
    """Main system for detecting mispricing opportunities between Pinnacle and Kalshi"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the mispricing detection system
        
        Args:
            config: Configuration dictionary with system parameters
        """
        # Start with default config and merge any provided config
        self.config = self._get_default_config()
        if config:
            self.config.update(config)
        self.central_tz = pytz.timezone('America/Chicago')
        
        # Initialize clients
        self.pinnacle_client = PinnacleClient(self.config['pinnacle_api_key_file'])
        self.kalshi_client = KalshiClient(self.config['kalshi_credentials_file'])
        
        # Initialize analysis tools with default values
        # These will be updated per-sport in run_analysis
        self.game_matcher = GameMatcher(time_threshold_hours=6.0)
        self.mispricing_detector = MispricingDetector(
            min_edge_threshold=0.03,
            min_confidence=0.4
        )
        
        # Results storage
        self.last_run_results = {}
    
    def _convert_to_central_time(self, utc_timestamp: str) -> str:
        """Convert UTC timestamp to Central Time with simplified format"""
        try:
            # Parse UTC timestamp
            if utc_timestamp.endswith('Z'):
                utc_timestamp = utc_timestamp[:-1] + '+00:00'
            
            utc_dt = datetime.fromisoformat(utc_timestamp)
            if utc_dt.tzinfo is None:
                utc_dt = utc_dt.replace(tzinfo=timezone.utc)
            
            # Convert to Central Time with simple format
            central_dt = utc_dt.astimezone(self.central_tz)
            return central_dt.strftime('%b %d, %H:%M CST')
            
        except Exception:
            # Use simplified display format as fallback
            return format_display_time(utc_timestamp)
    
    def _get_default_config(self) -> Dict:
        """Get default system configuration"""
        # Get absolute paths relative to the project root
        # File is in prod_ready/core/main_system.py, so project root is 2 levels up
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return {
            'pinnacle_api_key_file': os.path.join(project_root, 'keys', 'odds_api_key.txt'),
            'kalshi_credentials_file': os.path.join(project_root, 'keys', 'kalshi_credentials.txt'),
            'use_only_real_kalshi_data': True,  # No mock data, only real markets
            'min_time_buffer_minutes': 15,  # Minimum minutes before game starts
            'exclude_live_games': True,  # Never analyze games that have started
            'max_opportunities_to_report': 10,
            'save_results_to_file': True,
            'results_file_path': os.path.join(project_root, 'debug', 'latest_results.json')
        }
    
    def run_analysis(self, sport_type: str = 'mlb') -> Dict:
        """
        Run complete mispricing analysis pipeline
        
        Args:
            sport_type: Sport to analyze. Available: {}
        
        Returns:
            Dictionary containing analysis results and opportunities
        """.format(get_supported_sports_display())
        # Get sport configuration
        sport_config = get_sport_config(sport_type)
        if not sport_config:
            return {
                'status': 'failed',
                'error': f'Unsupported sport: {sport_type}. Available: {get_supported_sports_display()}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        # Update analysis tools with sport-specific settings
        self.game_matcher.time_threshold = timedelta(hours=sport_config.time_threshold_hours)
        self.mispricing_detector.min_edge = sport_config.min_edge_threshold
        self.mispricing_detector.min_confidence = sport_config.match_confidence_threshold
        
        print(f"Starting Pinnacle-Kalshi {sport_config.name} Mispricing Analysis")
        if self.config.get('exclude_live_games', True):
            buffer_mins = self.config.get('min_time_buffer_minutes', 15)
            print(f"Note: Excluding live games (minimum {buffer_mins} minutes before start)")
        print(f"Sport Config: Edge>={sport_config.min_edge_threshold:.1%}, Confidence>={sport_config.match_confidence_threshold:.1%}")
        print("=" * 60)
        
        analysis_start = datetime.now(timezone.utc)
        results = {
            'timestamp': analysis_start.isoformat(),
            'status': 'running',
            'pinnacle_data': {},
            'kalshi_data': {},
            'aligned_games': [],
            'opportunities': [],
            'summary': {},
            'errors': []
        }
        
        try:
            # Step 1: Fetch Pinnacle data
            print(f"Step 1: Fetching Pinnacle {sport_type.upper()} odds...")
            pinnacle_raw = self.pinnacle_client.get_sports_odds(sport_type)
            
            if not pinnacle_raw.get('success'):
                raise Exception(f"Pinnacle data fetch failed: {pinnacle_raw.get('error')}")
            
            # Apply time filtering if configured
            time_buffer = self.config.get('min_time_buffer_minutes', 15)
            pinnacle_games = self.pinnacle_client.normalize_pinnacle_data(pinnacle_raw, time_buffer)
            results['pinnacle_data'] = {
                'success': True,
                'games_count': len(pinnacle_games),
                'raw_games_count': len(pinnacle_raw.get('data', [])),
                'fetch_timestamp': pinnacle_raw.get('timestamp')
            }
            print(f"  SUCCESS: Fetched {len(pinnacle_games)} Pinnacle {sport_type.upper()} games")
            
            # Step 2: Fetch Kalshi sports markets
            print(f"Step 2: Fetching Kalshi {sport_type.upper()} markets...")
            print(f"  Searching for {sport_type} sports markets on Kalshi...")
            
            kalshi_raw = self.kalshi_client.search_sports_markets(sport_type)
            kalshi_games = self.kalshi_client.normalize_kalshi_data(kalshi_raw, time_buffer)
            
            if len(kalshi_games) == 0:
                print(f"  No {sport_type.upper()} markets found on Kalshi")
                print(f"  Note: Kalshi may not have individual {sport_type.upper()} games available today")
            else:
                print(f"  Found {len(kalshi_games)} real {sport_type.upper()} markets on Kalshi")
            
            if not kalshi_raw.get('success'):
                raise Exception(f"Kalshi data fetch failed: {kalshi_raw.get('error')}")
            
            results['kalshi_data'] = {
                'success': True,
                'games_count': len(kalshi_games),
                'data_source': 'real' if len(kalshi_games) > 0 else 'none',
                'fetch_timestamp': kalshi_raw.get('timestamp')
            }
            print(f"  SUCCESS: Fetched {len(kalshi_games)} Kalshi {sport_type.upper()} games")
            
            # Step 3: Align games between platforms
            print("Step 3: Aligning games between platforms...")
            aligned_games = self.game_matcher.align_games(pinnacle_games, kalshi_games)
            results['aligned_games'] = aligned_games
            print(f"  SUCCESS: Aligned {len(aligned_games)} games")
            
            # Step 4: Detect mispricing opportunities
            print("Step 4: Detecting mispricing opportunities...")
            opportunities = self.mispricing_detector.detect_opportunities(aligned_games)
            
            # Sort opportunities by edge size
            opportunities.sort(
                key=lambda x: x['discrepancy']['max_edge'],
                reverse=True
            )
            
            # Limit number of opportunities
            max_opportunities = self.config['max_opportunities_to_report']
            if len(opportunities) > max_opportunities:
                opportunities = opportunities[:max_opportunities]
            
            results['opportunities'] = opportunities
            print(f"  SUCCESS: Found {len(opportunities)} opportunities")
            
            # Step 5: Generate summary
            analysis_end = datetime.now(timezone.utc)
            duration = (analysis_end - analysis_start).total_seconds()
            
            results['summary'] = {
                'sport_analyzed': sport_type.upper(),
                'total_pinnacle_games': len(pinnacle_games),
                'total_kalshi_games': len(kalshi_games),
                'successfully_aligned': len(aligned_games),
                'opportunities_found': len(opportunities),
                'best_opportunity_edge': opportunities[0]['discrepancy']['max_edge'] if opportunities else 0,
                'analysis_duration_seconds': round(duration, 2),
                'system_config': self.config
            }
            
            results['status'] = 'completed'
            print(f"\nAnalysis completed in {duration:.1f} seconds")
            
        except Exception as e:
            results['status'] = 'failed'
            results['errors'].append({
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            print(f"\nAnalysis failed: {e}")
        
        # Store results
        self.last_run_results = results
        
        # Save to file if configured
        if self.config.get('save_results_to_file'):
            self._save_results_to_file(results)
        
        return results
    
    def _save_results_to_file(self, results: Dict):
        """Save analysis results to JSON file"""
        try:
            file_path = self.config.get('results_file_path', '../debug/latest_results.json')
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save results: {e}")
    
    def print_opportunities_summary(self, max_display: int = 5):
        """Print a formatted summary of the best opportunities"""
        if not self.last_run_results or not self.last_run_results.get('opportunities'):
            print("No opportunities to display")
            return
        
        opportunities = self.last_run_results['opportunities'][:max_display]
        
        print(f"\n{'='*60}")
        print("TOP MISPRICING OPPORTUNITIES")
        print(f"{'='*60}")
        
        for i, opp in enumerate(opportunities, 1):
            game_data = opp['game_data']
            pinnacle = game_data['pinnacle_data']
            kalshi = game_data['kalshi_data']
            discrepancy = opp['discrepancy']
            
            # Use simplified display time
            display_time = pinnacle.get('game_time_display', pinnacle.get('game_time', 'Unknown'))
            print(f"\n{i}. {pinnacle['away_team']} @ {pinnacle['home_team']}")
            print(f"   Game Time: {display_time}")
            print(f"   Match Confidence: {game_data['match_confidence']:.1%}")
            print(f"   Max Edge: {discrepancy['max_edge']:.1%}")
            print(f"   Recommended Side: {discrepancy['recommended_side']}")
            print(f"   Expected Value: {opp['profit_analysis']['expected_value']:.1%}")
            print(f"   Kelly Fraction: {opp['profit_analysis']['kelly_fraction']:.1%}")
            
            # Show odds comparison
            home_side = "home_team"
            away_side = "away_team"
            
            if discrepancy['recommended_side'] == 'home':
                print(f"   Pinnacle {pinnacle['home_team']}: {pinnacle['home_odds']['american']:+d}")
                print(f"   Kalshi {kalshi['home_team']}: {kalshi['home_odds']['american']:+d}")
            else:
                print(f"   Pinnacle {pinnacle['away_team']}: {pinnacle['away_odds']['american']:+d}")
                print(f"   Kalshi {kalshi['away_team']}: {kalshi['away_odds']['american']:+d}")
        
        if len(self.last_run_results['opportunities']) > max_display:
            remaining = len(self.last_run_results['opportunities']) - max_display
            print(f"\n... and {remaining} more opportunities")
    
    def get_system_status(self) -> Dict:
        """Get current system status and configuration"""
        return {
            'system_ready': True,
            'config': self.config,
            'last_run': self.last_run_results.get('timestamp'),
            'last_run_status': self.last_run_results.get('status'),
            'clients_initialized': {
                'pinnacle': self.pinnacle_client is not None,
                'kalshi': self.kalshi_client is not None
            }
        }
    
    def run_multi_sport_analysis(self, sports_list: List[str] = None) -> Dict:
        """Run analysis across multiple sports"""
        if sports_list is None:
            sports_list = get_available_sports()
        
        print(f"Starting Multi-Sport Analysis: {', '.join(s.upper() for s in sports_list)}")
        print("="*70)
        
        multi_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sports_analyzed': sports_list,
            'individual_results': {},
            'combined_summary': {
                'total_opportunities': 0,
                'total_aligned_games': 0,
                'best_overall_edge': 0,
                'sports_with_opportunities': []
            }
        }
        
        all_opportunities = []
        
        for sport in sports_list:
            print(f"\n{'='*20} ANALYZING {sport.upper()} {'='*20}")
            sport_results = self.run_analysis(sport)
            multi_results['individual_results'][sport] = sport_results
            
            if sport_results.get('opportunities'):
                all_opportunities.extend(sport_results['opportunities'])
                multi_results['combined_summary']['sports_with_opportunities'].append(sport.upper())
            
            multi_results['combined_summary']['total_aligned_games'] += len(sport_results.get('aligned_games', []))
        
        # Sort all opportunities by edge
        if all_opportunities:
            all_opportunities.sort(key=lambda x: x['discrepancy']['max_edge'], reverse=True)
            multi_results['combined_summary']['total_opportunities'] = len(all_opportunities)
            multi_results['combined_summary']['best_overall_edge'] = all_opportunities[0]['discrepancy']['max_edge']
            multi_results['top_opportunities'] = all_opportunities[:10]  # Top 10 across all sports
        
        # Print combined summary
        print(f"\n{'='*70}")
        print("MULTI-SPORT ANALYSIS SUMMARY")
        print(f"{'='*70}")
        summary = multi_results['combined_summary']
        print(f"Sports Analyzed: {', '.join(sports_list)}")
        print(f"Total Games Aligned: {summary['total_aligned_games']}")
        print(f"Total Opportunities: {summary['total_opportunities']}")
        print(f"Sports with Opportunities: {', '.join(summary['sports_with_opportunities'])}")
        if summary['best_overall_edge'] > 0:
            print(f"Best Overall Edge: {summary['best_overall_edge']:.1%}")
        
        return multi_results
    
    def get_easy_data_summary(self, sport_type: str = 'mlb') -> Dict:
        """Get easy-to-read summary of available data for a sport"""
        print(f"\nGETTING DATA SUMMARY FOR {sport_type.upper()}")
        print("-" * 50)
        
        # Get Pinnacle data view
        print("Fetching Pinnacle data...")
        pinnacle_view = self.pinnacle_client.get_easy_data_view(sport_type, 10)
        
        # Get Kalshi data view  
        print("Fetching Kalshi data...")
        kalshi_view = self.kalshi_client.get_easy_data_view(sport_type, 10)
        
        summary = {
            'sport': sport_type.upper(),
            'pinnacle': pinnacle_view,
            'kalshi': kalshi_view,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Print summary
        print(f"\nDATA AVAILABILITY SUMMARY - {sport_type.upper()}:")
        if pinnacle_view.get('success'):
            print(f"  Pinnacle: {pinnacle_view['total_found']} games available")
        else:
            print(f"  Pinnacle: Error - {pinnacle_view.get('error', 'Unknown')}")
        
        if kalshi_view.get('success'):
            print(f"  Kalshi: {kalshi_view['total_found']} markets available")
        else:
            print(f"  Kalshi: Error - {kalshi_view.get('error', 'Unknown')}")
        
        return summary

def run_demo():
    """Run a demonstration of the complete system"""
    print("PINNACLE-KALSHI MISPRICING DETECTION SYSTEM")
    print("Demo Mode - Production Ready Implementation")
    print("=" * 60)
    
    # Initialize system with demo configuration (use default paths)
    config = {
        'use_only_real_kalshi_data': True,  # No mock data
        'max_opportunities_to_report': 5,
        'save_results_to_file': True
    }
    
    system = MispricingSystem(config)
    
    # Run analysis for MLB
    results = system.run_analysis('nfl')
    
    # Display results
    if results['status'] == 'completed':
        print(f"\nSUMMARY:")
        summary = results['summary']
        print(f"  Pinnacle Games: {summary['total_pinnacle_games']}")
        kalshi_info = results['kalshi_data']['data_source']
        print(f"  Kalshi Games: {summary['total_kalshi_games']} ({kalshi_info})")
        print(f"  Games Aligned: {summary['successfully_aligned']}")
        print(f"  Opportunities: {summary['opportunities_found']}")
        
        if summary['opportunities_found'] > 0:
            print(f"  Best Edge: {summary['best_opportunity_edge']:.1%}")
            
            # Show opportunities
            system.print_opportunities_summary()
        
        print(f"\nAnalysis Duration: {summary['analysis_duration_seconds']} seconds")
        print(f"System Status: OPERATIONAL")
        
    else:
        print(f"\nAnalysis failed. Check errors: {results.get('errors')}")
    
    return system, results

if __name__ == "__main__":
    run_demo()