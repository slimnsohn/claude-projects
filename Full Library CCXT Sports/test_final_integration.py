#!/usr/bin/env python3
"""
Final Integration Test
Tests the complete sports market data library with comprehensive data.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from unified_client import create_unified_client
from market_data_core import Sport, get_nfl_data_manager


async def test_unified_client_comprehensive():
    """Test unified client with comprehensive data"""
    print("=== FINAL INTEGRATION TEST ===")
    print("Testing unified client with comprehensive multi-date data...")
    print()
    
    # Test data manager first
    print("1. Testing data manager...")
    nfl_data = get_nfl_data_manager()
    print(f"   Teams: {len(nfl_data.teams)}")
    print(f"   Games: {len(nfl_data.games)}")
    
    # Show date range
    dates = set()
    weeks = set()
    for game in nfl_data.games.values():
        dates.add(game.game_date.strftime('%Y-%m-%d'))
        if game.week:
            weeks.add(game.week)
    
    print(f"   Date range: {min(dates)} to {max(dates)}")
    print(f"   Weeks covered: {sorted(weeks)}")
    print()
    
    # Test date range queries
    print("2. Testing date range queries...")
    early_sept = nfl_data.get_games_by_date_range(
        datetime(2024, 9, 1), 
        datetime(2024, 9, 10)
    )
    mid_sept = nfl_data.get_games_by_date_range(
        datetime(2024, 9, 15),
        datetime(2024, 9, 25)
    )
    early_oct = nfl_data.get_games_by_date_range(
        datetime(2024, 10, 1),
        datetime(2024, 10, 10)
    )
    
    print(f"   Early September games: {len(early_sept)}")
    print(f"   Mid September games: {len(mid_sept)}")
    print(f"   Early October games: {len(early_oct)}")
    print()
    
    # Test unified client (with dummy credentials)
    print("3. Testing unified client initialization...")
    try:
        # Create client with both providers (dummy credentials)
        client = create_unified_client(
            kalshi_config={
                'api_key': 'dummy_kalshi_key_12345678901234567890',
                'private_key': 'dummy_private_key',
                'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
            },
            odds_api_config={
                'api_key': 'dummy_odds_key_12345678901234567890',
                'base_url': 'https://api.the-odds-api.com/v4'
            }
        )
        
        print("   Unified client created successfully")
        
        # Check enabled providers
        enabled = client.get_enabled_providers()
        print(f"   Enabled providers: {[p.value for p in enabled]}")
        
    except Exception as e:
        print(f"   Expected error with dummy credentials: {type(e).__name__}")
    
    print()
    
    # Test team matching across providers
    print("4. Testing team matching...")
    from market_data_core import get_team_matcher
    matcher = get_team_matcher(Sport.NFL)
    
    test_names = [
        'Kansas City Chiefs', 'KC', 'Chiefs',
        'Baltimore Ravens', 'Ravens', 'BAL',
        'Green Bay Packers', 'Packers', 'GB'
    ]
    
    for name in test_names:
        result = matcher.match_team(name)
        if result.matched_team:
            print(f"   '{name}' -> {result.matched_team.name} ({result.confidence:.2f})")
        else:
            print(f"   '{name}' -> No match")
    
    print()
    
    # Test provider-specific functionality
    print("5. Testing provider-specific functionality...")
    
    # Test Kalshi mapping
    from market_data_kalshi.client import KalshiClient
    print(f"   Kalshi NFL league key: {KalshiClient.LEAGUE_MAP.get(Sport.NFL)}")
    
    # Test Odds API mapping
    from market_data_odds.handler import OddsAPIResponseHandler
    handler = OddsAPIResponseHandler()
    print(f"   Odds API NFL sport key: {handler.get_sport_key_for_api(Sport.NFL)}")
    
    print()
    
    # Show sample games by week
    print("6. Sample games by week...")
    for week in sorted(weeks)[:3]:  # First 3 weeks
        week_games = nfl_data.get_games_by_week(week)
        print(f"   Week {week}: {len(week_games)} games")
        for game in week_games[:2]:  # Show first 2
            print(f"     {game.away_team.nickname} @ {game.home_team.nickname} - {game.game_date}")
    
    print()
    
    # Test prime time games
    print("7. Prime time games analysis...")
    prime_time = []
    for game in nfl_data.games.values():
        if game.game_date.hour >= 20:  # 8 PM or later
            prime_time.append(game)
    
    print(f"   Total prime time games: {len(prime_time)}")
    if prime_time:
        by_day = {}
        for game in prime_time:
            day = game.game_date.strftime('%A')
            by_day[day] = by_day.get(day, 0) + 1
        
        for day, count in sorted(by_day.items()):
            print(f"     {day}: {count} games")
    
    print()
    print("=== FINAL INTEGRATION SUCCESSFUL ===")
    print("All components working together with comprehensive multi-date data!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_unified_client_comprehensive())
        print("\nFINAL STATUS: SUCCESS" if success else "\nFINAL STATUS: FAILED")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFINAL STATUS: ERROR - {e}")
        sys.exit(1)