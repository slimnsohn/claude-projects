"""
Team Matching Engine
Advanced fuzzy matching logic for NFL teams across different data providers
"""

import json
import re
from typing import Dict, List, Tuple, Optional, Set
from difflib import SequenceMatcher
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class MatchResult:
    """Result of a team matching operation"""
    matched_team: Optional[str]  # Standard team abbreviation
    confidence: float  # 0.0 to 1.0
    match_type: str  # exact, fuzzy, manual, none
    matched_variations: List[str]  # Which variations matched
    metadata: Dict = None


class TeamMatchingEngine:
    """Advanced team matching engine with multiple strategies"""
    
    def __init__(self, team_data_file: str = None):
        """Initialize matching engine with team data"""
        self.team_data = {}
        self.reverse_lookup = {}
        self.abbreviation_map = {}
        self.nickname_map = {}
        self.city_map = {}
        self.manual_overrides = {}
        self.common_misspellings = {}
        
        if team_data_file:
            self._load_team_data(team_data_file)
        else:
            self._load_default_team_data()
        
        self._build_matching_indices()
        self._setup_manual_overrides()
        self._setup_common_misspellings()
    
    def _load_team_data(self, file_path: str):
        """Load team data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.team_data = data.get('teams', {})
        except FileNotFoundError:
            print(f"Team data file not found: {file_path}, using default data")
            self._load_default_team_data()
    
    def _load_default_team_data(self):
        """Load default NFL team data if file not available"""
        # Simplified team data for testing - in real use would load from nfl_teams_2024.json
        self.team_data = {
            'KC': {
                'name': 'Kansas City Chiefs',
                'city': 'Kansas City',
                'nickname': 'Chiefs',
                'abbreviations': ['KC', 'KAN', 'CHIEF'],
                'alternative_names': ['Kansas City Chiefs', 'Chiefs', 'Kansas City', 'KC Chiefs']
            },
            'BAL': {
                'name': 'Baltimore Ravens',
                'city': 'Baltimore', 
                'nickname': 'Ravens',
                'abbreviations': ['BAL', 'BALT'],
                'alternative_names': ['Baltimore Ravens', 'Ravens', 'Baltimore']
            },
            'SF': {
                'name': 'San Francisco 49ers',
                'city': 'San Francisco',
                'nickname': '49ers',
                'abbreviations': ['SF', 'SFO', '49ER'],
                'alternative_names': ['San Francisco 49ers', '49ers', 'San Francisco', 'Niners', 'SF 49ers']
            },
            'NE': {
                'name': 'New England Patriots',
                'city': 'Foxborough',
                'nickname': 'Patriots', 
                'abbreviations': ['NE', 'NWE', 'PAT', 'PATS'],
                'alternative_names': ['New England Patriots', 'Patriots', 'New England', 'Pats']
            },
            'LV': {
                'name': 'Las Vegas Raiders',
                'city': 'Las Vegas',
                'nickname': 'Raiders',
                'abbreviations': ['LV', 'LAS', 'RAID', 'OAK'],  # Include old Oakland
                'alternative_names': ['Las Vegas Raiders', 'Raiders', 'Las Vegas', 'LV Raiders', 'Oakland Raiders']
            }
        }
    
    def _build_matching_indices(self):
        """Build various indices for efficient matching"""
        self.reverse_lookup = {}
        self.abbreviation_map = {}
        self.nickname_map = {}
        self.city_map = {}
        
        for abbrev, team_data in self.team_data.items():
            # All variations point to standard abbreviation
            all_variations = set()
            
            # Add abbreviations
            all_variations.update([a.upper() for a in team_data.get('abbreviations', [])])
            
            # Add alternative names
            all_variations.update([name.upper() for name in team_data.get('alternative_names', [])])
            
            # Add core identifiers
            all_variations.add(team_data.get('name', '').upper())
            all_variations.add(team_data.get('nickname', '').upper())
            all_variations.add(team_data.get('city', '').upper())
            all_variations.add(f"{team_data.get('city', '')} {team_data.get('nickname', '')}".upper())
            
            # Remove empty strings
            all_variations = {v for v in all_variations if v.strip()}
            
            # Build reverse lookup
            for variation in all_variations:
                self.reverse_lookup[variation] = abbrev
            
            # Build specialized maps
            for abbr in team_data.get('abbreviations', []):
                self.abbreviation_map[abbr.upper()] = abbrev
            
            self.nickname_map[team_data.get('nickname', '').upper()] = abbrev
            self.city_map[team_data.get('city', '').upper()] = abbrev
    
    def _setup_manual_overrides(self):
        """Set up manual override mappings for edge cases"""
        self.manual_overrides = {
            # Handle common API variations
            'KANSAS CITY': 'KC',
            'K.C.': 'KC', 
            'KANSAS': 'KC',
            'SAN FRANCISCO': 'SF',
            'S.F.': 'SF',
            'FORTY NINERS': 'SF',
            '49ERS': 'SF',
            'NEW ENGLAND': 'NE',
            'N.E.': 'NE',
            'LAS VEGAS': 'LV',
            'L.V.': 'LV',
            'VEGAS': 'LV',
            'OAKLAND': 'LV',  # Raiders moved
            'OAK': 'LV',
            
            # Handle alternative spellings
            'RAVENS': 'BAL',
            'BALTIMORE': 'BAL',
            'CHIEFS': 'KC',
            'PATRIOTS': 'NE',
            'RAIDERS': 'LV',
            'NINERS': 'SF',
        }
    
    def _setup_common_misspellings(self):
        """Set up common misspelling corrections"""
        self.common_misspellings = {
            'CHEIFS': 'CHIEFS',
            'CHEEFS': 'CHIEFS', 
            'PATROITS': 'PATRIOTS',
            'PATRIATS': 'PATRIOTS',
            'RAVENS': 'RAVENS',  # Already correct
            'RAVES': 'RAVENS',
            '49ERS': '49ERS',  # Already correct
            'FOURTYNINERS': 'NINERS',
            'RAIDERS': 'RAIDERS',  # Already correct
            'RAIDES': 'RAIDERS',
        }
    
    def match_team(self, search_name: str, min_confidence: float = 0.7) -> MatchResult:
        """
        Match a team name using multiple strategies
        
        Args:
            search_name: Name to match
            min_confidence: Minimum confidence threshold
            
        Returns:
            MatchResult with best match found
        """
        if not search_name or not search_name.strip():
            return MatchResult(None, 0.0, "none", [], {"reason": "empty_search"})
        
        search_clean = search_name.strip().upper()
        
        # Strategy 1: Exact match in reverse lookup
        if search_clean in self.reverse_lookup:
            return MatchResult(
                self.reverse_lookup[search_clean], 
                1.0, 
                "exact", 
                [search_clean],
                {"strategy": "reverse_lookup"}
            )
        
        # Strategy 2: Manual overrides
        if search_clean in self.manual_overrides:
            return MatchResult(
                self.manual_overrides[search_clean],
                0.95,
                "manual",
                [search_clean], 
                {"strategy": "manual_override"}
            )
        
        # Strategy 3: Misspelling correction + retry
        corrected = self._correct_misspellings(search_clean)
        if corrected != search_clean:
            corrected_result = self.match_team(corrected, min_confidence)
            if corrected_result.confidence >= min_confidence:
                corrected_result.match_type = "corrected"
                corrected_result.metadata = {"strategy": "misspelling_correction", "original": search_clean}
                return corrected_result
        
        # Strategy 4: Fuzzy matching with different approaches
        fuzzy_results = []
        
        # 4a: Fuzzy match against all variations
        for variation, team_abbrev in self.reverse_lookup.items():
            similarity = self._calculate_similarity(search_clean, variation)
            if similarity >= min_confidence:
                fuzzy_results.append((team_abbrev, similarity, variation, "full_variation"))
        
        # 4b: Fuzzy match against nicknames only (higher weight)
        for nickname, team_abbrev in self.nickname_map.items():
            if nickname:
                similarity = self._calculate_similarity(search_clean, nickname)
                if similarity >= min_confidence:
                    # Boost nickname matches
                    boosted_similarity = min(1.0, similarity + 0.1)
                    fuzzy_results.append((team_abbrev, boosted_similarity, nickname, "nickname"))
        
        # 4c: Fuzzy match against cities
        for city, team_abbrev in self.city_map.items():
            if city:
                similarity = self._calculate_similarity(search_clean, city)
                if similarity >= min_confidence:
                    fuzzy_results.append((team_abbrev, similarity, city, "city"))
        
        # 4d: Partial word matching
        partial_results = self._partial_word_matching(search_clean, min_confidence)
        fuzzy_results.extend(partial_results)
        
        # Select best fuzzy match
        if fuzzy_results:
            # Sort by confidence, then by match type preference
            type_priority = {"nickname": 3, "full_variation": 2, "city": 1, "partial": 0}
            fuzzy_results.sort(key=lambda x: (x[1], type_priority.get(x[3], 0)), reverse=True)
            
            best_team, best_conf, best_variation, match_type = fuzzy_results[0]
            return MatchResult(
                best_team,
                best_conf, 
                "fuzzy",
                [best_variation],
                {"strategy": f"fuzzy_{match_type}", "all_candidates": len(fuzzy_results)}
            )
        
        # No match found
        return MatchResult(
            None, 
            0.0, 
            "none", 
            [],
            {"strategy": "no_match", "search_term": search_clean}
        )
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using multiple methods"""
        if not str1 or not str2:
            return 0.0
        
        # Method 1: Sequence matcher (difflib)
        seq_similarity = SequenceMatcher(None, str1, str2).ratio()
        
        # Method 2: Substring matching (boost if one contains the other)
        substring_bonus = 0.0
        if str1 in str2 or str2 in str1:
            substring_bonus = 0.2
        
        # Method 3: Word-level matching
        words1 = set(str1.split())
        words2 = set(str2.split())
        if words1 and words2:
            word_intersection = len(words1.intersection(words2))
            word_union = len(words1.union(words2))
            word_similarity = word_intersection / word_union if word_union > 0 else 0.0
        else:
            word_similarity = 0.0
        
        # Combine methods with weights
        combined_similarity = (
            seq_similarity * 0.6 +
            word_similarity * 0.3 +
            substring_bonus * 0.1
        )
        
        return min(1.0, combined_similarity)
    
    def _partial_word_matching(self, search_clean: str, min_confidence: float) -> List[Tuple]:
        """Match based on partial words"""
        results = []
        search_words = search_clean.split()
        
        for variation, team_abbrev in self.reverse_lookup.items():
            variation_words = variation.split()
            
            # Check if any search word matches any variation word
            matches = 0
            total_words = max(len(search_words), len(variation_words))
            
            for search_word in search_words:
                for var_word in variation_words:
                    if (search_word in var_word or var_word in search_word or
                        SequenceMatcher(None, search_word, var_word).ratio() > 0.8):
                        matches += 1
                        break
            
            if matches > 0 and total_words > 0:
                partial_score = matches / total_words
                if partial_score >= min_confidence:
                    results.append((team_abbrev, partial_score, variation, "partial"))
        
        return results
    
    def _correct_misspellings(self, text: str) -> str:
        """Correct common misspellings"""
        corrected = text
        for misspelling, correction in self.common_misspellings.items():
            corrected = corrected.replace(misspelling, correction)
        return corrected
    
    def match_game_teams(self, home_team: str, away_team: str, 
                        min_confidence: float = 0.7) -> Tuple[MatchResult, MatchResult]:
        """Match both teams in a game"""
        home_result = self.match_team(home_team, min_confidence)
        away_result = self.match_team(away_team, min_confidence)
        
        return home_result, away_result
    
    def batch_match_teams(self, team_names: List[str], 
                         min_confidence: float = 0.7) -> List[MatchResult]:
        """Match a list of team names"""
        return [self.match_team(name, min_confidence) for name in team_names]
    
    def get_team_variations(self, team_abbrev: str) -> List[str]:
        """Get all known variations for a team"""
        variations = []
        for variation, abbrev in self.reverse_lookup.items():
            if abbrev == team_abbrev:
                variations.append(variation)
        return sorted(variations)
    
    def validate_matching_accuracy(self) -> Dict:
        """Validate matching accuracy with test cases"""
        test_cases = [
            # Exact matches
            ("KC", "KC", 1.0),
            ("Chiefs", "KC", 1.0),
            ("Kansas City Chiefs", "KC", 1.0),
            
            # Fuzzy matches
            ("Kansas City", "KC", 0.8),
            ("K.C.", "KC", 0.8),
            ("Cheifs", "KC", 0.7),  # Misspelling
            
            ("Baltimore Ravens", "BAL", 1.0),
            ("Ravens", "BAL", 1.0),
            ("Baltimore", "BAL", 0.8),
            
            ("San Francisco 49ers", "SF", 1.0),
            ("49ers", "SF", 1.0),
            ("Niners", "SF", 0.9),
            ("San Francisco", "SF", 0.8),
            
            # Edge cases
            ("Raiders", "LV", 0.9),  # Should match Las Vegas
            ("Oakland Raiders", "LV", 0.9),  # Historical reference
            ("Las Vegas", "LV", 0.8),
            
            # Should not match
            ("Random Team", None, 0.0),
            ("", None, 0.0),
        ]
        
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "failures": []
        }
        
        for search_name, expected_team, min_confidence in test_cases:
            result = self.match_team(search_name, 0.6)  # Lower threshold for testing
            
            if expected_team is None:
                # Should not match
                if result.matched_team is None or result.confidence < min_confidence:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append({
                        "search": search_name,
                        "expected": expected_team,
                        "got": result.matched_team,
                        "confidence": result.confidence,
                        "reason": "Should not have matched"
                    })
            else:
                # Should match
                if (result.matched_team == expected_team and 
                    result.confidence >= min_confidence):
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failures"].append({
                        "search": search_name,
                        "expected": expected_team,
                        "got": result.matched_team,
                        "confidence": result.confidence,
                        "min_confidence": min_confidence,
                        "reason": "Match failed or low confidence"
                    })
        
        results["accuracy"] = results["passed"] / results["total_tests"]
        return results


