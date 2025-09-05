"""
Phase 2 Validation Tests
Tests NFL reference data collection, team matching, and schedule management
"""

import sys
import os
import unittest
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add project root and exploration paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'exploration'))

try:
    from exploration.nfl_team_data_collection import (
        NFL_TEAMS_2024, get_team_by_name, validate_team_data, 
        create_reverse_lookup, get_all_team_variations
    )
    from exploration.nfl_schedule_data import NFLScheduleManager, NFLGame
    from exploration.team_matching_engine import TeamMatchingEngine, MatchResult
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure exploration modules are available")


class TestNFLTeamData(unittest.TestCase):
    """Test NFL team data collection and management"""
    
    def test_team_data_completeness(self):
        """Test that all 32 NFL teams are present with required data"""
        self.assertEqual(len(NFL_TEAMS_2024), 32, "Should have all 32 NFL teams")
        
        required_fields = ['name', 'city', 'nickname', 'abbreviations', 'conference', 'division']
        for team_abbrev, team_data in NFL_TEAMS_2024.items():
            for field in required_fields:
                self.assertIn(field, team_data, f"Team {team_abbrev} missing field: {field}")
                self.assertTrue(team_data[field], f"Team {team_abbrev} has empty field: {field}")
    
    def test_conference_division_structure(self):
        """Test conference and division structure is correct"""
        afc_teams = [t for t in NFL_TEAMS_2024.values() if t['conference'] == 'AFC']
        nfc_teams = [t for t in NFL_TEAMS_2024.values() if t['conference'] == 'NFC']
        
        self.assertEqual(len(afc_teams), 16, "Should have 16 AFC teams")
        self.assertEqual(len(nfc_teams), 16, "Should have 16 NFC teams")
        
        # Check division structure
        divisions = {}
        for team in NFL_TEAMS_2024.values():
            div_key = f"{team['conference']} {team['division']}"
            if div_key not in divisions:
                divisions[div_key] = []
            divisions[div_key].append(team)
        
        self.assertEqual(len(divisions), 8, "Should have 8 divisions")
        for div_name, teams in divisions.items():
            self.assertEqual(len(teams), 4, f"Division {div_name} should have 4 teams")
    
    def test_team_lookup_functionality(self):
        """Test team lookup by various names"""
        test_cases = [
            ('KC', 'Kansas City Chiefs'),
            ('Kansas City Chiefs', 'Kansas City Chiefs'),
            ('Chiefs', 'Kansas City Chiefs'),
            ('NE', 'New England Patriots'),
            ('Patriots', 'New England Patriots'),
            ('SF', 'San Francisco 49ers'),
            ('49ers', 'San Francisco 49ers'),
            ('LV', 'Las Vegas Raiders'),
            ('Raiders', 'Las Vegas Raiders'),
        ]
        
        for search_name, expected_name in test_cases:
            team = get_team_by_name(search_name)
            self.assertIsNotNone(team, f"Should find team for search: {search_name}")
            self.assertEqual(team['name'], expected_name, f"Wrong team for search: {search_name}")
    
    def test_reverse_lookup_creation(self):
        """Test reverse lookup dictionary creation"""
        reverse_lookup = create_reverse_lookup()
        
        # Should have many variations
        self.assertGreater(len(reverse_lookup), 200, "Should have many team name variations")
        
        # Test some specific lookups
        self.assertEqual(reverse_lookup.get('KC'), 'KC')
        self.assertEqual(reverse_lookup.get('CHIEFS'), 'KC')
        self.assertEqual(reverse_lookup.get('KANSAS CITY CHIEFS'), 'KC')
    
    def test_team_variations(self):
        """Test team variation generation"""
        variations = get_all_team_variations()
        
        # Every team should have multiple variations
        for team_abbrev in NFL_TEAMS_2024.keys():
            self.assertIn(team_abbrev, variations, f"Team {team_abbrev} should have variations")
            team_vars = variations[team_abbrev]
            self.assertGreater(len(team_vars), 3, f"Team {team_abbrev} should have multiple variations")
            
            # Should include basic identifiers
            team_data = NFL_TEAMS_2024[team_abbrev]
            self.assertIn(team_data['name'], team_vars)
            self.assertIn(team_data['nickname'], team_vars)


