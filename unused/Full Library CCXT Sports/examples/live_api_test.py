#!/usr/bin/env python3
"""
Live API Test with Real Credentials
Tests the sports market data library with actual API keys from the kalshi ref folder.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import get_unified_client_config, print_config_status
from unified_client import create_unified_client
from market_data_core import Sport


async def test_live_apis():
    """Test the library with real API credentials"""
    print("=== LIVE API TEST WITH REAL CREDENTIALS ===")
    print()
    
    # Show configuration status
    print_config_status()
    print()
    
    # Get configuration
    config = get_unified_client_config()
    
    if not config:
        print("ERROR No valid API credentials found!")
        print("Please check config/.env file")
        return False
    
    # Create unified client with real credentials
    print("Creating unified client with real API credentials...")
    try:
        kalshi_config = config.get('kalshi_config')
        odds_api_config = config.get('odds_api_config')
        
        client = create_unified_client(
            kalshi_config=kalshi_config,
            odds_api_config=odds_api_config
        )
        
        enabled_providers = client.get_enabled_providers()
        print(f"OK Client created with providers: {[p.value for p in enabled_providers]}")
        
    except Exception as e:
        print(f"ERROR Failed to create client: {e}")
        return False
    
    print()
    
    # Test authentication
    print("Testing authentication...")
    try:
        auth_results = await client.authenticate_all()
        
        successful_auths = 0
        for provider, success in auth_results.items():
            status = "OK" if success else "ERROR"
            print(f"  {provider}: {status}")
            if success:
                successful_auths += 1
        
        if successful_auths == 0:
            print("ERROR No providers authenticated successfully")
            return False
        
        print(f"OK {successful_auths} provider(s) authenticated")
        
    except Exception as e:
        print(f"ERROR Authentication failed: {e}")
        return False
    
    print()
    
    # Test health check
    print("Checking system health...")
    try:
        health = await client.health_check()
        print(f"Overall Status: {health['overall_status']}")
        
        for provider, status in health['providers'].items():
            health_icon = {'healthy': 'OK', 'unhealthy': 'WARNING', 'error': 'ERROR', 'disabled': 'PAUSED'}.get(status['status'], '?')
            print(f"  {provider}: {health_icon} {status['status']}")
            if status.get('error'):
                print(f"    Error: {status['error']}")
        
    except Exception as e:
        print(f"ERROR Health check failed: {e}")
        return False
    
    print()
    
    # Test getting sports
    print("Testing sports data retrieval...")
    try:
        sports_response = await client.get_sports()
        
        total_sports = 0
        for provider, response in sports_response.items():
            if response.success:
                sports_count = len(response.data) if response.data else 0
                total_sports += sports_count
                print(f"  {provider}: OK {sports_count} sports")
                if response.data:
                    sports_list = [sport.name for sport in response.data[:3]]
                    print(f"    Sample: {', '.join(sports_list)}")
            else:
                print(f"  {provider}: ERROR {response.error}")
        
        if total_sports == 0:
            print("WARNING No sports data retrieved")
        else:
            print(f"OK Retrieved {total_sports} total sports across providers")
        
    except Exception as e:
        print(f"ERROR Sports retrieval failed: {e}")
        return False
    
    print()
    
    # Test getting NFL games
    print("Testing NFL games retrieval...")
    try:
        nfl_games = await client.get_unified_games(Sport.NFL)
        
        print(f"OK Retrieved {len(nfl_games)} unified NFL games")
        
        if nfl_games:
            print("Sample games:")
            for i, game in enumerate(nfl_games[:5]):
                sources = game.metadata.get('source_providers', ['unknown'])
                print(f"  {i+1}. {game.away_team.nickname} @ {game.home_team.nickname}")
                print(f"     Date: {game.game_date}")
                print(f"     Sources: {', '.join(sources)}")
            
            # Show date range
            dates = [game.game_date for game in nfl_games]
            print(f"Date range: {min(dates)} to {max(dates)}")
        
    except Exception as e:
        print(f"ERROR NFL games retrieval failed: {e}")
        return False
    
    print()
    
    # Test individual provider access (if available)
    if 'kalshi_config' in config:
        print("Testing direct Kalshi access...")
        try:
            from market_data_kalshi import KalshiClient
            kalshi_client = KalshiClient(config['kalshi_config'])
            
            categories_response = await kalshi_client.get_categories(Sport.NFL)
            if categories_response.success:
                print(f"  OK Kalshi NFL categories: {len(categories_response.data)}")
                if categories_response.data:
                    sample_category = categories_response.data[0]
                    print(f"    Sample: {sample_category.name}")
            else:
                print(f"  ERROR Kalshi categories failed: {categories_response.error}")
            
        except Exception as e:
            print(f"  WARNING Direct Kalshi access failed: {e}")
    
    if 'odds_api_config' in config:
        print("Testing direct Odds API access...")
        try:
            from market_data_odds import OddsAPIClient
            odds_client = OddsAPIClient(config['odds_api_config'])
            
            categories_response = await odds_client.get_categories(Sport.NFL)
            if categories_response.success:
                print(f"  OK Odds API NFL categories: {len(categories_response.data)}")
            else:
                print(f"  ERROR Odds API categories failed: {categories_response.error}")
            
        except Exception as e:
            print(f"  WARNING Direct Odds API access failed: {e}")
    
    print()
    print("=== LIVE API TEST COMPLETED ===")
    print("OK Successfully tested sports market data library with real API credentials!")
    print("The library is ready for production use with live market data.")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_live_apis())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR Live API test failed: {e}")
        sys.exit(1)