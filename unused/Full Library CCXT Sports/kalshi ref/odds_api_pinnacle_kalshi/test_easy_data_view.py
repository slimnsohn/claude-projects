"""
Test script to demonstrate easy data viewing functions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated
import json

def test_easy_data_views():
    """Test easy data viewing functions for both platforms"""
    print("=" * 60)
    print("TESTING EASY DATA VIEWING FUNCTIONS")
    print("=" * 60)
    
    try:
        # Test Pinnacle easy data view
        print("\n1. PINNACLE EASY DATA VIEW")
        print("-" * 40)
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        pinnacle_view = pinnacle.get_easy_data_view('mlb', 5)
        
        if pinnacle_view.get('success'):
            print(f"Found {pinnacle_view['total_found']} Pinnacle games, showing {pinnacle_view['showing']}:")
            for game in pinnacle_view['data']:
                print(f"  {game['game']} | Home: {game['home_odds']} | Away: {game['away_odds']}")
        else:
            print(f"Pinnacle data view failed: {pinnacle_view.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Pinnacle test failed: {e}")
    
    try:
        # Test Kalshi easy data view
        print("\n2. KALSHI EASY DATA VIEW")
        print("-" * 40)
        kalshi = KalshiClientUpdated("keys/kalshi_credentials.txt")
        kalshi_view = kalshi.get_easy_data_view('mlb', 5)
        
        if kalshi_view.get('success'):
            print(f"Found {kalshi_view['total_found']} Kalshi markets, showing {kalshi_view['showing']}:")
            for market in kalshi_view['data']:
                print(f"  {market['title'][:50]}... | {market['pricing']} | {market['sport']}")
        else:
            print(f"Kalshi data view failed: {kalshi_view.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Kalshi test failed: {e}")
    
    print("\n" + "=" * 60)
    print("EASY DATA VIEW TEST COMPLETED")
    print("=" * 60)

def test_comprehensive_sports_search():
    """Test multi-sport search capabilities"""
    print("\n" + "=" * 60)
    print("TESTING COMPREHENSIVE SPORTS SEARCH")
    print("=" * 60)
    
    try:
        kalshi = KalshiClientUpdated("keys/kalshi_credentials.txt")
        
        # Test all sports search
        print("\n1. KALSHI ALL SPORTS SEARCH")
        print("-" * 40)
        all_sports = kalshi.search_sports_markets('all')
        
        if all_sports.get('success'):
            sport_counts = all_sports.get('sport_counts', {})
            print(f"Total sports markets found: {len(all_sports['data'])}")
            print("Sport breakdown:")
            for sport, count in sorted(sport_counts.items()):
                print(f"  {sport.upper()}: {count} markets")
        
        # Test specific sport searches
        for sport in ['mlb', 'nfl', 'nba']:
            print(f"\n2. KALSHI {sport.upper()} SPECIFIC SEARCH")
            print("-" * 40)
            sport_data = kalshi.search_sports_markets(sport)
            if sport_data.get('success'):
                print(f"Found {len(sport_data['data'])} {sport.upper()} markets")
                # Show first few
                for market in sport_data['data'][:3]:
                    print(f"  - {market.get('ticker')}: {market.get('title', '')[:60]}...")
    
    except Exception as e:
        print(f"Comprehensive sports search failed: {e}")

if __name__ == "__main__":
    test_easy_data_views()
    test_comprehensive_sports_search()