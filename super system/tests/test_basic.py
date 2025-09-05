#!/usr/bin/env python3
"""
Basic integration tests for the Sports Analytics Platform
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from config import Sport, BetType, Provider
        print("  [PASS] Config imports successful")
    except ImportError as e:
        print(f"  [FAIL] Config import failed: {e}")
        return False
    
    try:
        from models import Game, Odds, Order, Position
        print("  [PASS] Models imports successful")
    except ImportError as e:
        print(f"  [FAIL] Models import failed: {e}")
        return False
    
    try:
        from market_data.base import DataProvider
        print("  [PASS] Base classes import successful")
    except ImportError as e:
        print(f"  [FAIL] Base classes import failed: {e}")
        return False
    
    try:
        from market_data.aggregator import MarketDataAggregator
        print("  [PASS] Aggregator import successful")
    except ImportError as e:
        print(f"  [FAIL] Aggregator import failed: {e}")
        return False
    
    return True

def test_basic_model_creation():
    """Test basic model object creation"""
    print("\nTesting basic model creation...")
    
    try:
        from config import Sport, Provider, BetType
        from models import Game, Odds
        
        # Test Game creation
        game = Game(
            game_id="test_001",
            sport=Sport.NFL,
            home_team="KC",
            away_team="BUF",
            start_time=datetime.now()
        )
        print("  [PASS] Game creation successful")
        
        # Test Odds creation
        odds = Odds(
            provider=Provider.ODDS_API,
            bet_type=BetType.MONEYLINE,
            timestamp=datetime.now(),
            home_ml=-110,
            away_ml=100
        )
        print("  [PASS] Odds creation successful")
        
        # Test adding odds to game
        game.add_odds("test_odds", odds)
        assert len(game.odds) == 1
        print("  [PASS] Adding odds to game successful")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Model creation failed: {e}")
        return False

def test_aggregator_initialization():
    """Test aggregator can be initialized"""
    print("\nTesting aggregator initialization...")
    
    try:
        from market_data.aggregator import MarketDataAggregator
        from config import Provider
        
        # Test with empty providers (should not crash)
        aggregator = MarketDataAggregator(providers=[])
        # Note: Some clients might still be initialized despite empty providers
        print(f"  [PASS] Empty aggregator initialization successful (clients: {len(aggregator.clients)})")
        
        # Test provider status
        status = aggregator.get_provider_status()
        print(f"  [PASS] Provider status check successful: {status}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Aggregator initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_odds_api_client_creation():
    """Test that Odds API client can be created (without making actual calls)"""
    print("\nTesting Odds API client creation...")
    
    try:
        from market_data.odds_api.production.client import OddsAPIClient
        
        # This should fail without API key, which is expected
        try:
            client = OddsAPIClient()
            print("  [WARN]  Odds API client created (API key must be set)")
        except ValueError as e:
            if "ODDS_API_KEY" in str(e):
                print("  [PASS] Odds API client correctly requires API key")
            else:
                raise
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Odds API client test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    try:
        from config import constants, settings
        
        # Test that enums are accessible
        from config.constants import Sport, Provider, BetType, PROVIDER_SPORT_MAPPING
        
        assert len(Sport) > 0
        assert len(Provider) > 0
        assert len(BetType) > 0
        assert len(PROVIDER_SPORT_MAPPING) > 0
        
        print("  [PASS] Constants loaded successfully")
        
        # Test that settings can be imported (even if values are None)
        from config.settings import ODDS_API_KEY, LOG_LEVEL
        print("  [PASS] Settings loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Configuration loading failed: {e}")
        return False

def test_directory_structure():
    """Test that expected directories and files exist"""
    print("\nTesting directory structure...")
    
    expected_dirs = [
        "config",
        "market_data", 
        "models",
        "tests",
        "utils"
    ]
    
    expected_files = [
        "main.py",
        "requirements.txt",
        ".env.example"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_name in expected_dirs:
        if not os.path.isdir(dir_name):
            missing_dirs.append(dir_name)
    
    for file_name in expected_files:
        if not os.path.isfile(file_name):
            missing_files.append(file_name)
    
    if missing_dirs:
        print(f"  [FAIL] Missing directories: {missing_dirs}")
        return False
    else:
        print("  [PASS] All expected directories present")
    
    if missing_files:
        print(f"  [FAIL] Missing files: {missing_files}")
        return False
    else:
        print("  [PASS] All expected files present")
    
    return True

def run_all_basic_tests():
    """Run all basic tests"""
    print("Running Basic Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Module Imports", test_imports),
        ("Configuration Loading", test_configuration_loading),
        ("Model Creation", test_basic_model_creation),
        ("Aggregator Initialization", test_aggregator_initialization),
        ("Odds API Client", test_odds_api_client_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"PASSED: {test_name}")
            else:
                print(f"FAILED: {test_name}")
        except Exception as e:
            print(f"ERROR: {test_name} - {e}")
    
    print(f"\nTEST SUMMARY")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("All basic tests passed!")
        return True
    else:
        print("Some tests failed. Check output above.")
        return False

if __name__ == "__main__":
    success = run_all_basic_tests()
    sys.exit(0 if success else 1)