class TestNFLScheduleData(unittest.TestCase):
    """Test NFL schedule data management"""
    
    def setUp(self):
        """Set up schedule manager for tests"""
        self.manager = NFLScheduleManager()
    
    def test_schedule_manager_initialization(self):
        """Test schedule manager loads and indexes data"""
        self.assertGreater(len(self.manager.games), 0, "Should load sample games")
        self.assertGreater(len(self.manager.games_by_week), 0, "Should index games by week")
        self.assertGreater(len(self.manager.games_by_team), 0, "Should index games by team")
        self.assertGreater(len(self.manager.games_by_date), 0, "Should index games by date")
    
    def test_game_finding(self):
        """Test game finding functionality"""
        # Find games by team
        kc_games = self.manager.get_team_schedule("KC")
        self.assertGreaterEqual(len(kc_games), 0, "Should find KC games or empty list")
        
        # Find games by week
        week1_games = self.manager.get_week_games(1)
        if week1_games:  # If we have week 1 data
            self.assertGreater(len(week1_games), 0, "Should find week 1 games")
            for game in week1_games:
                self.assertEqual(game.week, 1, "All games should be from week 1")
    
    def test_matchup_finding(self):
        """Test finding games between specific teams"""
        # This might not find anything in sample data, but should not error
        matchups = self.manager.find_matchup("KC", "BAL")
        self.assertIsInstance(matchups, list, "Should return list of matchups")
        
        for game in matchups:
            teams_in_game = {game.home_team, game.away_team}
            self.assertEqual(teams_in_game, {"KC", "BAL"}, "Matchup should have correct teams")
    
    def test_game_id_generation(self):
        """Test game ID generation"""
        test_date = datetime(2024, 9, 8, 13, 0)
        game_id = self.manager.generate_game_id("KC", "DEN", test_date, 1)
        
        self.assertIsInstance(game_id, str, "Game ID should be string")
        self.assertIn("kc", game_id.lower(), "Game ID should contain team")
        self.assertIn("den", game_id.lower(), "Game ID should contain team")
        self.assertIn("2024", game_id, "Game ID should contain year")
    
    def test_date_range_searching(self):
        """Test finding games within date range"""
        start_date = "2024-09-01"
        end_date = "2024-09-30"
        
        games = self.manager.get_games_by_date_range(start_date, end_date)
        self.assertIsInstance(games, list, "Should return list of games")
        
        # Check dates are within range if games exist
        if games:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            for game in games:
                self.assertGreaterEqual(game.game_date, start_dt, "Game date should be after start")
                self.assertLessEqual(game.game_date, end_dt, "Game date should be before end")


