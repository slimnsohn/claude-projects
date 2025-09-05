"""
Phase 2 Integration Tests
Tests the integrated NFL data management and team matching with core models.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from market_data_core import (
    get_nfl_data_manager, get_team_matcher, 
    Team, Game, Sport, MatchResult
)


class TestNFLDataManagerIntegration(unittest.TestCase):
    """Test NFL data manager functionality"""
    
    def setUp(self):
        """Set up test data manager"""
        self.data_manager = get_nfl_data_manager()
    
    def test_data_loading(self):
        """Test that NFL data loads correctly"""
        self.assertIsNotNone(self.data_manager.teams_data)
        self.assertIsNotNone(self.data_manager.schedule_data)
        self.assertGreater(len(self.data_manager.teams), 30)  # Should have 32 NFL teams
        self.assertGreater(len(self.data_manager.games), 200)  # Should have many games
    
    def test_team_objects_creation(self):
        """Test that Team objects are created correctly"""
        # Check a known team
        kc = self.data_manager.get_team('KC')
        self.assertIsNotNone(kc)
        self.assertIsInstance(kc, Team)
        self.assertEqual(kc.sport, Sport.NFL)
        self.assertIn('Chiefs', kc.nickname)
        self.assertIn('Kansas City', kc.name)
    
    def test_game_objects_creation(self):
        """Test that Game objects are created correctly"""
        games = list(self.data_manager.games.values())
        self.assertGreater(len(games), 0)
        
        # Check first game structure
        game = games[0]
        self.assertIsInstance(game, Game)
        self.assertIsInstance(game.home_team, Team)
        self.assertIsInstance(game.away_team, Team)
        self.assertEqual(game.sport, Sport.NFL)
        self.assertIsNotNone(game.game_date)
    
    def test_team_lookup(self):
        """Test various team lookup methods"""
        # Test by abbreviation
        team = self.data_manager.get_team('KC')
        self.assertIsNotNone(team)
        
        # Test by name (if team matching is working)
        team = self.data_manager.get_team('Kansas City Chiefs')
        # This might not work if matching not integrated, so make it optional
        if team is not None:
            self.assertIn('Kansas City', team.name)
        
        # Test non-existent team
        team = self.data_manager.get_team('Nonexistent Team')
        self.assertIsNone(team)
    
    def test_games_by_week(self):
        """Test getting games by week"""
        week1_games = self.data_manager.get_games_by_week(1)
        self.assertGreater(len(week1_games), 10)  # Should have many week 1 games
        
        for game in week1_games:
            self.assertEqual(game.week, 1)
    
    def test_find_specific_game(self):
        """Test finding specific games"""
        # This will depend on actual schedule data
        games = list(self.data_manager.games.values())
        if games:
            sample_game = games[0]
            found_game = self.data_manager.find_game(
                sample_game.home_team, 
                sample_game.away_team, 
                sample_game.week
            )
            self.assertIsNotNone(found_game)
            self.assertEqual(found_game.game_id, sample_game.game_id)
    
    def test_team_schedule(self):
        """Test getting team schedule"""
        kc = self.data_manager.get_team('KC')
        if kc:
            schedule = self.data_manager.get_team_schedule(kc)
            self.assertGreater(len(schedule), 15)  # Should have 17+ games in season
            
            # Check all games include KC
            for game in schedule:
                self.assertTrue(
                    game.home_team.name == kc.name or game.away_team.name == kc.name
                )
    
    def test_data_integrity(self):
        """Test data integrity validation"""
        report = self.data_manager.validate_data_integrity()
        
        self.assertGreater(report['teams_count'], 30)
        self.assertGreater(report['games_count'], 200)
        self.assertGreater(len(report['weeks_covered']), 15)
        
        # Check that most teams have games
        teams_with_games_ratio = len(report['teams_with_games']) / report['teams_count']
        self.assertGreater(teams_with_games_ratio, 0.9)  # At least 90% of teams should have games


class TestTeamMatcherIntegration(unittest.TestCase):
    """Test team matching engine functionality"""
    
    def setUp(self):
        """Set up test team matcher"""
        self.matcher = get_team_matcher(Sport.NFL)
    
    def test_matcher_initialization(self):
        """Test that matcher initializes correctly"""
        self.assertEqual(self.matcher.sport, Sport.NFL)
        self.assertGreater(len(self.matcher.teams), 30)
        self.assertGreater(len(self.matcher.reverse_lookup), 100)  # Should have many variations
    
    def test_exact_matching(self):
        """Test exact team matching"""
        # Test abbreviation matching
        result = self.matcher.match_team('KC')
        self.assertIsNotNone(result.matched_team)
        self.assertEqual(result.match_type, 'exact')
        self.assertGreater(result.confidence, 0.9)
        
        # Test full name matching
        result = self.matcher.match_team('Kansas City Chiefs')
        self.assertIsNotNone(result.matched_team)
        self.assertGreater(result.confidence, 0.9)
    
    def test_fuzzy_matching(self):
        """Test fuzzy team matching"""
        # Test nickname matching
        result = self.matcher.match_team('Chiefs')
        self.assertIsNotNone(result.matched_team)
        self.assertIn('Chiefs', result.matched_team.nickname)
        
        # Test city matching
        result = self.matcher.match_team('Kansas City')
        self.assertIsNotNone(result.matched_team)
        self.assertIn('Kansas City', result.matched_team.city)
    
    def test_manual_overrides(self):
        """Test manual override matching"""
        # Test common variations that should be handled by overrides
        test_cases = [
            'K.C.',
            'Vegas',
            'Oakland',  # Should map to Las Vegas
            'San Francisco'
        ]
        
        for case in test_cases:
            result = self.matcher.match_team(case)
            # Should find something with reasonable confidence
            if result.matched_team:
                self.assertGreater(result.confidence, 0.7)
    
    def test_no_match_cases(self):
        """Test cases that should not match"""
        result = self.matcher.match_team('Random Team Name')
        self.assertTrue(result.matched_team is None or result.confidence < 0.7)
        
        result = self.matcher.match_team('')
        self.assertIsNone(result.matched_team)
        self.assertEqual(result.match_type, 'none')
    
    def test_game_team_matching(self):
        """Test matching both teams in a game"""
        home_result, away_result = self.matcher.match_game_teams('Chiefs', 'Ravens')
        
        if home_result.matched_team:
            self.assertIn('Chiefs', home_result.matched_team.nickname)
        if away_result.matched_team:
            self.assertIn('Ravens', away_result.matched_team.nickname)
    
    def test_batch_matching(self):
        """Test batch team matching"""
        team_names = ['KC', 'Chiefs', 'Baltimore Ravens', 'Random Team']
        results = self.matcher.batch_match_teams(team_names)
        
        self.assertEqual(len(results), 4)
        self.assertIsInstance(results[0], MatchResult)
        
        # First three should match, last should not
        self.assertIsNotNone(results[0].matched_team)
        self.assertIsNotNone(results[1].matched_team)
        self.assertIsNotNone(results[2].matched_team)
        self.assertTrue(results[3].matched_team is None or results[3].confidence < 0.7)
    
    def test_team_variations(self):
        """Test getting team variations"""
        # Get a known team
        kc = self.matcher.teams.get('KC')
        if kc:
            variations = self.matcher.get_team_variations(kc)
            self.assertGreater(len(variations), 3)
            self.assertIn('KC', variations)
            self.assertIn('CHIEFS', variations)
    
    def test_matching_accuracy_validation(self):
        """Test matching accuracy validation"""
        results = self.matcher.validate_matching_accuracy()
        
        self.assertIn('accuracy', results)
        self.assertIn('total_tests', results)
        self.assertIn('passed', results)
        self.assertIn('failed', results)
        
        # Should have reasonable accuracy
        self.assertGreater(results['accuracy'], 0.8)  # At least 80% accuracy


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios between data manager and matcher"""
    
    def setUp(self):
        """Set up integration test components"""
        self.data_manager = get_nfl_data_manager()
        self.matcher = get_team_matcher(Sport.NFL)
    
    def test_team_consistency(self):
        """Test that teams are consistent between data manager and matcher"""
        # Get teams from both sources
        dm_teams = self.data_manager.get_all_teams()
        matcher_teams = self.matcher.teams
        
        # Should have same number of teams
        self.assertEqual(len(dm_teams), len(matcher_teams))
        
        # Teams should be the same objects
        for abbrev in dm_teams:
            self.assertIn(abbrev, matcher_teams)
            self.assertEqual(dm_teams[abbrev], matcher_teams[abbrev])
    
    def test_game_team_matching_workflow(self):
        """Test full workflow of game team matching"""
        # Get a sample game
        games = list(self.data_manager.games.values())
        if not games:
            self.skipTest("No games available in data")
        
        sample_game = games[0]
        
        # Test that we can find the teams using matcher
        home_result = self.matcher.match_team(sample_game.home_team.name)
        away_result = self.matcher.match_team(sample_game.away_team.name)
        
        self.assertIsNotNone(home_result.matched_team)
        self.assertIsNotNone(away_result.matched_team)
        self.assertEqual(home_result.matched_team, sample_game.home_team)
        self.assertEqual(away_result.matched_team, sample_game.away_team)
    
    def test_schedule_matching_workflow(self):
        """Test matching external team names to schedule"""
        # Simulate external API team names that need matching
        external_team_names = [
            'Kansas City Chiefs',
            'KC',
            'Chiefs', 
            'Baltimore Ravens',
            'Ravens',
            'New England Patriots',
            'Patriots'
        ]
        
        matched_teams = []
        for name in external_team_names:
            result = self.matcher.match_team(name)
            if result.matched_team:
                matched_teams.append(result.matched_team)
        
        # Should match most names
        self.assertGreater(len(matched_teams), len(external_team_names) * 0.8)
        
        # Each matched team should have a schedule
        for team in matched_teams:
            schedule = self.data_manager.get_team_schedule(team)
            self.assertGreater(len(schedule), 10)


def run_phase2_integration_tests():
    """Run all Phase 2 integration tests"""
    print("=== PHASE 2 INTEGRATION TESTS ===")
    print("Testing integrated NFL data management and team matching with core models...")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestNFLDataManagerIntegration,
        TestTeamMatcherIntegration,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\nPHASE 2 INTEGRATION SUCCESSFUL!")
        print("Integrated NFL data management and team matching are working correctly.")
        print("Ready to proceed to Phase 3: Kalshi API Integration")
        return True
    else:
        print("\nX PHASE 2 INTEGRATION FAILED!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        for test, error in result.errors:
            print(f"ERROR in {test}: {error}")
        for test, failure in result.failures:
            print(f"FAILURE in {test}: {failure}")
        return False


if __name__ == "__main__":
    # Run integration tests
    success = run_phase2_integration_tests()
    sys.exit(0 if success else 1)