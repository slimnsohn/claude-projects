"""
Data Alignment Module for Matching Games Across Platforms
Production-ready module for aligning Pinnacle and Kalshi data
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone, timedelta
import re
from difflib import SequenceMatcher
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.sports_config import get_sport_config, SPORTS_CONFIG

class GameMatcher:
    """Class for matching games between Pinnacle and Kalshi platforms across all sports"""
    
    # Legacy comprehensive team aliases - now loaded dynamically from sports_config
    # Kept for backward compatibility but will be replaced by sport-specific configs
    LEGACY_TEAM_ALIASES = {
        # MLB Teams
        'LAA': ['Los Angeles Angels', 'Angels', 'LA Angels'],
        'HOU': ['Houston Astros', 'Astros'], 
        'OAK': ['Oakland Athletics', 'Athletics', 'A\'s'],
        'TOR': ['Toronto Blue Jays', 'Blue Jays', 'Jays'],
        'ATL': ['Atlanta Braves', 'Braves'],
        'MIL': ['Milwaukee Brewers', 'Brewers'],
        'STL': ['St. Louis Cardinals', 'Cardinals'],
        'CHC': ['Chicago Cubs', 'Cubs'],
        'ARI': ['Arizona Diamondbacks', 'Diamondbacks', 'D-backs'],
        'COL': ['Colorado Rockies', 'Rockies'],
        'LAD': ['Los Angeles Dodgers', 'Dodgers'],
        'SD': ['San Diego Padres', 'Padres'],
        'SF': ['San Francisco Giants', 'Giants'],
        'MIA': ['Miami Marlins', 'Marlins'],
        'NYM': ['New York Mets', 'Mets'],
        'PHI': ['Philadelphia Phillies', 'Phillies'],
        'PIT': ['Pittsburgh Pirates', 'Pirates'],
        'WSH': ['Washington Nationals', 'Nationals'],
        'CWS': ['Chicago White Sox', 'White Sox'],
        'CLE': ['Cleveland Guardians', 'Guardians'],
        'DET': ['Detroit Tigers', 'Tigers'],
        'KC': ['Kansas City Royals', 'Royals'],
        'MIN': ['Minnesota Twins', 'Twins', 'Minnesota'],
        'NYY': ['New York Yankees', 'Yankees'],
        'BAL': ['Baltimore Orioles', 'Orioles'],
        'BOS': ['Boston Red Sox', 'Red Sox'],
        'TB': ['Tampa Bay Rays', 'Rays'],
        'TEX': ['Texas Rangers', 'Rangers'],
        'SEA': ['Seattle Mariners', 'Mariners'],
        
        # NFL Teams
        'ARI': ['Arizona Cardinals', 'Cardinals'],
        'ATL': ['Atlanta Falcons', 'Falcons'],
        'BAL': ['Baltimore Ravens', 'Ravens'],
        'BUF': ['Buffalo Bills', 'Bills'],
        'CAR': ['Carolina Panthers', 'Panthers'],
        'CHI': ['Chicago Bears', 'Bears'],
        'CIN': ['Cincinnati Bengals', 'Bengals'],
        'CLE': ['Cleveland Browns', 'Browns'],
        'DAL': ['Dallas Cowboys', 'Cowboys'],
        'DEN': ['Denver Broncos', 'Broncos'],
        'DET': ['Detroit Lions', 'Lions'],
        'GB': ['Green Bay Packers', 'Packers'],
        'HOU': ['Houston Texans', 'Texans'],
        'IND': ['Indianapolis Colts', 'Colts'],
        'JAX': ['Jacksonville Jaguars', 'Jaguars'],
        'KC': ['Kansas City Chiefs', 'Chiefs'],
        'LV': ['Las Vegas Raiders', 'Raiders'],
        'LAC': ['Los Angeles Chargers', 'Chargers'],
        'LAR': ['Los Angeles Rams', 'Rams'],
        'MIA': ['Miami Dolphins', 'Dolphins'],
        'MIN': ['Minnesota Vikings', 'Vikings'],
        'NE': ['New England Patriots', 'Patriots'],
        'NO': ['New Orleans Saints', 'Saints'],
        'NYG': ['New York Giants', 'Giants'],
        'NYJ': ['New York Jets', 'Jets'],
        'PHI': ['Philadelphia Eagles', 'Eagles'],
        'PIT': ['Pittsburgh Steelers', 'Steelers'],
        'SF': ['San Francisco 49ers', '49ers', 'Niners'],
        'SEA': ['Seattle Seahawks', 'Seahawks'],
        'TB': ['Tampa Bay Buccaneers', 'Buccaneers', 'Bucs'],
        'TEN': ['Tennessee Titans', 'Titans'],
        'WAS': ['Washington Commanders', 'Commanders'],
        
        # NBA Teams
        'ATL': ['Atlanta Hawks', 'Hawks'],
        'BOS': ['Boston Celtics', 'Celtics'],
        'BKN': ['Brooklyn Nets', 'Nets'],
        'CHA': ['Charlotte Hornets', 'Hornets'],
        'CHI': ['Chicago Bulls', 'Bulls'],
        'CLE': ['Cleveland Cavaliers', 'Cavaliers', 'Cavs'],
        'DAL': ['Dallas Mavericks', 'Mavericks', 'Mavs'],
        'DEN': ['Denver Nuggets', 'Nuggets'],
        'DET': ['Detroit Pistons', 'Pistons'],
        'GSW': ['Golden State Warriors', 'Warriors'],
        'HOU': ['Houston Rockets', 'Rockets'],
        'IND': ['Indiana Pacers', 'Pacers'],
        'LAC': ['Los Angeles Clippers', 'Clippers'],
        'LAL': ['Los Angeles Lakers', 'Lakers'],
        'MEM': ['Memphis Grizzlies', 'Grizzlies'],
        'MIA': ['Miami Heat', 'Heat'],
        'MIL': ['Milwaukee Bucks', 'Bucks'],
        'MIN': ['Minnesota Timberwolves', 'Timberwolves', 'Wolves'],
        'NOP': ['New Orleans Pelicans', 'Pelicans'],
        'NYK': ['New York Knicks', 'Knicks'],
        'OKC': ['Oklahoma City Thunder', 'Thunder'],
        'ORL': ['Orlando Magic', 'Magic'],
        'PHI': ['Philadelphia 76ers', '76ers', 'Sixers'],
        'PHX': ['Phoenix Suns', 'Suns'],
        'POR': ['Portland Trail Blazers', 'Trail Blazers', 'Blazers'],
        'SAC': ['Sacramento Kings', 'Kings'],
        'SAS': ['San Antonio Spurs', 'Spurs'],
        'TOR': ['Toronto Raptors', 'Raptors'],
        'UTA': ['Utah Jazz', 'Jazz'],
        'WAS': ['Washington Wizards', 'Wizards'],
        
        # NHL Teams
        'ANA': ['Anaheim Ducks', 'Ducks'],
        'ARI': ['Arizona Coyotes', 'Coyotes'],
        'BOS': ['Boston Bruins', 'Bruins'],
        'BUF': ['Buffalo Sabres', 'Sabres'],
        'CGY': ['Calgary Flames', 'Flames'],
        'CAR': ['Carolina Hurricanes', 'Hurricanes'],
        'CHI': ['Chicago Blackhawks', 'Blackhawks'],
        'COL': ['Colorado Avalanche', 'Avalanche'],
        'CBJ': ['Columbus Blue Jackets', 'Blue Jackets'],
        'DAL': ['Dallas Stars', 'Stars'],
        'DET': ['Detroit Red Wings', 'Red Wings'],
        'EDM': ['Edmonton Oilers', 'Oilers'],
        'FLA': ['Florida Panthers', 'Panthers'],
        'LAK': ['Los Angeles Kings', 'Kings'],
        'MIN': ['Minnesota Wild', 'Wild'],
        'MTL': ['Montreal Canadiens', 'Canadiens', 'Habs'],
        'NSH': ['Nashville Predators', 'Predators'],
        'NJD': ['New Jersey Devils', 'Devils'],
        'NYI': ['New York Islanders', 'Islanders'],
        'NYR': ['New York Rangers', 'Rangers'],
        'OTT': ['Ottawa Senators', 'Senators'],
        'PHI': ['Philadelphia Flyers', 'Flyers'],
        'PIT': ['Pittsburgh Penguins', 'Penguins'],
        'SJS': ['San Jose Sharks', 'Sharks'],
        'SEA': ['Seattle Kraken', 'Kraken'],
        'STL': ['St. Louis Blues', 'Blues'],
        'TBL': ['Tampa Bay Lightning', 'Lightning'],
        'TOR': ['Toronto Maple Leafs', 'Maple Leafs', 'Leafs'],
        'VAN': ['Vancouver Canucks', 'Canucks'],
        'VGK': ['Vegas Golden Knights', 'Golden Knights'],
        'WSH': ['Washington Capitals', 'Capitals', 'Caps'],
        'WPG': ['Winnipeg Jets', 'Jets']
    }
    
    def __init__(self, time_threshold_hours: float = 96.0):
        """
        Initialize GameMatcher
        
        Args:
            time_threshold_hours: Maximum time difference for matching games (hours)
        """
        self.time_threshold = timedelta(hours=time_threshold_hours)
        
        # Combine all sport team aliases for comprehensive matching
        self.TEAM_ALIASES = self._build_combined_team_aliases()
    
    def align_games(self, pinnacle_games: List[Dict], kalshi_games: List[Dict]) -> List[Dict]:
        """
        Align games between Pinnacle and Kalshi data
        
        Args:
            pinnacle_games: List of normalized Pinnacle game data
            kalshi_games: List of normalized Kalshi game data
            
        Returns:
            List of aligned game pairs with both Pinnacle and Kalshi data
        """
        aligned_games = []
        used_kalshi_indices = set()
        
        for pinnacle_game in pinnacle_games:
            best_match = self._find_best_match(pinnacle_game, kalshi_games, used_kalshi_indices)
            
            if best_match is not None:
                kalshi_game, kalshi_index, confidence = best_match
                used_kalshi_indices.add(kalshi_index)
                
                aligned_game = {
                    'match_id': f"match_{len(aligned_games) + 1}",
                    'pinnacle_data': pinnacle_game,
                    'kalshi_data': kalshi_game,
                    'match_confidence': confidence,
                    'alignment_metadata': {
                        'matched_on': self._get_match_criteria(pinnacle_game, kalshi_game),
                        'time_difference': self._calculate_time_difference(pinnacle_game, kalshi_game),
                        'team_match_score': self._calculate_team_similarity(pinnacle_game, kalshi_game),
                        'aligned_at': datetime.now(timezone.utc).isoformat()
                    }
                }
                
                aligned_games.append(aligned_game)
        
        print(f"Aligned {len(aligned_games)} games out of {len(pinnacle_games)} Pinnacle games")
        return aligned_games
    
    def _find_best_match(self, pinnacle_game: Dict, kalshi_games: List[Dict], 
                        used_indices: set) -> Optional[Tuple[Dict, int, float]]:
        """Find the best matching Kalshi game for a Pinnacle game"""
        best_match = None
        best_confidence = 0.0
        best_index = -1
        
        for i, kalshi_game in enumerate(kalshi_games):
            if i in used_indices:
                continue
                
            confidence = self._calculate_match_confidence(pinnacle_game, kalshi_game)
            
            # Use sport-specific confidence threshold if available
            sport_threshold = self._get_sport_threshold(pinnacle_game, kalshi_game)
            if confidence > best_confidence and confidence >= sport_threshold:
                best_match = kalshi_game
                best_confidence = confidence
                best_index = i
        
        if best_match is not None:
            return (best_match, best_index, best_confidence)
        return None
    
    def _calculate_match_confidence(self, pinnacle_game: Dict, kalshi_game: Dict) -> float:
        """Calculate confidence score for matching two games"""
        scores = []
        
        # 1. Sport compatibility check
        pinnacle_sport = pinnacle_game.get('sport', '').upper()
        kalshi_sport = kalshi_game.get('sport', '').upper()
        
        if pinnacle_sport and kalshi_sport and pinnacle_sport != kalshi_sport:
            return 0.0  # Different sports = no match
        
        # 2. Team similarity (most important)
        team_score = self._calculate_team_similarity(pinnacle_game, kalshi_game)
        scores.append(team_score * 0.6)  # 60% weight
        
        # 3. Time proximity
        time_score = self._calculate_time_similarity(pinnacle_game, kalshi_game)
        scores.append(time_score * 0.3)  # 30% weight
        
        # 4. Date match
        date_score = self._calculate_date_similarity(pinnacle_game, kalshi_game)
        scores.append(date_score * 0.1)  # 10% weight
        
        return sum(scores)
    
    def _calculate_team_similarity(self, pinnacle_game: Dict, kalshi_game: Dict) -> float:
        """Calculate team name similarity score"""
        pinnacle_home = pinnacle_game.get('home_team', '').upper()
        pinnacle_away = pinnacle_game.get('away_team', '').upper()
        kalshi_home = kalshi_game.get('home_team', '').upper()
        kalshi_away = kalshi_game.get('away_team', '').upper()
        
        # Direct match (best case)
        if (pinnacle_home == kalshi_home and pinnacle_away == kalshi_away) or \
           (pinnacle_home == kalshi_away and pinnacle_away == kalshi_home):
            return 1.0
        
        # Check aliases and variations
        home_similarity = self._get_team_similarity(pinnacle_home, kalshi_home)
        away_similarity = self._get_team_similarity(pinnacle_away, kalshi_away)
        
        # Check reversed matchup
        home_similarity_rev = self._get_team_similarity(pinnacle_home, kalshi_away)
        away_similarity_rev = self._get_team_similarity(pinnacle_away, kalshi_home)
        
        # Take the better of the two arrangements
        direct_score = (home_similarity + away_similarity) / 2
        reversed_score = (home_similarity_rev + away_similarity_rev) / 2
        
        return max(direct_score, reversed_score)
    
    def _build_combined_team_aliases(self) -> Dict[str, List[str]]:
        """Build combined team aliases from all sports configurations"""
        combined_aliases = {}
        
        # Add all sport-specific team aliases
        for sport_config in SPORTS_CONFIG.values():
            combined_aliases.update(sport_config.team_aliases)
        
        # Add legacy aliases for any teams not covered
        for team, aliases in self.LEGACY_TEAM_ALIASES.items():
            if team not in combined_aliases:
                combined_aliases[team] = aliases
        
        return combined_aliases
    
    def _get_sport_threshold(self, pinnacle_game: Dict, kalshi_game: Dict) -> float:
        """Get sport-specific confidence threshold"""
        # Try to determine sport from game data
        sport_key = None
        
        # Check if sport is explicitly set in game data
        if 'sport' in pinnacle_game:
            sport_key = pinnacle_game['sport'].lower()
        elif 'sport' in kalshi_game:
            sport_key = kalshi_game['sport'].lower()
        
        # Get sport config and return threshold
        if sport_key:
            sport_config = get_sport_config(sport_key)
            if sport_config:
                return sport_config.match_confidence_threshold
        
        # Default threshold if sport not found
        return 0.4
    
    def _get_team_similarity(self, team1: str, team2: str) -> float:
        """Calculate similarity between two team names using dynamic sport configs"""
        if team1 == team2:
            return 1.0
        
        # Check aliases from combined team mappings
        for standard_name, aliases in self.TEAM_ALIASES.items():
            if (team1 == standard_name or team1 in [alias.upper() for alias in aliases]) and \
               (team2 == standard_name or team2 in [alias.upper() for alias in aliases]):
                return 1.0
        
        # String similarity as fallback
        return SequenceMatcher(None, team1, team2).ratio()
    
    def _calculate_time_similarity(self, pinnacle_game: Dict, kalshi_game: Dict) -> float:
        """Calculate time proximity similarity score"""
        time_diff = self._calculate_time_difference(pinnacle_game, kalshi_game)
        
        if time_diff is None:
            return 0.5  # Neutral score if no time data
        
        # Perfect match within 15 minutes
        if time_diff < timedelta(minutes=15):
            return 1.0
        
        # Good match within threshold
        if time_diff < self.time_threshold:
            # Decay score based on time difference
            ratio = time_diff.total_seconds() / self.time_threshold.total_seconds()
            return max(0.0, 1.0 - ratio)
        
        return 0.0
    
    def _calculate_date_similarity(self, pinnacle_game: Dict, kalshi_game: Dict) -> float:
        """Calculate date similarity score"""
        pinnacle_date = pinnacle_game.get('game_date')
        kalshi_date = kalshi_game.get('game_date')
        
        if not pinnacle_date or not kalshi_date:
            return 0.5  # Neutral if no date data
        
        return 1.0 if pinnacle_date == kalshi_date else 0.0
    
    def _calculate_time_difference(self, pinnacle_game: Dict, kalshi_game: Dict) -> Optional[timedelta]:
        """Calculate time difference between two games"""
        pinnacle_time = pinnacle_game.get('game_time')
        kalshi_time = kalshi_game.get('game_time')
        
        if not pinnacle_time or not kalshi_time:
            return None
        
        try:
            pinnacle_dt = datetime.fromisoformat(pinnacle_time.replace('Z', '+00:00'))
            kalshi_dt = datetime.fromisoformat(kalshi_time.replace('Z', '+00:00'))
            return abs(pinnacle_dt - kalshi_dt)
        except:
            return None
    
    def _get_match_criteria(self, pinnacle_game: Dict, kalshi_game: Dict) -> List[str]:
        """Get list of criteria used for matching"""
        criteria = []
        
        # Check what matched
        if pinnacle_game.get('game_date') == kalshi_game.get('game_date'):
            criteria.append('date_match')
        
        team_similarity = self._calculate_team_similarity(pinnacle_game, kalshi_game)
        if team_similarity >= 0.9:
            criteria.append('team_exact_match')
        elif team_similarity >= 0.7:
            criteria.append('team_fuzzy_match')
        
        time_diff = self._calculate_time_difference(pinnacle_game, kalshi_game)
        if time_diff and time_diff < timedelta(hours=1):
            criteria.append('time_proximity')
        
        return criteria


class MispricingDetector:
    """Class for detecting mispricing opportunities between aligned games"""
    
    def __init__(self, min_edge_threshold: float = 0.05, min_confidence: float = 0.4):
        """
        Initialize MispricingDetector
        
        Args:
            min_edge_threshold: Minimum edge percentage to consider an opportunity
            min_confidence: Minimum match confidence to analyze
        """
        self.min_edge = min_edge_threshold
        self.min_confidence = min_confidence
    
    def detect_opportunities(self, aligned_games: List[Dict]) -> List[Dict]:
        """
        Detect mispricing opportunities in aligned games
        
        Args:
            aligned_games: List of aligned game data
            
        Returns:
            List of mispricing opportunities
        """
        opportunities = []
        
        for game in aligned_games:
            if game.get('match_confidence', 0) < self.min_confidence:
                continue
                
            opportunity = self._analyze_game_for_mispricing(game)
            if opportunity:
                opportunities.append(opportunity)
        
        print(f"Found {len(opportunities)} mispricing opportunities")
        return opportunities
    
    def _analyze_game_for_mispricing(self, aligned_game: Dict) -> Optional[Dict]:
        """Analyze a single aligned game for mispricing"""
        pinnacle_data = aligned_game['pinnacle_data']
        kalshi_data = aligned_game['kalshi_data']
        
        # Get implied probabilities
        p_home_prob = pinnacle_data['home_odds']['implied_probability']
        p_away_prob = pinnacle_data['away_odds']['implied_probability']
        k_home_prob = kalshi_data['home_odds']['implied_probability']
        k_away_prob = kalshi_data['away_odds']['implied_probability']
        
        # Calculate edges
        home_edge = abs(p_home_prob - k_home_prob)
        away_edge = abs(p_away_prob - k_away_prob)
        
        max_edge = max(home_edge, away_edge)
        
        if max_edge < self.min_edge:
            return None
        
        # Determine best opportunity
        if home_edge > away_edge:
            best_side = 'home'
            edge = home_edge
            pinnacle_prob = p_home_prob
            kalshi_prob = k_home_prob
        else:
            best_side = 'away'
            edge = away_edge
            pinnacle_prob = p_away_prob
            kalshi_prob = k_away_prob
        
        # Calculate expected value and other metrics
        expected_value = self._calculate_expected_value(pinnacle_prob, kalshi_prob)
        kelly_fraction = self._calculate_kelly_fraction(pinnacle_prob, kalshi_prob)
        
        opportunity = {
            'opportunity_id': f"opp_{aligned_game['match_id']}",
            'game_data': aligned_game,
            'pinnacle_odds': pinnacle_data,
            'kalshi_odds': kalshi_data,
            'discrepancy': {
                'home_team_diff': abs(p_home_prob - k_home_prob),
                'away_team_diff': abs(p_away_prob - k_away_prob),
                'max_edge': max_edge,
                'recommended_side': best_side
            },
            'profit_analysis': {
                'expected_value': expected_value,
                'kelly_fraction': kelly_fraction,
                'confidence_score': aligned_game.get('match_confidence', 0) * (edge / 0.1)  # Scale by edge size
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return opportunity
    
    def _calculate_expected_value(self, true_prob: float, market_prob: float) -> float:
        """Calculate expected value of the bet"""
        if market_prob <= 0:
            return 0.0
        return (true_prob / market_prob) - 1
    
    def _calculate_kelly_fraction(self, true_prob: float, market_prob: float) -> float:
        """Calculate Kelly criterion bet sizing"""
        if market_prob <= 0 or market_prob >= 1:
            return 0.0
        
        decimal_odds = 1 / market_prob
        kelly = (true_prob * decimal_odds - 1) / (decimal_odds - 1)
        return max(0.0, min(kelly, 0.25))  # Cap at 25% of bankroll


# Test function
def test_data_aligner():
    """Test the data alignment functionality"""
    print("=== TESTING DATA ALIGNMENT ===")
    
    # Mock data for testing
    pinnacle_games = [
        {
            'game_id': 'pinnacle_1',
            'home_team': 'MIN',
            'away_team': 'OAK',
            'game_date': '2025-08-21',
            'game_time': '2025-08-21T17:11:00Z',
            'home_odds': {'implied_probability': 0.48},
            'away_odds': {'implied_probability': 0.54}
        }
    ]
    
    kalshi_games = [
        {
            'game_id': 'kalshi_1',
            'home_team': 'OAK',
            'away_team': 'MIN',
            'game_date': '2025-08-21', 
            'game_time': '2025-08-21T17:11:00Z',
            'home_odds': {'implied_probability': 0.55},
            'away_odds': {'implied_probability': 0.45}
        }
    ]
    
    # Test alignment
    matcher = GameMatcher()
    aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
    
    print(f"Aligned games: {len(aligned_games)}")
    if aligned_games:
        print(f"Match confidence: {aligned_games[0]['match_confidence']:.2f}")
        print(f"Match criteria: {aligned_games[0]['alignment_metadata']['matched_on']}")
    
    # Test mispricing detection
    detector = MispricingDetector(min_edge_threshold=0.02)
    opportunities = detector.detect_opportunities(aligned_games)
    
    print(f"Opportunities found: {len(opportunities)}")
    if opportunities:
        opp = opportunities[0]
        print(f"Max edge: {opp['discrepancy']['max_edge']:.1%}")
        print(f"Recommended side: {opp['discrepancy']['recommended_side']}")

if __name__ == "__main__":
    test_data_aligner()