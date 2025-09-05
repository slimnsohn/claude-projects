#!/usr/bin/env python3
"""
Test Individual Clients
Test Kalshi and Odds API clients individually with the fixed configuration.
"""

import asyncio
import sys
from pathlib import Path
import traceback
import pytest

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_unified_client_config
from market_data_core import Sport


@pytest.mark.asyncio
async def test_kalshi_client():
    """Test Kalshi client individually"""
    print("=== TESTING KALSHI CLIENT ===")
    
    config = get_unified_client_config()
    kalshi_config = config.get('kalshi_config')
    
    if not kalshi_config:
        print("ERROR: No Kalshi configuration found")
        return False
    
    print(f"API Key: {kalshi_config.get('api_key')}")
    print(f"Private Key Length: {len(kalshi_config.get('private_key', ''))}")
    print(f"Base URL: {kalshi_config.get('base_url')}")
    print()
    
    try:
        from market_data_kalshi import KalshiClient
        
        print("Creating Kalshi client...")
        client = KalshiClient(kalshi_config)
        print("OK: Client created successfully")
        
        print("Testing authentication...")
        auth_result = await client.authenticate()
        print(f"Authentication result: {auth_result}")
        
        if auth_result:
            print("Testing get_sports...")
            sports_response = await client.get_sports()
            if sports_response.success:
                print(f"OK: Retrieved {len(sports_response.data)} sports")
                print(f"Sports: {[s.name for s in sports_response.data]}")
            else:
                print(f"ERROR: get_sports failed - {sports_response.error}")
        
        return auth_result
        
    except Exception as e:
        print(f"ERROR: Kalshi client failed - {e}")
        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_odds_api_client():
    """Test Odds API client individually"""
    print("=== TESTING ODDS API CLIENT ===")
    
    config = get_unified_client_config()
    odds_config = config.get('odds_api_config')
    
    if not odds_config:
        print("ERROR: No Odds API configuration found")
        return False
    
    print(f"API Key: {odds_config.get('api_key')[:8]}...")
    print(f"Base URL: {odds_config.get('base_url')}")
    print()
    
    try:
        from market_data_odds import OddsAPIClient
        
        print("Creating Odds API client...")
        client = OddsAPIClient(odds_config)
        print("OK: Client created successfully")
        
        print("Testing authentication...")
        auth_result = await client.authenticate()
        print(f"Authentication result: {auth_result}")
        
        if auth_result:
            print("Testing get_sports...")
            sports_response = await client.get_sports()
            if sports_response.success:
                print(f"OK: Retrieved {len(sports_response.data)} sports")
                print(f"Sports: {[s.name for s in sports_response.data[:5]]}")
            else:
                print(f"ERROR: get_sports failed - {sports_response.error}")
        
        return auth_result
        
    except Exception as e:
        print(f"ERROR: Odds API client failed - {e}")
        traceback.print_exc()
        return False


async def main():
    """Test both individual clients"""
    print("INDIVIDUAL CLIENT TESTING")
    print("=" * 50)
    print()
    
    # Test Kalshi
    kalshi_ok = await test_kalshi_client()
    print()
    
    # Test Odds API
    odds_ok = await test_odds_api_client()
    print()
    
    # Summary
    print("=" * 50)
    print("INDIVIDUAL CLIENT SUMMARY:")
    print(f"Kalshi Client: {'OK' if kalshi_ok else 'FAILED'}")
    print(f"Odds API Client: {'OK' if odds_ok else 'FAILED'}")
    
    if kalshi_ok or odds_ok:
        print("STATUS: At least one client is working")
        return True
    else:
        print("STATUS: Both clients failed")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)