"""
Advanced Team Matching Engine
Provides fuzzy matching logic for NFL teams across different data providers.
Integrated with core Team models.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher

from .models import Team, Sport
from .data_manager import get_nfl_data_manager
from .utils import setup_logging


@dataclass
class MatchResult:
    """Result of a team matching operation"""
    matched_team: Optional[Team]  # Team object instead of string
    confidence: float  # 0.0 to 1.0
    match_type: str  # exact, fuzzy, manual, none
    matched_variations: List[str]  # Which variations matched
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TeamMatcher:
    """Advanced team matching engine using core Team models"""
    
    def __init__(self, sport: Sport = Sport.NFL):
        """Initialize team matcher for specific sport"""
        self.sport = sport
        self.logger = setup_logging(f"team_matcher.{sport.value}")
        
        # Load team data based on sport
        if sport == Sport.NFL:
            self.data_manager = get_nfl_data_manager()
            self.teams = self.data_manager.get_all_teams()
        else:
            raise NotImplementedError(f"Sport {sport} not yet supported")
        
        self._build_matching_indices()
        self._setup_manual_overrides()
        self._setup_common_misspellings()
    
    def _build_matching_indices(self):
        """Build various indices for efficient matching"""
        self.reverse_lookup = {}  # variation -> Team
        self.abbreviation_map = {}  # abbrev -> Team
        self.nickname_map = {}  # nickname -> Team
        self.city_map = {}  # city -> Team
        
        for abbrev, team in self.teams.items():
            # All variations point to Team object
            all_variations = set()
            
            # Add abbreviations
            all_variations.update([a.upper() for a in team.abbreviations])
            
            # Add alternative names
            all_variations.update([name.upper() for name in team.alternative_names])
            
            # Add core identifiers
            all_variations.add(team.name.upper())
            all_variations.add(team.nickname.upper())
            all_variations.add(team.city.upper())
            all_variations.add(f"{team.city} {team.nickname}".upper())
            
            # Remove empty strings
            all_variations = {v for v in all_variations if v.strip()}
            
            # Build reverse lookup
            for variation in all_variations:
                self.reverse_lookup[variation] = team
            
            # Build specialized maps
            for abbr in team.abbreviations:
                self.abbreviation_map[abbr.upper()] = team
            
            self.nickname_map[team.nickname.upper()] = team
            self.city_map[team.city.upper()] = team
    
    def _setup_manual_overrides(self):
        """Set up manual override mappings for edge cases"""
        # Get teams by common identifiers for overrides
        team_lookup = {}
        for team in self.teams.values():
            # Use first abbreviation as key
            if team.abbreviations:
                team_lookup[team.abbreviations[0]] = team
            else:
                # Fallback to creating abbreviation from name
                team_lookup[team.name.split()[-1][:3].upper()] = team
        
        self.manual_overrides = {}
        
        # NFL specific overrides
        if self.sport == Sport.NFL:
            # Handle common API variations
            overrides_map = {
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
                'WASHINGTON': 'WAS',
                'WASHINGTON COMMANDERS': 'WAS',
                'WASHINGTON REDSKINS': 'WAS',  # Historical
                'LOS ANGELES RAMS': 'LAR',
                'LA RAMS': 'LAR',
                'LOS ANGELES CHARGERS': 'LAC',
                'LA CHARGERS': 'LAC'
            }
            
            # Map to actual team objects
            for search_term, abbrev in overrides_map.items():
                if abbrev in self.teams:
                    self.manual_overrides[search_term] = self.teams[abbrev]
                else:
                    # Find by abbreviation in any team
                    for team in self.teams.values():
                        if abbrev in team.abbreviations:
                            self.manual_overrides[search_term] = team
                            break
    
    def _setup_common_misspellings(self):
        """Set up common misspelling corrections"""
        self.common_misspellings = {
            'CHEIFS': 'CHIEFS',
            'CHEEFS': 'CHIEFS',
            'PATROITS': 'PATRIOTS',
            'PATRIATS': 'PATRIOTS',
            'RAVES': 'RAVENS',
            'FOURTYNINERS': 'NINERS',
            'RAIDES': 'RAIDERS',
            'BRONKOS': 'BRONCOS',
            'STEELERS': 'STEELERS',  # Already correct
            'STILLERS': 'STEELERS',  # Pittsburgh slang
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
            team = self.reverse_lookup[search_clean]
            return MatchResult(
                team, 
                1.0, 
                "exact", 
                [search_clean],
                {"strategy": "reverse_lookup"}
            )
        
        # Strategy 2: Manual overrides
        if search_clean in self.manual_overrides:
            team = self.manual_overrides[search_clean]
            return MatchResult(
                team,
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
                corrected_result.metadata = {
                    "strategy": "misspelling_correction", 
                    "original": search_clean
                }
                return corrected_result
        
        # Strategy 4: Fuzzy matching with different approaches
        fuzzy_results = []
        
        # 4a: Fuzzy match against all variations
        for variation, team in self.reverse_lookup.items():
            similarity = self._calculate_similarity(search_clean, variation)
            if similarity >= min_confidence:
                fuzzy_results.append((team, similarity, variation, "full_variation"))
        
        # 4b: Fuzzy match against nicknames only (higher weight)
        for nickname, team in self.nickname_map.items():
            if nickname:
                similarity = self._calculate_similarity(search_clean, nickname)
                if similarity >= min_confidence:
                    # Boost nickname matches
                    boosted_similarity = min(1.0, similarity + 0.1)
                    fuzzy_results.append((team, boosted_similarity, nickname, "nickname"))
        
        # 4c: Fuzzy match against cities
        for city, team in self.city_map.items():
            if city:
                similarity = self._calculate_similarity(search_clean, city)
                if similarity >= min_confidence:
                    fuzzy_results.append((team, similarity, city, "city"))
        
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
        
        for variation, team in self.reverse_lookup.items():
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
                    results.append((team, partial_score, variation, "partial"))
        
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
    
    def get_team_variations(self, team: Team) -> List[str]:
        """Get all known variations for a team"""
        variations = []
        for variation, match_team in self.reverse_lookup.items():
            if match_team == team:
                variations.append(variation)
        return sorted(variations)
    
    def validate_matching_accuracy(self) -> Dict:
        """Validate matching accuracy with test cases"""
        # Use actual team data for validation
        test_cases = []
        
        # Create test cases from actual teams
        for abbrev, team in list(self.teams.items())[:5]:  # Test first 5 teams
            # Exact matches
            test_cases.extend([
                (abbrev, team, 1.0),
                (team.nickname, team, 1.0),
                (team.name, team, 1.0),
                (team.city, team, 0.8)
            ])
        
        # Edge cases
        test_cases.extend([
            ("Random Team", None, 0.0),
            ("", None, 0.0),
        ])
        
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
                        "expected": None,
                        "got": result.matched_team.name if result.matched_team else None,
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
                        "expected": expected_team.name,
                        "got": result.matched_team.name if result.matched_team else None,
                        "confidence": result.confidence,
                        "min_confidence": min_confidence,
                        "reason": "Match failed or low confidence"
                    })
        
        results["accuracy"] = results["passed"] / results["total_tests"] if results["total_tests"] > 0 else 0
        return results


# Global instances for easy access
_team_matchers = {}

def get_team_matcher(sport: Sport = Sport.NFL) -> TeamMatcher:
    """Get team matcher instance for specific sport"""
    if sport not in _team_matchers:
        _team_matchers[sport] = TeamMatcher(sport)
    return _team_matchers[sport]