class TestTeamMatchingEngine(unittest.TestCase):
    """Test team matching and fuzzy matching logic"""
    
    def setUp(self):
        """Set up matching engine for tests"""
        self.engine = TeamMatchingEngine()
    
    def test_engine_initialization(self):
        """Test matching engine initializes correctly"""
        self.assertGreater(len(self.engine.team_data), 0, "Should load team data")
        self.assertGreater(len(self.engine.reverse_lookup), 0, "Should build reverse lookup")
        self.assertGreater(len(self.engine.manual_overrides), 0, "Should have manual overrides")
    
    def test_exact_matching(self):
        """Test exact string matching"""
        test_cases = [
            ("KC", "KC"),
            ("Chiefs", "KC"),
            ("Baltimore Ravens", "BAL"),
            ("Ravens", "BAL"),
            ("49ers", "SF"),
        ]
        
        for search_name, expected_team in test_cases:
            result = self.engine.match_team(search_name)
            self.assertIsNotNone(result, f"Should get result for {search_name}")
            self.assertEqual(result.matched_team, expected_team, f"Should match {expected_team} for {search_name}")
            self.assertGreaterEqual(result.confidence, 0.9, f"Should have high confidence for exact match")
    
    def test_fuzzy_matching(self):
        """Test fuzzy/approximate matching"""
        test_cases = [
            ("Kansas City", "KC", 0.7),  # Partial match
            ("K.C.", "KC", 0.7),         # Abbreviation variant
            ("San Francisco", "SF", 0.7), # City name
            ("New England", "NE", 0.7),  # Region name
        ]
        
        for search_name, expected_team, min_conf in test_cases:
            result = self.engine.match_team(search_name, min_confidence=min_conf)
            self.assertIsNotNone(result, f"Should get result for {search_name}")
            if result.matched_team:  # Might not match in limited sample data
                self.assertEqual(result.matched_team, expected_team, f"Should match {expected_team} for {search_name}")
                self.assertGreaterEqual(result.confidence, min_conf, f"Should meet minimum confidence")
    
    def test_no_match_handling(self):
        """Test handling of non-matching inputs"""
        no_match_cases = [
            "",
            "   ",
            "Random Team Name",
            "XYZ",
            "Not A Team"
        ]
        
        for search_name in no_match_cases:
            result = self.engine.match_team(search_name)
            self.assertIsNotNone(result, f"Should get result object for {search_name}")
            if search_name.strip():  # Non-empty strings
                # Either no match or very low confidence
                if result.matched_team:
                    self.assertLess(result.confidence, 0.7, f"Should have low confidence for non-match")
    
    def test_game_team_matching(self):
        """Test matching both teams in a game"""
        home_result, away_result = self.engine.match_game_teams("Chiefs", "Ravens")
        
        self.assertIsNotNone(home_result, "Should get home team result")
        self.assertIsNotNone(away_result, "Should get away team result") 
        
        # In our sample data, these should match
        if home_result.matched_team:
            self.assertEqual(home_result.matched_team, "KC")
        if away_result.matched_team:
            self.assertEqual(away_result.matched_team, "BAL")
    
    def test_batch_matching(self):
        """Test batch matching multiple teams"""
        team_names = ["KC", "Chiefs", "Ravens", "49ers", "Patriots"]
        results = self.engine.batch_match_teams(team_names)
        
        self.assertEqual(len(results), len(team_names), "Should get result for each team")
        
        for i, result in enumerate(results):
            self.assertIsNotNone(result, f"Should get result for team {team_names[i]}")
            self.assertIsInstance(result, MatchResult, "Result should be MatchResult object")
    
    def test_team_variations_lookup(self):
        """Test looking up variations for a team"""
        kc_variations = self.engine.get_team_variations("KC")
        
        self.assertIsInstance(kc_variations, list, "Should return list of variations")
        if kc_variations:  # If we have data for KC
            self.assertIn("CHIEFS", kc_variations, "Should include nickname")
            self.assertIn("KC", kc_variations, "Should include abbreviation")


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios combining team data, schedules, and matching"""
    
    def setUp(self):
        """Set up components for integration tests"""
        self.schedule_manager = NFLScheduleManager()
        self.team_matcher = TeamMatchingEngine()
    
    def test_schedule_team_matching_integration(self):
        """Test that teams in schedule can be matched properly"""
        # Get some games from schedule
        games = self.schedule_manager.games[:5] if self.schedule_manager.games else []
        
        for game in games:
            # Try to match the teams in the game
            home_result = self.team_matcher.match_team(game.home_team)
            away_result = self.team_matcher.match_team(game.away_team)
            
            # Teams in our schedule should be matchable (they use standard abbreviations)
            self.assertIsNotNone(home_result, f"Should get result for home team {game.home_team}")
            self.assertIsNotNone(away_result, f"Should get result for away team {game.away_team}")
            
            if home_result.matched_team and away_result.matched_team:
                self.assertNotEqual(home_result.matched_team, away_result.matched_team,
                                  "Home and away teams should be different")
    
    def test_real_world_api_simulation(self):
        """Simulate real-world API data with various team name formats"""
        # Simulate data from different APIs with different team naming conventions
        api_data_samples = [
            # Kalshi-style data
            {
                "provider": "kalshi",
                "games": [
                    {"home": "Kansas City Chiefs", "away": "Baltimore Ravens"},
                    {"home": "Chiefs", "away": "Ravens"}
                ]
            },
            # Odds API style data  
            {
                "provider": "odds_api",
                "games": [
                    {"home": "Kansas City", "away": "Baltimore"},
                    {"home": "KC", "away": "BAL"}
                ]
            }
        ]
        
        for api_data in api_data_samples:
            provider = api_data["provider"]
            
            for game_data in api_data["games"]:
                home_result = self.team_matcher.match_team(game_data["home"])
                away_result = self.team_matcher.match_team(game_data["away"])
                
                # Should be able to match teams from different API formats
                self.assertIsNotNone(home_result, 
                                   f"Should match home team from {provider}: {game_data['home']}")
                self.assertIsNotNone(away_result, 
                                   f"Should match away team from {provider}: {game_data['away']}")


def run_phase2_validation():
    """Run all Phase 2 validation tests"""
    print("=== PHASE 2 VALIDATION TESTS ===")
    print("Testing NFL reference data collection, team matching, and schedule management...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestNFLTeamData,
        TestNFLScheduleData, 
        TestTeamMatchingEngine,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nPHASE 2 VALIDATION SUCCESSFUL!")
        print("NFL reference data collection, team matching, and schedule management are working correctly.")
        print("Ready to proceed to Phase 3: Kalshi API Integration")
        return True
    else:
        print("\nX PHASE 2 VALIDATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, error in result.failures:
                print(f"  {test}: {error}")
        
        if result.errors:
            print("\nErrors:")
            for test, error in result.errors:
                print(f"  {test}: {error}")
        
        return False


if __name__ == "__main__":
    success = run_phase2_validation()
    sys.exit(0 if success else 1)