def test_team_matching():
    """Test team matching engine functionality"""
    print("=== TEAM MATCHING ENGINE TESTS ===")
    
    # Initialize engine
    engine = TeamMatchingEngine()
    
    # Test basic functionality
    print(f"OK Loaded {len(engine.team_data)} teams")
    print(f"OK Built reverse lookup with {len(engine.reverse_lookup)} variations")
    print(f"OK Set up {len(engine.manual_overrides)} manual overrides")
    
    # Test specific matches
    test_cases = [
        "KC", "Chiefs", "Kansas City", "Kansas City Chiefs",
        "Baltimore", "Ravens", "Baltimore Ravens",
        "49ers", "San Francisco", "Niners",
        "Patriots", "New England", "Pats",
        "Raiders", "Las Vegas", "Oakland Raiders"
    ]
    
    print("\n--- INDIVIDUAL MATCHING TESTS ---")
    for test_name in test_cases:
        result = engine.match_team(test_name)
        status = "MATCH" if result.matched_team else "NO MATCH"
        conf_str = f"{result.confidence:.2f}" if result.confidence > 0 else "0.00"
        print(f"'{test_name}' -> {status} ({result.matched_team}) conf={conf_str} type={result.match_type}")
    
    # Test game matching
    print("\n--- GAME MATCHING TESTS ---")
    game_tests = [
        ("Kansas City Chiefs", "Baltimore Ravens"),
        ("Chiefs", "Ravens"), 
        ("KC", "BAL"),
        ("San Francisco", "New England Patriots")
    ]
    
    for home, away in game_tests:
        home_result, away_result = engine.match_game_teams(home, away)
        print(f"Game: '{away}' @ '{home}'")
        print(f"  Home: {home_result.matched_team} (conf={home_result.confidence:.2f})")
        print(f"  Away: {away_result.matched_team} (conf={away_result.confidence:.2f})")
    
    # Run validation
    print("\n--- ACCURACY VALIDATION ---")
    validation = engine.validate_matching_accuracy()
    print(f"Tests passed: {validation['passed']}/{validation['total_tests']} ({validation['accuracy']:.1%})")
    
    if validation['failures']:
        print("Failures:")
        for failure in validation['failures']:
            print(f"  '{failure['search']}' -> Expected {failure['expected']}, got {failure['got']} (conf={failure['confidence']:.2f})")
    
    return engine


if __name__ == "__main__":
    # Test the matching engine
    engine = test_team_matching()
    
    print("\n=== MATCHING ENGINE SUMMARY ===")
    print(f"Teams loaded: {len(engine.team_data)}")
    print(f"Total variations: {len(engine.reverse_lookup)}")
    print(f"Manual overrides: {len(engine.manual_overrides)}")
    print(f"Misspelling corrections: {len(engine.common_misspellings)}")
    
    # Show variations for a team
    print(f"\nKansas City variations:")
    kc_variations = engine.get_team_variations("KC")
    for var in sorted(kc_variations):
        print(f"  '{var}'")
    
    print(f"\nEngine ready for integration with API providers!")