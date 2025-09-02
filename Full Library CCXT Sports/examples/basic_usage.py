#!/usr/bin/env python3
"""
Basic Usage Examples for Sports Market Data Library

This script demonstrates how to use the unified sports market data library
to access Kalshi and Odds API data through a single interface.
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_client import create_unified_client
from market_data_core import Sport


async def basic_kalshi_usage():
    """Example: Basic Kalshi API usage"""
    print("=== BASIC KALSHI USAGE ===")
    
    # Configure Kalshi (you'll need real credentials)
    kalshi_config = {
        'api_key': os.getenv('KALSHI_API_KEY', 'your_kalshi_api_key_here'),
        'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'your_private_key_here'),
        'base_url': 'https://demo-api.kalshi.co/trade-api/v2'  # Demo environment
    }
    
    # Create unified client with just Kalshi
    client = create_unified_client(kalshi_config=kalshi_config)
    
    try:
        # Authenticate
        print("Authenticating with Kalshi...")
        auth_results = await client.authenticate_all()
        print(f"Authentication: {auth_results}")
        
        # Get available sports
        print("\nGetting available sports...")
        sports_response = await client.get_sports()
        for provider, response in sports_response.items():
            if response.success:
                print(f"{provider}: {response.data}")
            else:
                print(f"{provider} error: {response.error}")
        
        # Get NFL games
        print("\nGetting NFL games...")
        nfl_games = await client.get_unified_games(Sport.NFL)
        print(f"Found {len(nfl_games)} NFL games")
        
        for game in nfl_games[:3]:  # Show first 3
            print(f"  {game.away_team.nickname} @ {game.home_team.nickname} - {game.game_date}")
            sources = game.metadata.get('source_providers', ['unknown'])
            print(f"    Sources: {sources}")
    
    except Exception as e:
        print(f"Error: {e}")


async def basic_odds_api_usage():
    """Example: Basic Odds API usage"""
    print("\n=== BASIC ODDS API USAGE ===")
    
    # Configure Odds API (you'll need a real API key)
    odds_api_config = {
        'api_key': os.getenv('ODDS_API_KEY', 'your_odds_api_key_here'),
        'base_url': 'https://api.the-odds-api.com/v4'
    }
    
    # Create unified client with just Odds API
    client = create_unified_client(odds_api_config=odds_api_config)
    
    try:
        # Authenticate (simple for Odds API)
        print("Authenticating with Odds API...")
        auth_results = await client.authenticate_all()
        print(f"Authentication: {auth_results}")
        
        # Get available sports
        print("\nGetting available sports...")
        sports_response = await client.get_sports()
        for provider, response in sports_response.items():
            if response.success:
                print(f"{provider}: {response.data}")
            else:
                print(f"{provider} error: {response.error}")
        
        # Get NFL games
        print("\nGetting NFL games...")
        nfl_games = await client.get_unified_games(Sport.NFL)
        print(f"Found {len(nfl_games)} NFL games")
        
        for game in nfl_games[:3]:  # Show first 3
            print(f"  {game.away_team.nickname} @ {game.home_team.nickname} - {game.game_date}")
            sources = game.metadata.get('source_providers', ['unknown'])
            print(f"    Sources: {sources}")
    
    except Exception as e:
        print(f"Error: {e}")


async def unified_multi_provider_usage():
    """Example: Using both providers simultaneously"""
    print("\n=== UNIFIED MULTI-PROVIDER USAGE ===")
    
    # Configure both providers
    kalshi_config = {
        'api_key': os.getenv('KALSHI_API_KEY', 'your_kalshi_api_key_here'),
        'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'your_private_key_here'),
        'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
    }
    
    odds_api_config = {
        'api_key': os.getenv('ODDS_API_KEY', 'your_odds_api_key_here'),
        'base_url': 'https://api.the-odds-api.com/v4'
    }
    
    # Create unified client with both providers
    client = create_unified_client(
        kalshi_config=kalshi_config,
        odds_api_config=odds_api_config
    )
    
    try:
        # Check health of all providers
        print("Checking provider health...")
        health = await client.health_check()
        print(f"Overall status: {health['overall_status']}")
        for provider, status in health['providers'].items():
            print(f"  {provider}: {status['status']} (auth: {status['authenticated']})")
        
        # Get unified games (combining data from both providers)
        print("\nGetting unified NFL games...")
        unified_games = await client.get_unified_games(Sport.NFL)
        print(f"Found {len(unified_games)} unique NFL games")
        
        # Show games with provider sources
        for game in unified_games[:5]:
            sources = game.metadata.get('source_providers', ['unknown'])
            print(f"  {game.away_team.nickname} @ {game.home_team.nickname}")
            print(f"    Date: {game.game_date}")
            print(f"    Sources: {', '.join(sources)}")
        
        # Look for arbitrage opportunities
        print("\nSearching for arbitrage opportunities...")
        arbitrage_ops = await client.find_arbitrage_opportunities(
            Sport.NFL, 
            min_edge=0.01  # 1% minimum edge
        )
        
        if arbitrage_ops:
            print(f"Found {len(arbitrage_ops)} potential opportunities:")
            for opp in arbitrage_ops[:3]:
                print(f"  {opp}")
        else:
            print("No arbitrage opportunities found at this time")
    
    except Exception as e:
        print(f"Error: {e}")


async def individual_provider_access():
    """Example: Accessing individual providers directly"""
    print("\n=== INDIVIDUAL PROVIDER ACCESS ===")
    
    # You can also access individual providers directly
    from market_data_kalshi import KalshiClient
    from market_data_odds import OddsAPIClient
    
    # Direct Kalshi access
    print("Direct Kalshi client usage...")
    kalshi_config = {
        'api_key': os.getenv('KALSHI_API_KEY', 'your_kalshi_api_key_here'),
        'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'your_private_key_here'),
        'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
    }
    
    try:
        kalshi_client = KalshiClient(kalshi_config)
        
        # Get categories (prediction market categories)
        categories_response = await kalshi_client.get_categories(Sport.NFL)
        if categories_response.success:
            print(f"Kalshi NFL categories: {len(categories_response.data)}")
            for category in categories_response.data[:2]:
                print(f"  {category.name}: {category.description}")
    except Exception as e:
        print(f"Kalshi direct access error: {e}")
    
    # Direct Odds API access
    print("\nDirect Odds API client usage...")
    odds_config = {
        'api_key': os.getenv('ODDS_API_KEY', 'your_odds_api_key_here'),
        'base_url': 'https://api.the-odds-api.com/v4'
    }
    
    try:
        odds_client = OddsAPIClient(odds_config)
        
        # Get categories (sports/leagues)
        categories_response = await odds_client.get_categories(Sport.NFL)
        if categories_response.success:
            print(f"Odds API NFL categories: {len(categories_response.data)}")
            for category in categories_response.data:
                print(f"  {category.name}: {category.description}")
    except Exception as e:
        print(f"Odds API direct access error: {e}")


def setup_environment_variables():
    """Show how to set up environment variables for API keys"""
    print("=== ENVIRONMENT SETUP ===")
    print("To use this library with real data, set these environment variables:")
    print()
    print("For Kalshi:")
    print("  export KALSHI_API_KEY='your_actual_kalshi_api_key'")
    print("  export KALSHI_PRIVATE_KEY='your_rsa_private_key_pem_content'")
    print()
    print("For Odds API:")
    print("  export ODDS_API_KEY='your_actual_odds_api_key'")
    print()
    print("Alternatively, create a .env file in your project root:")
    print("  KALSHI_API_KEY=your_actual_kalshi_api_key")
    print("  KALSHI_PRIVATE_KEY=your_rsa_private_key_pem_content")
    print("  ODDS_API_KEY=your_actual_odds_api_key")
    print()


async def main():
    """Run all examples"""
    print("Sports Market Data Library - Usage Examples")
    print("=" * 50)
    
    # Show environment setup first
    setup_environment_variables()
    
    # Run examples (these will fail without real API keys, but show the patterns)
    await basic_kalshi_usage()
    await basic_odds_api_usage()
    await unified_multi_provider_usage()
    await individual_provider_access()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nNOTE: These examples require valid API keys to work with real data.")
    print("Replace 'your_*_key_here' with actual credentials from:")
    print("- Kalshi: https://kalshi.com/")
    print("- The Odds API: https://the-odds-api.com/")


if __name__ == "__main__":
    asyncio.run(main())