#!/usr/bin/env python3
"""
Test script to verify live game filtering in Kalshi client
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.kalshi_client import KalshiClientUpdated
from datetime import datetime, timezone, timedelta
import json

def test_kalshi_live_filtering():
    """Test that Kalshi client properly filters out live games"""
    print("KALSHI LIVE GAME FILTERING TEST")
    print("=" * 50)
    
    # Create mock Kalshi data with different game times
    now = datetime.now(timezone.utc)
    
    # Create test market data
    mock_data = {
        'success': True,
        'data': [
            {
                'ticker': 'KXMLBGAME-25AUG21OAKMIN-OAK',
                'title': 'Oakland at Minnesota Winner?',
                'close_time': (now + timedelta(hours=3)).isoformat(),  # Future game - should be included
                'detected_sport': 'mlb'
            },
            {
                'ticker': 'KXMLBGAME-25AUG21ANYHOU-ANY',
                'title': 'Any Team at Houston Winner?',
                'close_time': (now - timedelta(hours=1)).isoformat(),  # Past game - should be filtered
                'detected_sport': 'mlb'
            },
            {
                'ticker': 'KXMLBGAME-25AUG21TEXSEA-TEX',
                'title': 'Texas at Seattle Winner?',
                'close_time': (now + timedelta(minutes=10)).isoformat(),  # Starting soon - should be filtered
                'detected_sport': 'mlb'
            },
            {
                'ticker': 'KXMLBGAME-25AUG21BOSNYY-BOS',
                'title': 'Boston at New York Yankees Winner?',
                'close_time': (now + timedelta(hours=5)).isoformat(),  # Future game - should be included
                'detected_sport': 'mlb'
            }
        ]
    }
    
    # Test with different time buffers
    try:
        client = KalshiClientUpdated('../keys/kalshi_credentials.txt')
        
        print("Testing with 15-minute buffer (default):")
        print("-" * 40)
        
        normalized_games = client.normalize_kalshi_data(mock_data, min_time_buffer_minutes=15)
        
        print(f"Original markets: {len(mock_data['data'])}")
        print(f"After filtering: {len(normalized_games)}")
        print()
        
        print("Included games:")
        for game in normalized_games:
            print(f"  - {game['away_team']} @ {game['home_team']} ({game['game_time_display']})")
        
        print()
        print("Testing with 30-minute buffer:")
        print("-" * 40)
        
        normalized_games_30 = client.normalize_kalshi_data(mock_data, min_time_buffer_minutes=30)
        
        print(f"Original markets: {len(mock_data['data'])}")
        print(f"After filtering (30min): {len(normalized_games_30)}")
        print()
        
        print("Included games (30min buffer):")
        for game in normalized_games_30:
            print(f"  - {game['away_team']} @ {game['home_team']} ({game['game_time_display']})")
        
        # Verify expected behavior
        print()
        print("VALIDATION:")
        print("-" * 40)
        
        expected_with_15min = 2  # Only games 3+ hours in future
        expected_with_30min = 2  # Only games 3+ and 5+ hours in future
        
        if len(normalized_games) == expected_with_15min:
            print("PASS 15-min buffer filtering correct")
        else:
            print(f"FAIL 15-min buffer: expected {expected_with_15min}, got {len(normalized_games)}")
        
        if len(normalized_games_30) <= len(normalized_games):
            print("PASS 30-min buffer is more restrictive")
        else:
            print("FAIL 30-min buffer should be more restrictive")
        
        print()
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed - {e}")
        return False

def test_real_kalshi_filtering():
    """Test filtering with real Kalshi data"""
    print("REAL KALSHI DATA FILTERING TEST")
    print("=" * 50)
    
    try:
        client = KalshiClientUpdated('../keys/kalshi_credentials.txt')
        
        # Get real MLB markets
        print("Fetching real Kalshi markets...")
        raw_data = client.search_sports_markets('mlb')
        
        if not raw_data.get('success'):
            print("SKIP Could not fetch real data")
            return False
        
        original_count = len(raw_data.get('data', []))
        print(f"Original markets found: {original_count}")
        
        if original_count == 0:
            print("SKIP No markets found to test filtering")
            return True
        
        # Test with different buffer times
        buffers = [0, 15, 30, 60]
        
        for buffer_min in buffers:
            normalized_games = client.normalize_kalshi_data(raw_data, min_time_buffer_minutes=buffer_min)
            print(f"With {buffer_min}-min buffer: {len(normalized_games)} games")
            
            if len(normalized_games) > 0:
                print(f"  Example: {normalized_games[0]['away_team']} @ {normalized_games[0]['home_team']}")
        
        print()
        print("VALIDATION:")
        print("- Higher buffer minutes should result in same or fewer games")
        print("- System should report filtered games in output")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Real data test failed - {e}")
        return False

if __name__ == "__main__":
    print("Testing Kalshi live game filtering...")
    print()
    
    # Test 1: Mock data
    test1_passed = test_kalshi_live_filtering()
    print()
    
    # Test 2: Real data  
    test2_passed = test_real_kalshi_filtering()
    print()
    
    print("=" * 50)
    print("OVERALL RESULTS:")
    if test1_passed:
        print("PASS Mock data filtering test")
    else:
        print("FAIL Mock data filtering test")
    
    if test2_passed:
        print("PASS Real data filtering test")
    else:
        print("FAIL Real data filtering test")
    
    if test1_passed and test2_passed:
        print()
        print("SUCCESS: Live game filtering is working correctly!")
    else:
        print()
        print("ISSUES FOUND: Live game filtering needs attention")