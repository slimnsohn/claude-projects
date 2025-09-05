"""
Improved Game Alignment for NFL
Uses proper team name standardization to match games between platforms
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from nfl_team_mapper import NFLTeamMapper

class ImprovedGameAligner:
    """Improved game aligner with better team name matching"""
    
    def __init__(self, time_threshold_hours: float = 168.0):  # 7 days
        """
        Initialize aligner
        
        Args:
            time_threshold_hours: Maximum time difference for matching games (default: 7 days)
        """
        self.time_threshold = timedelta(hours=time_threshold_hours)
        self.mapper = NFLTeamMapper()
    
    def align_games(self, pinnacle_games: List[Dict], kalshi_games: List[Dict]) -> List[Dict]:
        """
        Align games between Pinnacle and Kalshi using improved matching
        
        Args:
            pinnacle_games: List of Pinnacle game data
            kalshi_games: List of Kalshi game data
            
        Returns:
            List of aligned game pairs
        """
        print(f"\\nAttempting to align {len(pinnacle_games)} Pinnacle games with {len(kalshi_games)} Kalshi games...")
        
        aligned_games = []
        used_kalshi_indices = set()
        match_details = []
        
        for i, pinnacle_game in enumerate(pinnacle_games):
            best_match = self._find_best_match(pinnacle_game, kalshi_games, used_kalshi_indices)
            
            if best_match is not None:
                kalshi_game, kalshi_index, confidence, match_reason = best_match
                used_kalshi_indices.add(kalshi_index)
                
                aligned_game = {
                    'match_id': f"match_{len(aligned_games) + 1}",
                    'pinnacle_data': pinnacle_game,
                    'kalshi_data': kalshi_game,
                    'match_confidence': confidence,
                    'match_reason': match_reason,
                    'team_codes': {
                        'pinnacle_home': self.mapper.standardize_team_name(pinnacle_game.get('home', ''), 'pinnacle'),
                        'pinnacle_away': self.mapper.standardize_team_name(pinnacle_game.get('away', ''), 'pinnacle'),
                        'kalshi_home': self.mapper.standardize_team_name(kalshi_game.get('home', ''), 'kalshi'),
                        'kalshi_away': self.mapper.standardize_team_name(kalshi_game.get('away', ''), 'kalshi')
                    }
                }
                
                aligned_games.append(aligned_game)
                match_details.append(f"[MATCH] {pinnacle_game.get('away', '')} @ {pinnacle_game.get('home', '')} -> {kalshi_game.get('away', '')} @ {kalshi_game.get('home', '')} ({match_reason})")
            else:
                # Log failed matches for debugging
                p_home = self.mapper.standardize_team_name(pinnacle_game.get('home', ''), 'pinnacle')
                p_away = self.mapper.standardize_team_name(pinnacle_game.get('away', ''), 'pinnacle')
                match_details.append(f"[NO MATCH] {pinnacle_game.get('away', '')} @ {pinnacle_game.get('home', '')} ({p_away}-{p_home}) - No match found")
        
        print(f"Successfully aligned {len(aligned_games)} games")
        
        # Show match details
        if match_details:
            print("\\nAlignment Details:")
            for detail in match_details[:10]:  # Show first 10
                print(f"  {detail}")
            if len(match_details) > 10:
                print(f"  ... and {len(match_details) - 10} more")
        
        return aligned_games
    
    def _find_best_match(self, pinnacle_game: Dict, kalshi_games: List[Dict], 
                        used_indices: set) -> Optional[Tuple[Dict, int, float, str]]:
        """Find the best matching Kalshi game for a Pinnacle game"""
        best_match = None
        best_confidence = 0.0
        best_index = -1
        best_reason = ""
        
        for i, kalshi_game in enumerate(kalshi_games):
            if i in used_indices:
                continue
            
            confidence, reason = self._calculate_match_confidence(pinnacle_game, kalshi_game)
            
            if confidence > best_confidence and confidence >= 0.7:  # Require 70% confidence
                best_match = kalshi_game
                best_confidence = confidence
                best_index = i
                best_reason = reason
        
        if best_match is not None:
            return (best_match, best_index, best_confidence, best_reason)
        return None
    
    def _calculate_match_confidence(self, pinnacle_game: Dict, kalshi_game: Dict) -> Tuple[float, str]:
        """
        Calculate confidence score for matching two games
        
        Returns:
            Tuple of (confidence_score, reason_string)
        """
        # Check team matching using improved mapper
        teams_match = self.mapper.games_match(pinnacle_game, kalshi_game)
        
        if not teams_match:
            return 0.0, "teams_mismatch"
        
        # Teams match! Now check time proximity
        time_score, time_reason = self._calculate_time_score(pinnacle_game, kalshi_game)
        
        # Base confidence is high for team match
        base_confidence = 0.8
        final_confidence = base_confidence + (time_score * 0.2)  # Time adds up to 20%
        
        reason = f"teams_match"
        if time_reason:
            reason += f"+{time_reason}"
        
        return min(final_confidence, 1.0), reason
    
    def _calculate_time_score(self, pinnacle_game: Dict, kalshi_game: Dict) -> Tuple[float, str]:
        """Calculate time proximity score"""
        pin_time_str = pinnacle_game.get('game_time', '')
        kal_time_str = kalshi_game.get('game_time', '')
        
        if not pin_time_str or not kal_time_str:
            return 0.5, "no_time"
        
        try:
            # Parse times - handle different formats
            pin_time = self._parse_time(pin_time_str)
            kal_time = self._parse_time(kal_time_str)
            
            if not pin_time or not kal_time:
                return 0.5, "time_parse_fail"
            
            time_diff = abs(pin_time - kal_time)
            
            if time_diff < timedelta(hours=2):
                return 1.0, "time_exact"
            elif time_diff < timedelta(days=1):
                return 0.8, "time_close"
            elif time_diff < timedelta(days=7):
                return 0.5, "time_week"
            else:
                return 0.2, "time_far"
                
        except Exception:
            return 0.5, "time_error"
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string into datetime object"""
        if not time_str:
            return None
        
        # Common formats to try
        formats = [
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S+00:00'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str.replace('Z', ''), fmt.replace('Z', ''))
            except ValueError:
                continue
        
        return None

def test_alignment():
    """Test the improved alignment with sample data"""
    print("=== TESTING IMPROVED GAME ALIGNMENT ===")
    
    # Sample data mimicking real formats
    pinnacle_games = [
        {
            'home': 'Dallas Cowboys',
            'away': 'Philadelphia Eagles', 
            'game_time': '2025-09-05 00:20',
            'home_odds': -421,
            'away_odds': 348
        },
        {
            'home': 'Los Angeles Chargers',
            'away': 'Kansas City Chiefs',
            'game_time': '2025-09-06 00:00', 
            'home_odds': 152,
            'away_odds': -170
        }
    ]
    
    kalshi_games = [
        {
            'home': 'Dallas',
            'away': 'Philadelphia',
            'game_time': '2025-09-05 00:20',  # Same time
            'home_odds': -400,
            'away_odds': 354
        },
        {
            'home': 'Los Angeles C', 
            'away': 'Kansas City',
            'game_time': '2025-09-06 00:00',  # Same time
            'home_odds': -163,
            'away_odds': 156
        }
    ]
    
    aligner = ImprovedGameAligner()
    aligned = aligner.align_games(pinnacle_games, kalshi_games)
    
    print(f"\\nResult: {len(aligned)} games aligned")
    for i, game in enumerate(aligned, 1):
        print(f"{i}. Match confidence: {game['match_confidence']:.1%} ({game['match_reason']})")
        print(f"   Pinnacle: {game['pinnacle_data']['away']} @ {game['pinnacle_data']['home']}")
        print(f"   Kalshi: {game['kalshi_data']['away']} @ {game['kalshi_data']['home']}")
        print()

if __name__ == "__main__":
    test_alignment()