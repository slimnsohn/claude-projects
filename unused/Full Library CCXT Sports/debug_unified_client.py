#!/usr/bin/env python3
"""
Debug Unified Client Issues
Identify and fix problems with the unified client authentication and provider integration.
"""

import asyncio
import sys
from pathlib import Path
import traceback

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_unified_client_config, print_config_status
from unified_client import create_unified_client
from market_data_core import Sport


async def debug_step_by_step():
    """Debug each step of the unified client process"""
    print("=== UNIFIED CLIENT DEBUG SESSION ===")
    print()
    
    # Step 1: Check configuration
    print("1. Checking configuration...")
    try:
        config = get_unified_client_config()
        print(f"   Configuration loaded: {list(config.keys())}")
        
        if 'kalshi_config' in config:
            kalshi_config = config['kalshi_config']
            print(f"   Kalshi API Key: {kalshi_config.get('api_key')[:10]}...")
            print(f"   Kalshi Private Key length: {len(kalshi_config.get('private_key', ''))}")
            print(f"   Kalshi Base URL: {kalshi_config.get('base_url')}")
        
        if 'odds_api_config' in config:
            odds_config = config['odds_api_config']
            print(f"   Odds API Key: {odds_config.get('api_key')[:10]}...")
            print(f"   Odds Base URL: {odds_config.get('base_url')}")
        
    except Exception as e:
        print(f"   ERROR in configuration: {e}")
        traceback.print_exc()
        return False
    
    print("   OK - Configuration loaded successfully")
    print()
    
    # Step 2: Test individual clients first
    print("2. Testing individual client creation...")
    
    # Test Kalshi client
    if 'kalshi_config' in config:
        try:
            from market_data_kalshi import KalshiClient
            print("   Testing Kalshi client...")
            kalshi_client = KalshiClient(config['kalshi_config'])
            print("   OK - Kalshi client created")
            
            # Test authentication
            try:
                print("   Testing Kalshi authentication...")
                auth_success = await kalshi_client.authenticate()
                print(f"   Kalshi auth result: {auth_success}")
            except Exception as e:
                print(f"   Kalshi auth failed: {e}")
                
        except Exception as e:
            print(f"   ERROR creating Kalshi client: {e}")
            traceback.print_exc()
    
    # Test Odds API client
    if 'odds_api_config' in config:
        try:
            from market_data_odds import OddsAPIClient
            print("   Testing Odds API client...")
            odds_client = OddsAPIClient(config['odds_api_config'])
            print("   OK - Odds API client created")
            
            # Test authentication
            try:
                print("   Testing Odds API authentication...")
                auth_success = await odds_client.authenticate()
                print(f"   Odds API auth result: {auth_success}")
            except Exception as e:
                print(f"   Odds API auth failed: {e}")
                
        except Exception as e:
            print(f"   ERROR creating Odds API client: {e}")
            traceback.print_exc()
    
    print()
    
    # Step 3: Test unified client creation
    print("3. Testing unified client creation...")
    try:
        unified_client = create_unified_client(
            kalshi_config=config.get('kalshi_config'),
            odds_api_config=config.get('odds_api_config')
        )
        print("   OK - Unified client created")
        
        # Check enabled providers
        enabled = unified_client.get_enabled_providers()
        print(f"   Enabled providers: {[p.value for p in enabled]}")
        
    except Exception as e:
        print(f"   ERROR creating unified client: {e}")
        traceback.print_exc()
        return False
    
    print()
    
    # Step 4: Test unified authentication
    print("4. Testing unified authentication...")
    try:
        auth_results = await unified_client.authenticate_all()
        print("   Authentication results:")
        for provider, success in auth_results.items():
            print(f"     {provider}: {success}")
        
        successful_providers = sum(1 for success in auth_results.values() if success)
        print(f"   {successful_providers} of {len(auth_results)} providers authenticated")
        
    except Exception as e:
        print(f"   ERROR in unified authentication: {e}")
        traceback.print_exc()
        return False
    
    print()
    
    # Step 5: Test basic data operations
    print("5. Testing basic data operations...")
    try:
        # Test health check
        print("   Testing health check...")
        health = await unified_client.health_check()
        print(f"   Overall health: {health.get('overall_status', 'unknown')}")
        
        # Test sports retrieval
        print("   Testing sports retrieval...")
        sports_response = await unified_client.get_sports()
        print(f"   Sports responses from {len(sports_response)} providers:")
        
        for provider, response in sports_response.items():
            if response.success:
                print(f"     {provider}: OK - {len(response.data or [])} sports")
            else:
                print(f"     {provider}: ERROR - {response.error}")
        
    except Exception as e:
        print(f"   ERROR in data operations: {e}")
        traceback.print_exc()
        return False
    
    print()
    print("=== DEBUG COMPLETED ===")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(debug_step_by_step())
        if success:
            print("DEBUG: All systems appear functional")
        else:
            print("DEBUG: Issues identified - see output above")
    except Exception as e:
        print(f"DEBUG: Critical error - {e}")
        traceback.print_exc()