"""
Data Manager for NFL teams and schedules
Manages team data, matching, and schedule information.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

from .models import Team, Game, Sport
from .utils import parse_timestamp, setup_logging


class NFLDataManager:
    """Manages NFL team data and schedule information"""
    
    def __init__(self, teams_file: Optional[str] = None, schedule_file: Optional[str] = None):
        """
        Initialize NFL data manager
        
        Args:
            teams_file: Path to NFL teams JSON file
            schedule_file: Path to NFL schedule JSON file
        """
        self.logger = setup_logging("nfl_data_manager")
        
        # Set default paths relative to project root
        project_root = Path(__file__).parent.parent
        self.teams_file = teams_file or str(project_root / "exploration" / "nfl_teams_2024.json")
        # Use comprehensive schedule with multiple weeks and dates
        self.schedule_file = schedule_file or str(project_root / "exploration" / "nfl_schedule_2024_comprehensive.json")
        
        self.teams_data = {}
        self.teams = {}  # abbrev -> Team object
        self.schedule_data = {}
        self.games = {}  # game_id -> Game object
        
        self._load_data()
        self._create_team_objects()
        self._create_game_objects()
    
    def _load_data(self):
        """Load teams and schedule data from JSON files"""
        try:
            # Load teams data
            with open(self.teams_file, 'r') as f:
                self.teams_data = json.load(f)
            self.logger.info(f"Loaded {len(self.teams_data.get('teams', {}))} NFL teams")
            
            # Load schedule data
            with open(self.schedule_file, 'r') as f:
                self.schedule_data = json.load(f)
            self.logger.info(f"Loaded {len(self.schedule_data.get('games', []))} NFL games")
            
        except FileNotFoundError as e:
            self.logger.error(f"Data file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in data file: {e}")
            raise
    
    def _create_team_objects(self):
        """Create Team objects from loaded data"""
        teams_raw = self.teams_data.get('teams', {})
        
        for abbrev, team_data in teams_raw.items():
            team = Team(
                name=team_data.get('name', ''),
                city=team_data.get('city', ''),
                nickname=team_data.get('nickname', ''),
                abbreviations=team_data.get('abbreviations', []),
                alternative_names=team_data.get('alternative_names', []),
                sport=Sport.NFL,
                conference=team_data.get('conference'),
                division=team_data.get('division')
            )
            self.teams[abbrev] = team
        
        self.logger.info(f"Created {len(self.teams)} Team objects")
    
    def _create_game_objects(self):
        """Create Game objects from loaded schedule data"""
        games_raw = self.schedule_data.get('games', [])
        
        for game_data in games_raw:
            home_abbrev = game_data.get('home_team')
            away_abbrev = game_data.get('away_team')
            
            if home_abbrev not in self.teams or away_abbrev not in self.teams:
                self.logger.warning(f"Unknown team in game: {home_abbrev} vs {away_abbrev}")
                continue
            
            game_date_str = game_data.get('game_date')
            game_date = parse_timestamp(game_date_str)
            if not game_date:
                self.logger.warning(f"Invalid game date: {game_date_str}")
                continue
            
            game = Game(
                game_id=game_data.get('game_id'),
                home_team=self.teams[home_abbrev],
                away_team=self.teams[away_abbrev],
                sport=Sport.NFL,
                game_date=game_date,
                season=str(game_data.get('season', '2024')),
                week=game_data.get('week'),
                venue=game_data.get('venue'),
                status=game_data.get('status'),
                metadata={
                    'tv_network': game_data.get('tv_network'),
                    'is_playoff': game_data.get('is_playoff', False),
                    'is_prime_time': game_data.get('is_prime_time', False)
                }
            )
            self.games[game.game_id] = game
        
        self.logger.info(f"Created {len(self.games)} Game objects")
    
    def get_team(self, identifier: str) -> Optional[Team]:
        """
        Get team by abbreviation, name, or city
        
        Args:
            identifier: Team abbreviation, name, or city
            
        Returns:
            Team object if found, None otherwise
        """
        # Direct abbreviation lookup
        if identifier.upper() in self.teams:
            return self.teams[identifier.upper()]
        
        # Search by matching
        identifier_upper = identifier.upper()
        for team in self.teams.values():
            if team.matches(identifier) > 0.8:
                return team
        
        return None
    
    def get_all_teams(self) -> Dict[str, Team]:
        """Get all teams"""
        return self.teams.copy()
    
    def get_game(self, game_id: str) -> Optional[Game]:
        """Get game by ID"""
        return self.games.get(game_id)
    
    def get_games_by_week(self, week: int, season: str = "2024") -> List[Game]:
        """Get all games for a specific week"""
        return [
            game for game in self.games.values()
            if game.week == week and game.season == season
        ]
    
    def get_games_by_teams(self, team1: Union[str, Team], 
                          team2: Union[str, Team]) -> List[Game]:
        """Get games between two teams"""
        if isinstance(team1, str):
            team1 = self.get_team(team1)
        if isinstance(team2, str):
            team2 = self.get_team(team2)
        
        if not team1 or not team2:
            return []
        
        games = []
        for game in self.games.values():
            teams_in_game = {game.home_team.name, game.away_team.name}
            search_teams = {team1.name, team2.name}
            if teams_in_game == search_teams:
                games.append(game)
        
        return games
    
    def get_games_by_date_range(self, start_date: datetime, 
                               end_date: datetime) -> List[Game]:
        """Get games within date range"""
        return [
            game for game in self.games.values()
            if start_date <= game.game_date <= end_date
        ]
    
    def find_game(self, home_team: Union[str, Team], away_team: Union[str, Team], 
                 week: Optional[int] = None) -> Optional[Game]:
        """
        Find a specific game by teams and optional week
        
        Args:
            home_team: Home team (name, abbrev, or Team object)
            away_team: Away team (name, abbrev, or Team object)
            week: Optional week number for filtering
            
        Returns:
            Game object if found, None otherwise
        """
        if isinstance(home_team, str):
            home_team = self.get_team(home_team)
        if isinstance(away_team, str):
            away_team = self.get_team(away_team)
        
        if not home_team or not away_team:
            return None
        
        for game in self.games.values():
            # Check both home/away arrangements
            match1 = (game.home_team.name == home_team.name and 
                     game.away_team.name == away_team.name)
            match2 = (game.home_team.name == away_team.name and 
                     game.away_team.name == home_team.name)
            
            if (match1 or match2) and (week is None or game.week == week):
                return game
        
        return None
    
    def get_team_schedule(self, team: Union[str, Team], 
                         season: str = "2024") -> List[Game]:
        """Get all games for a specific team"""
        if isinstance(team, str):
            team = self.get_team(team)
        
        if not team:
            return []
        
        return [
            game for game in self.games.values()
            if (game.home_team.name == team.name or game.away_team.name == team.name) 
            and game.season == season
        ]
    
    def validate_data_integrity(self) -> Dict[str, any]:
        """Validate data integrity and return report"""
        report = {
            'teams_count': len(self.teams),
            'games_count': len(self.games),
            'weeks_covered': set(),
            'teams_with_games': set(),
            'issues': []
        }
        
        # Check game data
        for game in self.games.values():
            if game.week:
                report['weeks_covered'].add(game.week)
            
            # Check if teams exist
            home_abbrev = None
            away_abbrev = None
            for abbrev, team in self.teams.items():
                if team.name == game.home_team.name:
                    home_abbrev = abbrev
                if team.name == game.away_team.name:
                    away_abbrev = abbrev
            
            if home_abbrev:
                report['teams_with_games'].add(home_abbrev)
            if away_abbrev:
                report['teams_with_games'].add(away_abbrev)
        
        # Find teams without games
        teams_without_games = set(self.teams.keys()) - report['teams_with_games']
        if teams_without_games:
            report['issues'].append(f"Teams without games: {teams_without_games}")
        
        # Check week coverage
        report['weeks_covered'] = sorted(report['weeks_covered'])
        expected_weeks = list(range(1, 19))  # NFL regular season
        missing_weeks = set(expected_weeks) - set(report['weeks_covered'])
        if missing_weeks:
            report['issues'].append(f"Missing weeks: {sorted(missing_weeks)}")
        
        return report


# Global instance for easy access
_nfl_data_manager = None

def get_nfl_data_manager() -> NFLDataManager:
    """Get global NFL data manager instance"""
    global _nfl_data_manager
    if _nfl_data_manager is None:
        _nfl_data_manager = NFLDataManager()
    return _nfl_data_manager