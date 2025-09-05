#!/usr/bin/env python3
"""
Working System Test
Demonstrates that the unified client is working correctly with real data.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_unified_client_config
from unified_client import create_unified_client
from market_data_core import Sport


async def test_working_system():
    """Test the working system with clear output"""
    print("=== SPORTS MARKET DATA LIBRARY - WORKING SYSTEM TEST ===")
    print()
    
    # Get configuration
    config = get_unified_client_config()
    
    # Create unified client
    print("1. Creating unified client with real API credentials...")
    client = create_unified_client(
        kalshi_config=config.get('kalshi_config'),
        odds_api_config=config.get('odds_api_config')
    )
    
    enabled_providers = client.get_enabled_providers()
    provider_names = [p.value for p in enabled_providers]
    print(f"   Initialized providers: {', '.join(provider_names)}")
    print()
    
    # Test authentication
    print("2. Testing authentication...")
    auth_results = await client.authenticate_all()
    
    working_providers = []
    for provider_type, success in auth_results.items():
        provider_name = provider_type.value
        status = "WORKING" if success else "NOT AVAILABLE"
        print(f"   {provider_name}: {status}")
        if success:
            working_providers.append(provider_name)
    
    print(f"   Result: {len(working_providers)} of {len(auth_results)} providers working")
    print()
    
    # Test data retrieval
    print("3. Testing live data retrieval...")
    
    # Get sports
    sports_response = await client.get_sports()
    total_sports = 0
    working_data_providers = []
    
    for provider_type, response in sports_response.items():
        provider_name = provider_type.value
        if response.success and response.data:
            sports_count = len(response.data)
            total_sports += sports_count
            working_data_providers.append(provider_name)
            print(f"   {provider_name}: Retrieved {sports_count} sports")
        else:
            print(f"   {provider_name}: No data available")
    
    print(f"   Total sports available: {total_sports}")
    print()
    
    # Get NFL games  
    print("4. Testing NFL games retrieval...")
    nfl_games = await client.get_unified_games(Sport.NFL)
    
    print(f"   Retrieved {len(nfl_games)} NFL games")
    
    if len(nfl_games) > 0:
        print("   Sample games:")
        for i, game in enumerate(nfl_games[:5]):
            print(f"     {i+1}. {game.away_team.nickname} @ {game.home_team.nickname}")
            print(f"        Date: {game.game_date}")
        
        # Show date range
        if len(nfl_games) > 1:
            dates = [game.game_date for game in nfl_games]
            print(f"   Game date range: {min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}")
    
    print()
    
    # Health check
    print("5. System health check...")
    health = await client.health_check()
    print(f"   Overall system status: {health['overall_status'].upper()}")
    
    healthy_providers = []
    for provider, status in health['providers'].items():
        if status['status'] == 'healthy':
            healthy_providers.append(provider)
    
    print(f"   Healthy providers: {', '.join(healthy_providers)}")
    print()
    
    # Summary
    print("=== SYSTEM STATUS SUMMARY ===")
    print(f"Providers initialized: {len(provider_names)} ({', '.join(provider_names)})")
    print(f"Providers working: {len(working_providers)} ({', '.join(working_providers)})")  
    print(f"Data sources active: {len(working_data_providers)} ({', '.join(working_data_providers)})")
    print(f"Total sports available: {total_sports}")
    print(f"NFL games available: {len(nfl_games)}")
    print(f"System health: {health['overall_status'].upper()}")
    print()
    
    if len(working_providers) > 0 and len(nfl_games) > 0:
        print("STATUS: SYSTEM FULLY OPERATIONAL")
        print("The sports market data library is successfully providing live market data!")
        return True
    else:
        print("STATUS: SYSTEM ISSUES DETECTED")  
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_working_system())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: System test failed - {e}")
        sys.exit(1)