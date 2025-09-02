"""
Test script to demonstrate live game filtering functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from main_system import MispricingSystem
from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from datetime import datetime, timezone, timedelta

def test_time_buffer_settings():
    """Test different time buffer settings"""
    print("=" * 70)
    print("TESTING LIVE GAME FILTERING WITH DIFFERENT TIME BUFFERS")
    print("=" * 70)
    
    try:
        # Test with different buffer settings
        buffer_settings = [5, 15, 30, 60]  # minutes
        
        for buffer_minutes in buffer_settings:
            print(f"\n{'='*20} TESTING {buffer_minutes} MINUTE BUFFER {'='*20}")
            
            # Configure system with specific buffer
            config = {
                'pinnacle_api_key_file': 'keys/odds_api_key.txt',
                'kalshi_credentials_file': 'keys/kalshi_credentials.txt',
                'min_time_buffer_minutes': buffer_minutes,
                'exclude_live_games': True,
                'min_edge_threshold': 0.02,
                'min_match_confidence': 0.6,
                'max_opportunities_to_report': 3
            }
            
            system = MispricingSystem(config)
            
            # Test with MLB data
            print(f"Testing MLB games with {buffer_minutes} minute buffer...")
            
            # Get raw data first to see total games
            pinnacle_raw = system.pinnacle_client.get_sports_odds('mlb')
            if pinnacle_raw.get('success'):
                total_pinnacle_games = len(pinnacle_raw.get('data', []))
                print(f"  Raw Pinnacle games: {total_pinnacle_games}")
                
                # Apply filtering
                filtered_pinnacle = system.pinnacle_client.normalize_pinnacle_data(pinnacle_raw, buffer_minutes)
                print(f"  Filtered Pinnacle games: {len(filtered_pinnacle)}")
                print(f"  Games filtered out: {total_pinnacle_games - len(filtered_pinnacle)}")
            
            # Test Kalshi filtering
            kalshi_raw = system.kalshi_client.search_sports_markets('mlb')
            if kalshi_raw.get('success'):
                total_kalshi_games = len(kalshi_raw.get('data', []))
                print(f"  Raw Kalshi markets: {total_kalshi_games}")
                
                # Apply filtering
                filtered_kalshi = system.kalshi_client.normalize_kalshi_data(kalshi_raw, buffer_minutes)
                print(f"  Filtered Kalshi markets: {len(filtered_kalshi)}")
                print(f"  Markets filtered out: {total_kalshi_games - len(filtered_kalshi)}")
                
    except Exception as e:
        print(f"Error testing time buffers: {e}")

def test_live_vs_future_games():
    """Test the filtering logic with sample data"""
    print("\n" + "=" * 70)
    print("TESTING LIVE VS FUTURE GAME DETECTION")
    print("=" * 70)
    
    try:
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        # Test different game times
        now = datetime.now(timezone.utc)
        
        test_times = [
            (now - timedelta(hours=1), "1 hour ago (LIVE)"),
            (now - timedelta(minutes=30), "30 minutes ago (LIVE)"),
            (now + timedelta(minutes=5), "5 minutes from now (STARTING SOON)"),
            (now + timedelta(minutes=20), "20 minutes from now (FUTURE)"),
            (now + timedelta(hours=2), "2 hours from now (FUTURE)")
        ]
        
        for test_time, description in test_times:
            time_str = test_time.isoformat() + 'Z'
            
            # Test with different buffer settings
            for buffer_minutes in [15, 30]:
                is_future_pinnacle = pinnacle._is_future_game(time_str, buffer_minutes)
                is_future_kalshi = kalshi._is_future_game(time_str, buffer_minutes)
                
                print(f"  {description}:")
                print(f"    {buffer_minutes}min buffer - Pinnacle: {'INCLUDE' if is_future_pinnacle else 'EXCLUDE'}, "
                      f"Kalshi: {'INCLUDE' if is_future_kalshi else 'EXCLUDE'}")
        
    except Exception as e:
        print(f"Error testing live vs future: {e}")

def test_full_system_with_filtering():
    """Test full system analysis with live game filtering"""
    print("\n" + "=" * 70)
    print("TESTING FULL SYSTEM WITH LIVE GAME FILTERING")
    print("=" * 70)
    
    try:
        # Configure system to be very strict about live games
        strict_config = {
            'pinnacle_api_key_file': 'keys/odds_api_key.txt',
            'kalshi_credentials_file': 'keys/kalshi_credentials.txt',
            'min_time_buffer_minutes': 30,  # 30 minute buffer
            'exclude_live_games': True,
            'min_edge_threshold': 0.01,  # Lower threshold to find more opportunities
            'min_match_confidence': 0.5,
            'max_opportunities_to_report': 5
        }
        
        system = MispricingSystem(strict_config)
        
        # Run analysis
        print("Running MLB analysis with strict live game filtering...")
        results = system.run_analysis('mlb')
        
        if results['status'] == 'completed':
            print(f"\nSTRICT FILTERING RESULTS:")
            summary = results['summary']
            print(f"  Pinnacle games (30min+ buffer): {summary['total_pinnacle_games']}")
            print(f"  Kalshi markets (30min+ buffer): {summary['total_kalshi_games']}")
            print(f"  Successfully aligned: {summary['successfully_aligned']}")
            print(f"  Opportunities found: {summary['opportunities_found']}")
            
            if summary['opportunities_found'] > 0:
                print(f"  Best opportunity edge: {summary['best_opportunity_edge']:.1%}")
                
                # Show sample opportunities
                for i, opp in enumerate(results['opportunities'][:3], 1):
                    pinnacle_data = opp['game_data']['pinnacle_data']
                    game_time = pinnacle_data.get('game_time', 'N/A')
                    edge = opp['discrepancy']['max_edge']
                    home_team = pinnacle_data.get('home_team', 'Unknown')
                    away_team = pinnacle_data.get('away_team', 'Unknown')
                    
                    print(f"  {i}. {away_team} @ {home_team}")
                    print(f"     Edge: {edge:.1%} | Game time: {game_time}")
            
        else:
            print(f"Analysis failed: {results.get('errors')}")
            
    except Exception as e:
        print(f"Error testing full system: {e}")

def main():
    """Run all live game filtering tests"""
    print("LIVE GAME FILTERING TEST SUITE")
    print("=" * 70)
    
    # Test 1: Different time buffer settings
    test_time_buffer_settings()
    
    # Test 2: Live vs future game detection logic
    test_live_vs_future_games()
    
    # Test 3: Full system with filtering
    test_full_system_with_filtering()
    
    print("\n" + "=" * 70)
    print("LIVE GAME FILTERING TESTS COMPLETED")
    print("=" * 70)
    print("\nSYSTEM NOW CONFIGURED TO EXCLUDE LIVE GAMES!")
    print("Configuration options:")
    print("  - min_time_buffer_minutes: Minimum minutes before game start (default: 15)")
    print("  - exclude_live_games: Always filter live games (default: True)")
    print("\nAll analysis will only include games starting at least 15+ minutes in the future.")

if __name__ == "__main__":
    main()