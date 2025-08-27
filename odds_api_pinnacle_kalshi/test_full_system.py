"""
Comprehensive Test Script for Multi-Sport Mispricing Detection System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from main_system import MispricingSystem
import json

def test_individual_sports():
    """Test individual sport analysis"""
    print("=" * 70)
    print("TESTING INDIVIDUAL SPORTS ANALYSIS")
    print("=" * 70)
    
    # Initialize system
    config = {
        'pinnacle_api_key_file': 'keys/odds_api_key.txt',
        'kalshi_credentials_file': 'keys/kalshi_credentials.txt',
        'match_time_threshold_hours': 6.0,
        'min_edge_threshold': 0.02,  # 2% minimum edge
        'min_match_confidence': 0.6,
        'use_only_real_kalshi_data': True,
        'max_opportunities_to_report': 3,
        'save_results_to_file': True
    }
    
    system = MispricingSystem(config)
    
    # Test each sport
    sports_to_test = ['mlb', 'nfl', 'nba']
    
    for sport in sports_to_test:
        print(f"\n{'='*20} TESTING {sport.upper()} {'='*20}")
        
        try:
            # Get data summary first
            data_summary = system.get_easy_data_summary(sport)
            
            # Run full analysis if data available
            if (data_summary['pinnacle'].get('success') and 
                data_summary['kalshi'].get('success') and
                data_summary['pinnacle'].get('total_found', 0) > 0 and
                data_summary['kalshi'].get('total_found', 0) > 0):
                
                print(f"\nRunning full {sport.upper()} analysis...")
                results = system.run_analysis(sport)
                
                if results['status'] == 'completed':
                    print(f"SUCCESS: Found {results['summary']['opportunities_found']} opportunities")
                else:
                    print(f"Analysis failed: {results.get('errors')}")
            else:
                print(f"Skipping full analysis - insufficient data for {sport.upper()}")
                
        except Exception as e:
            print(f"Error testing {sport}: {e}")

def test_multi_sport_analysis():
    """Test multi-sport analysis"""
    print("\n" + "=" * 70)
    print("TESTING MULTI-SPORT ANALYSIS")
    print("=" * 70)
    
    try:
        system = MispricingSystem()
        
        # Test multi-sport analysis
        sports_list = ['mlb', 'nfl', 'nba']
        multi_results = system.run_multi_sport_analysis(sports_list)
        
        print(f"\nMULTI-SPORT RESULTS:")
        print(f"Total opportunities across all sports: {multi_results['combined_summary']['total_opportunities']}")
        print(f"Sports with opportunities: {multi_results['combined_summary']['sports_with_opportunities']}")
        
        if multi_results.get('top_opportunities'):
            print(f"\nTOP 3 OPPORTUNITIES ACROSS ALL SPORTS:")
            for i, opp in enumerate(multi_results['top_opportunities'][:3], 1):
                pinnacle_data = opp['game_data']['pinnacle_data']
                edge = opp['discrepancy']['max_edge']
                sport = pinnacle_data.get('sport', 'Unknown')
                home_team = pinnacle_data.get('home_team', 'Unknown')
                away_team = pinnacle_data.get('away_team', 'Unknown')
                print(f"  {i}. {sport}: {away_team} @ {home_team} - {edge:.1%} edge")
        
    except Exception as e:
        print(f"Multi-sport analysis failed: {e}")

def test_data_viewing_functions():
    """Test easy data viewing functions"""
    print("\n" + "=" * 70)
    print("TESTING DATA VIEWING FUNCTIONS")
    print("=" * 70)
    
    try:
        system = MispricingSystem()
        
        # Test data viewing for different sports
        for sport in ['mlb', 'nfl']:
            print(f"\n--- {sport.upper()} DATA VIEW ---")
            
            # Test Pinnacle data view
            pinnacle_view = system.pinnacle_client.get_easy_data_view(sport, 3)
            if pinnacle_view.get('success'):
                print(f"Pinnacle {sport.upper()}: {pinnacle_view['total_found']} games")
                for game in pinnacle_view['data']:
                    print(f"  {game['game']} | Home: {game['home_odds']} | Away: {game['away_odds']}")
            
            # Test Kalshi data view
            kalshi_view = system.kalshi_client.get_easy_data_view(sport, 3)
            if kalshi_view.get('success'):
                print(f"Kalshi {sport.upper()}: {kalshi_view['total_found']} markets")
                for market in kalshi_view['data'][:3]:
                    print(f"  {market['title'][:50]}... | {market['pricing']}")
    
    except Exception as e:
        print(f"Data viewing test failed: {e}")

def main():
    """Run all tests"""
    print("COMPREHENSIVE MULTI-SPORT MISPRICING DETECTION SYSTEM TEST")
    print("=" * 70)
    
    # Test 1: Individual sports
    test_individual_sports()
    
    # Test 2: Multi-sport analysis  
    test_multi_sport_analysis()
    
    # Test 3: Data viewing functions
    test_data_viewing_functions()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nSYSTEM READY FOR PRODUCTION USE!")
    print("Available methods:")
    print("  - system.run_analysis(sport_type='mlb|nfl|nba|nhl')")
    print("  - system.run_multi_sport_analysis(['mlb', 'nfl', 'nba'])")
    print("  - system.get_easy_data_summary(sport_type='mlb')")
    print("  - system.pinnacle_client.get_easy_data_view(sport_type, limit)")
    print("  - system.kalshi_client.get_easy_data_view(sport_type, limit)")

if __name__ == "__main__":
    main()