#!/usr/bin/env python3
"""
Advanced Usage Examples for Sports Market Data Library

This script demonstrates advanced features like arbitrage detection,
market analysis, and custom provider configurations.
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_client import create_unified_client, ProviderConfig, ProviderType
from market_data_core import Sport


async def arbitrage_detection_example():
    """Example: Finding arbitrage opportunities between providers"""
    print("=== ARBITRAGE DETECTION EXAMPLE ===")
    
    # Create client with both providers
    client = create_unified_client(
        kalshi_config={
            'api_key': os.getenv('KALSHI_API_KEY', 'demo_key'),
            'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'demo_key'),
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    try:
        print("Searching for arbitrage opportunities across NFL games...")
        
        # Look for opportunities with different minimum edges
        edges_to_test = [0.005, 0.01, 0.02, 0.05]  # 0.5%, 1%, 2%, 5%
        
        for min_edge in edges_to_test:
            print(f"\nSearching for opportunities with {min_edge:.1%}+ edge...")
            
            arbitrage_ops = await client.find_arbitrage_opportunities(
                Sport.NFL,
                min_edge=min_edge,
                date_from=datetime.now(),
                date_to=datetime.now() + timedelta(days=7)
            )
            
            if arbitrage_ops:
                print(f"Found {len(arbitrage_ops)} opportunities:")
                for i, opp in enumerate(arbitrage_ops[:3], 1):
                    print(f"  {i}. {opp}")
                    print(f"     Providers: {', '.join(opp.providers_involved)}")
                    print(f"     Total Edge: {opp.total_edge:.2%}")
            else:
                print("No opportunities found at this edge level")
    
    except Exception as e:
        print(f"Error in arbitrage detection: {e}")


async def market_analysis_example():
    """Example: Analyzing market data across providers"""
    print("\n=== MARKET ANALYSIS EXAMPLE ===")
    
    client = create_unified_client(
        kalshi_config={
            'api_key': os.getenv('KALSHI_API_KEY', 'demo_key'),
            'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'demo_key'),
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    try:
        print("Analyzing best quotes across providers...")
        
        # Get best quotes for NFL moneyline markets
        best_quotes = await client.get_best_quotes(Sport.NFL, market_type="moneyline")
        
        print(f"Found best quotes for {len(best_quotes)} games:")
        
        for game_key, quote_data in list(best_quotes.items())[:5]:
            game = quote_data['game']
            quotes = quote_data['best_quotes']
            
            print(f"\n{game.away_team.nickname} @ {game.home_team.nickname}")
            print(f"Date: {game.game_date}")
            
            if quotes:
                for market_type, quote_info in quotes.items():
                    print(f"  {market_type}: {quote_info}")
            else:
                print("  No quotes available")
    
    except Exception as e:
        print(f"Error in market analysis: {e}")


async def custom_provider_configuration():
    """Example: Custom provider configurations"""
    print("\n=== CUSTOM PROVIDER CONFIGURATION ===")
    
    # Create custom provider configurations
    provider_configs = [
        ProviderConfig(
            provider_type=ProviderType.KALSHI,
            config={
                'api_key': os.getenv('KALSHI_API_KEY', 'demo_key'),
                'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'demo_key'),
                'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
            },
            enabled=True,
            priority=1  # Higher priority (lower number)
        ),
        ProviderConfig(
            provider_type=ProviderType.ODDS_API,
            config={
                'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
                'base_url': 'https://api.the-odds-api.com/v4'
            },
            enabled=True,
            priority=2  # Lower priority (higher number)
        )
    ]
    
    # Create unified client with custom config
    from unified_client import UnifiedMarketDataClient
    client = UnifiedMarketDataClient(provider_configs)
    
    try:
        print("Testing custom provider configuration...")
        
        # Check which providers are enabled
        enabled_providers = client.get_enabled_providers()
        print(f"Enabled providers: {[p.value for p in enabled_providers]}")
        
        # Test health of custom configuration
        health = await client.health_check()
        print(f"Overall health: {health['overall_status']}")
        
        for provider, status in health['providers'].items():
            priority = client.providers[ProviderType(provider)]['priority'] if ProviderType(provider) in client.providers else "N/A"
            print(f"  {provider}: {status['status']} (priority: {priority})")
    
    except Exception as e:
        print(f"Error in custom configuration: {e}")


async def provider_filtering_example():
    """Example: Filtering data by specific providers"""
    print("\n=== PROVIDER FILTERING EXAMPLE ===")
    
    client = create_unified_client(
        kalshi_config={
            'api_key': os.getenv('KALSHI_API_KEY', 'demo_key'),
            'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'demo_key'),
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    try:
        print("Getting sports data from specific providers...")
        
        # Get sports from Kalshi only
        print("\n1. Kalshi only:")
        kalshi_sports = await client.get_sports(provider_filter=[ProviderType.KALSHI])
        for provider, response in kalshi_sports.items():
            if response.success:
                print(f"   {provider}: {response.data}")
            else:
                print(f"   {provider} error: {response.error}")
        
        # Get sports from Odds API only
        print("\n2. Odds API only:")
        odds_sports = await client.get_sports(provider_filter=[ProviderType.ODDS_API])
        for provider, response in odds_sports.items():
            if response.success:
                print(f"   {provider}: {response.data}")
            else:
                print(f"   {provider} error: {response.error}")
        
        # Get games from specific provider
        print("\n3. NFL games from Odds API only:")
        odds_games = await client.get_games(
            Sport.NFL,
            provider_filter=[ProviderType.ODDS_API]
        )
        
        for provider, response in odds_games.items():
            if response.success and response.data:
                print(f"   {provider}: {len(response.data)} games")
                for game in response.data[:2]:
                    print(f"     {game.away_team.nickname} @ {game.home_team.nickname}")
            else:
                print(f"   {provider}: No data or error")
    
    except Exception as e:
        print(f"Error in provider filtering: {e}")


async def error_handling_and_resilience():
    """Example: Error handling and system resilience"""
    print("\n=== ERROR HANDLING AND RESILIENCE ===")
    
    # Create client with intentionally bad configuration for one provider
    client = create_unified_client(
        kalshi_config={
            'api_key': 'invalid_key',
            'private_key': 'invalid_key',
            'base_url': 'https://invalid-url.com'
        },
        odds_api_config={
            'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    try:
        print("Testing system resilience with mixed provider health...")
        
        # Check authentication with mixed results
        print("\n1. Authentication test:")
        auth_results = await client.authenticate_all()
        for provider, success in auth_results.items():
            print(f"   {provider}: {'✓' if success else '✗'}")
        
        # Health check with mixed results
        print("\n2. Health check:")
        health = await client.health_check()
        print(f"   Overall status: {health['overall_status']}")
        
        for provider, status in health['providers'].items():
            status_icon = {'healthy': '✓', 'unhealthy': '!', 'error': '✗', 'disabled': '-'}.get(status['status'], '?')
            print(f"   {provider}: {status_icon} {status['status']}")
            if status.get('error'):
                print(f"      Error: {status['error']}")
        
        # Try to get data despite failures
        print("\n3. Data retrieval with partial failures:")
        sports_response = await client.get_sports()
        
        successful_providers = 0
        for provider, response in sports_response.items():
            if response.success:
                successful_providers += 1
                print(f"   ✓ {provider}: {len(response.data)} sports")
            else:
                print(f"   ✗ {provider}: {response.error}")
        
        print(f"\n   Result: {successful_providers}/{len(sports_response)} providers successful")
        print("   System continues to function with available providers!")
    
    except Exception as e:
        print(f"Unexpected error: {e}")


async def performance_monitoring():
    """Example: Performance monitoring and metrics"""
    print("\n=== PERFORMANCE MONITORING ===")
    
    client = create_unified_client(
        kalshi_config={
            'api_key': os.getenv('KALSHI_API_KEY', 'demo_key'),
            'private_key': os.getenv('KALSHI_PRIVATE_KEY', 'demo_key'),
            'base_url': 'https://demo-api.kalshi.co/trade-api/v2'
        },
        odds_api_config={
            'api_key': os.getenv('ODDS_API_KEY', 'demo_key'),
            'base_url': 'https://api.the-odds-api.com/v4'
        }
    )
    
    try:
        print("Monitoring performance across multiple operations...")
        
        operations = [
            ("Health Check", client.health_check()),
            ("Get Sports", client.get_sports()),
            ("Get NFL Games", client.get_unified_games(Sport.NFL)),
        ]
        
        for operation_name, operation_coro in operations:
            print(f"\n{operation_name}:")
            start_time = datetime.now()
            
            try:
                result = await operation_coro
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"  Duration: {duration:.3f}s")
                
                if hasattr(result, 'items'):  # Dict-like response
                    successful = sum(1 for r in result.values() if getattr(r, 'success', True))
                    total = len(result)
                    print(f"  Success rate: {successful}/{total} providers")
                elif isinstance(result, list):  # List response
                    print(f"  Results: {len(result)} items")
                elif hasattr(result, 'get'):  # Health check response
                    print(f"  Status: {result.get('overall_status', 'unknown')}")
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                print(f"  Duration: {duration:.3f}s (failed)")
                print(f"  Error: {e}")
    
    except Exception as e:
        print(f"Error in performance monitoring: {e}")


async def main():
    """Run all advanced examples"""
    print("Sports Market Data Library - Advanced Usage Examples")
    print("=" * 60)
    
    examples = [
        arbitrage_detection_example,
        market_analysis_example,
        custom_provider_configuration,
        provider_filtering_example,
        error_handling_and_resilience,
        performance_monitoring
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"Example {example_func.__name__} failed: {e}")
        
        print()  # Add spacing between examples
    
    print("=" * 60)
    print("Advanced examples completed!")
    print("\nNOTE: These examples require valid API keys to work with real data.")
    print("The examples demonstrate the library's resilience by continuing to work")
    print("even when some providers are unavailable or misconfigured.")


if __name__ == "__main__":
    asyncio.run(main())