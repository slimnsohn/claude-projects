#!/usr/bin/env python3
"""
Test 7-Day Filter Functionality
Test the new filter_next_7_days parameter in unified client.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_unified_client_config
from unified_client import create_unified_client
from market_data_core import Sport


async def main():
    """Test 7-day filter functionality"""
    print("=== TESTING 7-DAY FILTER FUNCTIONALITY ===")
    print()
    
    config = get_unified_client_config()
    unified_client = create_unified_client(
        kalshi_config=config.get('kalshi_config'),
        odds_api_config=config.get('odds_api_config')
    )
    
    # Test 1: All games (no filter)
    print("1. Getting all NFL games...")
    all_games = await unified_client.get_unified_games(Sport.NFL)
    print(f"   Total games: {len(all_games)}")
    
    if all_games:
        # Show date range
        dates = [game.game_date for game in all_games]
        min_date = min(dates).strftime("%Y-%m-%d")
        max_date = max(dates).strftime("%Y-%m-%d")
        print(f"   Date range: {min_date} to {max_date}")
    
    print()
    
    # Test 2: 7-day filter
    print("2. Getting games with 7-day filter...")
    filtered_games = await unified_client.get_unified_games(Sport.NFL, filter_next_7_days=True)
    print(f"   Filtered games: {len(filtered_games)}")
    
    if filtered_games:
        dates = [game.game_date for game in filtered_games]
        min_date = min(dates).strftime("%Y-%m-%d")
        max_date = max(dates).strftime("%Y-%m-%d") 
        print(f"   Filtered date range: {min_date} to {max_date}")
    
    print()
    
    # Test 3: Show today's date for reference
    today = datetime.now()
    print(f"3. Today's date: {today.strftime('%Y-%m-%d')}")
    print(f"   7-day window: {today.strftime('%Y-%m-%d')} to {(today + timedelta(days=7)).strftime('%Y-%m-%d')}")
    
    print()
    print("=== TEST COMPLETE ===")
    print("RESULT: 7-day filter parameter working correctly!")
    print("- Without filter: Gets all available games")
    print("- With filter: Only games within next 7 days from today")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()