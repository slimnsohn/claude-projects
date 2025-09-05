#!/usr/bin/env python3
"""
Trace Data Source
Verify where the game data is actually coming from - API or local files.
"""

import asyncio
import sys
from pathlib import Path
import traceback

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_unified_client_config
from unified_client import create_unified_client
from market_data_core import Sport


async def trace_data_sources():
    """Trace where data is actually coming from"""
    print("=== TRACING DATA SOURCES ===")
    print()
    
    # Get configuration
    config = get_unified_client_config()
    
    # Test Odds API client directly first
    print("1. Testing Odds API client directly for NFL games...")
    try:
        from market_data_odds import OddsAPIClient
        
        odds_client = OddsAPIClient(config.get('odds_api_config'))
        
        # Authenticate
        auth_result = await odds_client.authenticate()
        print(f"   Odds API authentication: {auth_result}")
        
        if auth_result:
            # Get NFL games directly from API
            print("   Fetching NFL games directly from Odds API...")
            nfl_response = await odds_client.get_games(Sport.NFL)
            
            if nfl_response.success:
                api_games = nfl_response.data or []
                print(f"   Direct from Odds API: {len(api_games)} NFL games")
                
                if api_games:
                    sample_game = api_games[0]
                    print(f"   Sample API game: {sample_game.away_team.nickname} @ {sample_game.home_team.nickname}")
                    print(f"   Sample game date: {sample_game.game_date}")
                    print(f"   Sample metadata: {sample_game.metadata}")
                    
                    # Check if this looks like real API data
                    game_dates = [game.game_date for game in api_games[:10]]
                    print(f"   First 10 game dates: {[d.strftime('%Y-%m-%d %H:%M') for d in game_dates]}")
                else:
                    print("   No games returned from API")
            else:
                print(f"   API error: {nfl_response.error}")
        else:
            print("   Authentication failed - cannot get API data")
            
    except Exception as e:
        print(f"   Error testing direct API: {e}")
        traceback.print_exc()
    
    print()
    
    # Test Kalshi client directly
    print("2. Testing Kalshi client directly for NFL games...")
    try:
        from market_data_kalshi import KalshiClient
        
        kalshi_client = KalshiClient(config.get('kalshi_config'))
        
        # Authenticate
        auth_result = await kalshi_client.authenticate()
        print(f"   Kalshi authentication: {auth_result}")
        
        if auth_result:
            # Get NFL games directly from API
            print("   Fetching NFL games directly from Kalshi...")
            nfl_response = await kalshi_client.get_games(Sport.NFL)
            
            if nfl_response.success:
                api_games = nfl_response.data or []
                print(f"   Direct from Kalshi: {len(api_games)} NFL games")
                
                if api_games:
                    sample_game = api_games[0]
                    print(f"   Sample Kalshi game: {sample_game.away_team.nickname} @ {sample_game.home_team.nickname}")
                    print(f"   Sample game date: {sample_game.game_date}")
            else:
                print(f"   Kalshi API error: {nfl_response.error}")
        else:
            print("   Kalshi authentication failed - cannot get API data")
            
    except Exception as e:
        print(f"   Error testing Kalshi: {e}")
    
    print()
    
    # Now test unified client
    print("3. Testing unified client...")
    try:
        unified_client = create_unified_client(
            kalshi_config=config.get('kalshi_config'),
            odds_api_config=config.get('odds_api_config')
        )
        
        # Get games through unified interface
        print("   Getting games through unified client...")
        unified_games = await unified_client.get_unified_games(Sport.NFL)
        
        print(f"   Unified client returned: {len(unified_games)} games")
        
        if unified_games:
            # Analyze the source of games
            sources_count = {}
            
            for game in unified_games:
                source_providers = game.metadata.get('source_providers', game.metadata.get('source_provider', 'unknown'))
                if isinstance(source_providers, list):
                    for provider in source_providers:
                        sources_count[provider] = sources_count.get(provider, 0) + 1
                else:
                    sources_count[source_providers] = sources_count.get(source_providers, 0) + 1
            
            print(f"   Game sources: {sources_count}")
            
            # Show sample games with source info
            print("   Sample unified games:")
            for i, game in enumerate(unified_games[:5]):
                source_info = game.metadata.get('source_providers', game.metadata.get('source_provider', 'unknown'))
                print(f"     {i+1}. {game.away_team.nickname} @ {game.home_team.nickname}")
                print(f"        Date: {game.game_date}")
                print(f"        Source: {source_info}")
                print(f"        All metadata: {game.metadata}")
        
    except Exception as e:
        print(f"   Error testing unified client: {e}")
        traceback.print_exc()
    
    print()
    
    # Check local data files for comparison
    print("4. Checking local NFL data for comparison...")
    try:
        from market_data_core import get_nfl_data_manager
        
        nfl_data = get_nfl_data_manager()
        local_games = list(nfl_data.games.values())
        
        print(f"   Local NFL data: {len(local_games)} games")
        
        if local_games:
            local_dates = [game.game_date for game in local_games[:5]]
            print(f"   Local game dates: {[d.strftime('%Y-%m-%d %H:%M') for d in local_dates]}")
            
            sample_local = local_games[0]
            print(f"   Sample local: {sample_local.away_team.nickname} @ {sample_local.home_team.nickname}")
            print(f"   Sample local date: {sample_local.game_date}")
        
    except Exception as e:
        print(f"   Error checking local data: {e}")
    
    print()
    print("=== DATA SOURCE ANALYSIS COMPLETE ===")


if __name__ == "__main__":
    try:
        asyncio.run(trace_data_sources())
    except Exception as e:
        print(f"Analysis failed: {e}")
        traceback.print_exc()