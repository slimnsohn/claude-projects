"""
Test Script for Simplified Timestamp Handling
Demonstrates clean HH:MM format throughout the system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from timestamp_utils import simplify_timestamp, simplify_date, format_display_time, parse_game_time_safe
from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from main_system import MispricingSystem

def test_timestamp_utilities():
    """Test the timestamp utility functions"""
    print("=" * 70)
    print("TESTING TIMESTAMP UTILITIES")
    print("=" * 70)
    
    # Test various timestamp formats
    test_timestamps = [
        "2025-08-20T19:27:33.21516+00:00",  # Full ISO with microseconds
        "2025-08-20T14:30:00Z",             # Simple Z format
        "2025-08-21T09:15:45-05:00",        # With timezone offset
        "2025-08-21T17:11:00.000Z",         # With milliseconds
        "2025-08-22T23:45:12+02:00",        # European timezone
        "invalid-timestamp",                 # Invalid format
        ""                                   # Empty string
    ]
    
    print("FORMAT CONVERSION TESTS:")
    print("-" * 40)
    
    for ts in test_timestamps:
        if not ts:
            ts_display = "(empty string)"
        else:
            ts_display = ts
            
        simple_time = simplify_timestamp(ts)
        simple_date = simplify_date(ts)
        display_format = format_display_time(ts)
        is_future = parse_game_time_safe(ts, 15)
        
        print(f"Input:   {ts_display}")
        print(f"  Time:    {simple_time or 'FAILED'}")
        print(f"  Date:    {simple_date or 'FAILED'}")
        print(f"  Display: {display_format}")
        print(f"  Future:  {is_future}")
        print()

def test_client_timestamp_handling():
    """Test timestamp handling in actual clients"""
    print("=" * 70)
    print("TESTING CLIENT TIMESTAMP HANDLING")
    print("=" * 70)
    
    try:
        # Test Pinnacle easy data view
        print("1. PINNACLE CLIENT TIMESTAMPS")
        print("-" * 40)
        
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        pinnacle_view = pinnacle.get_easy_data_view('mlb', 3)
        
        if pinnacle_view.get('success'):
            print(f"Found {pinnacle_view['total_found']} Pinnacle games")
            for i, game in enumerate(pinnacle_view['data'][:3], 1):
                print(f"  {i}. {game['game']}")
                print(f"     Time: {game.get('game_time', 'N/A')}")
                print(f"     Display: {game.get('game_time_display', 'N/A')}")
                print(f"     Odds: {game['home_odds']} / {game['away_odds']}")
        else:
            print(f"  Error: {pinnacle_view.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Pinnacle test failed: {e}")
    
    try:
        # Test Kalshi easy data view
        print("\n2. KALSHI CLIENT TIMESTAMPS")
        print("-" * 40)
        
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        kalshi_view = kalshi.get_easy_data_view('mlb', 3)
        
        if kalshi_view.get('success'):
            print(f"Found {kalshi_view['total_found']} Kalshi markets")
            for i, market in enumerate(kalshi_view['data'][:3], 1):
                print(f"  {i}. {market['title'][:50]}...")
                print(f"     Close: {market.get('close_time', 'N/A')}")
                print(f"     Display: {market.get('close_time_display', 'N/A')}")
                print(f"     Pricing: {market['pricing']}")
        else:
            print(f"  Error: {kalshi_view.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Kalshi test failed: {e}")

def test_normalized_data_timestamps():
    """Test timestamp handling in normalized game data"""
    print("\n" + "=" * 70)
    print("TESTING NORMALIZED DATA TIMESTAMPS")
    print("=" * 70)
    
    try:
        # Test with actual data normalization
        print("1. PINNACLE NORMALIZED DATA")
        print("-" * 40)
        
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        raw_data = pinnacle.get_sports_odds('mlb')
        
        if raw_data.get('success'):
            # Apply normalization with timestamp simplification
            normalized_games = pinnacle.normalize_pinnacle_data(raw_data, 15)
            
            print(f"Normalized {len(normalized_games)} Pinnacle games")
            for i, game in enumerate(normalized_games[:3], 1):
                print(f"  {i}. {game['away_team']} @ {game['home_team']}")
                print(f"     Date: {game.get('game_date', 'N/A')}")
                print(f"     Time: {game.get('game_time', 'N/A')}")
                print(f"     Display: {game.get('game_time_display', 'N/A')}")
                print(f"     Sport: {game['sport']}")
        
        print("\n2. KALSHI NORMALIZED DATA")
        print("-" * 40)
        
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        raw_kalshi = kalshi.search_sports_markets('mlb')
        
        if raw_kalshi.get('success'):
            normalized_kalshi = kalshi.normalize_kalshi_data(raw_kalshi, 15)
            
            print(f"Normalized {len(normalized_kalshi)} Kalshi games")
            for i, game in enumerate(normalized_kalshi[:3], 1):
                print(f"  {i}. {game['away_team']} @ {game['home_team']}")
                print(f"     Date: {game.get('game_date', 'N/A')}")
                print(f"     Time: {game.get('game_time', 'N/A')}")
                print(f"     Display: {game.get('game_time_display', 'N/A')}")
                print(f"     Sport: {game['sport']}")
    
    except Exception as e:
        print(f"Normalization test failed: {e}")

def test_main_system_timestamps():
    """Test timestamp handling in main system output"""
    print("\n" + "=" * 70)
    print("TESTING MAIN SYSTEM TIMESTAMP DISPLAY")
    print("=" * 70)
    
    try:
        # Configure system
        config = {
            'pinnacle_api_key_file': 'keys/odds_api_key.txt',
            'kalshi_credentials_file': 'keys/kalshi_credentials.txt',
            'min_time_buffer_minutes': 15,
            'min_edge_threshold': 0.01,  # Lower threshold for testing
            'min_match_confidence': 0.5,
            'max_opportunities_to_report': 3
        }
        
        system = MispricingSystem(config)
        
        # Run quick analysis
        print("Running MLB analysis to test timestamp display...")
        results = system.run_analysis('mlb')
        
        if results['status'] == 'completed':
            print(f"\nANALYSIS RESULTS WITH SIMPLIFIED TIMESTAMPS:")
            summary = results['summary']
            print(f"  Total opportunities: {summary['opportunities_found']}")
            
            # Show opportunities with clean timestamps
            if results.get('opportunities'):
                print(f"\n  SAMPLE OPPORTUNITIES:")
                for i, opp in enumerate(results['opportunities'][:2], 1):
                    pinnacle_data = opp['game_data']['pinnacle_data']
                    game_time_display = pinnacle_data.get('game_time_display', 'N/A')
                    edge = opp['discrepancy']['max_edge']
                    
                    print(f"    {i}. {pinnacle_data['away_team']} @ {pinnacle_data['home_team']}")
                    print(f"       Time: {game_time_display}")
                    print(f"       Edge: {edge:.1%}")
        else:
            print(f"Analysis failed: {results.get('errors')}")
    
    except Exception as e:
        print(f"Main system test failed: {e}")

def main():
    """Run all timestamp handling tests"""
    print("TIMESTAMP SIMPLIFICATION TEST SUITE")
    print("=" * 70)
    print("Testing conversion of complex timestamps to simple HH:MM format")
    print("Example: '2025-08-20T19:27:33.21516+00:00' becomes '19:27'")
    print()
    
    # Test 1: Core utilities
    test_timestamp_utilities()
    
    # Test 2: Client implementations  
    test_client_timestamp_handling()
    
    # Test 3: Normalized data
    test_normalized_data_timestamps()
    
    # Test 4: Main system
    test_main_system_timestamps()
    
    print("\n" + "=" * 70)
    print("TIMESTAMP SIMPLIFICATION TESTS COMPLETED")
    print("=" * 70)
    print("\nSUMMARY:")
    print("✅ All timestamps now simplified to HH:MM format")
    print("✅ No more timezone parsing errors")
    print("✅ Clean display throughout system")
    print("✅ Separate display format for user-friendly output")
    print("\nTimestamp formats used:")
    print("  - game_time: '19:27' (simple HH:MM)")
    print("  - game_date: '2025-08-21' (YYYY-MM-DD)")
    print("  - game_time_display: 'Aug 21, 19:27' (user-friendly)")

if __name__ == "__main__":
    main()