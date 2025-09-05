"""
NFL Schedule Data Collection
Comprehensive NFL schedule data for the 2024-2025 season with game identification logic
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class NFLGame:
    """Represents an NFL game with identification information"""
    game_id: str
    week: int
    season: int
    game_date: datetime
    home_team: str
    away_team: str
    game_time: str  # Original time string
    status: str = "scheduled"
    tv_network: str = ""
    is_playoff: bool = False
    is_prime_time: bool = False
    venue: str = ""


# Sample 2024 NFL Regular Season Schedule (partial - showing structure)
# In a real implementation, this would be loaded from an API or comprehensive data source
NFL_2024_SCHEDULE_SAMPLE = [
    # Week 1
    {
        "game_id": "2024_week1_kc_bal",
        "week": 1,
        "season": 2024,
        "date": "2024-09-05",
        "time": "20:20",
        "home_team": "KC", 
        "away_team": "BAL",
        "venue": "Arrowhead Stadium",
        "tv": "NBC",
        "prime_time": True
    },
    {
        "game_id": "2024_week1_gb_phi",
        "week": 1,
        "season": 2024,
        "date": "2024-09-06",
        "time": "20:15",
        "home_team": "PHI",
        "away_team": "GB",
        "venue": "Lincoln Financial Field", 
        "tv": "NBC",
        "prime_time": True
    },
    # Week 2 examples
    {
        "game_id": "2024_week2_dal_no",
        "week": 2,
        "season": 2024,
        "date": "2024-09-15",
        "time": "13:00",
        "home_team": "NO",
        "away_team": "DAL",
        "venue": "Caesars Superdome",
        "tv": "FOX"
    },
    {
        "game_id": "2024_week2_pit_den",
        "week": 2,
        "season": 2024,
        "date": "2024-09-15",
        "time": "16:25",
        "home_team": "DEN",
        "away_team": "PIT", 
        "venue": "Empower Field at Mile High",
        "tv": "CBS"
    },
    # Add more sample games...
]

# Key dates for 2024-2025 NFL Season
NFL_2024_KEY_DATES = {
    "season_start": "2024-09-05",
    "season_end": "2025-01-05", 
    "playoff_start": "2025-01-11",
    "conference_championships": "2025-01-26",
    "super_bowl": "2025-02-09",
    "draft": "2024-04-25",
    "regular_season_weeks": 18,
    "games_per_team": 17
}

# 2025 Season preview (schedule not yet released as of search date)
NFL_2025_PREVIEW = {
    "season_start": "2025-09-04",
    "season_end": "2026-01-04",
    "playoff_start": "2026-01-10", 
    "super_bowl": "2026-02-08",
    "super_bowl_location": "Levi's Stadium, Santa Clara, CA",
    "schedule_release": "2025-05-14",
    "international_games": 8,
    "kickoff_game": "PHI vs DAL"
}


class NFLScheduleManager:
    """Manages NFL schedule data and provides game lookup functionality"""
    
    def __init__(self):
        """Initialize schedule manager with sample data"""
        self.games = []
        self.games_by_week = {}
        self.games_by_team = {}
        self.games_by_date = {}
        
        # Load sample data
        self._load_sample_schedule()
        self._build_indices()
    
    def _load_sample_schedule(self):
        """Load sample schedule data"""
        for game_data in NFL_2024_SCHEDULE_SAMPLE:
            game = NFLGame(
                game_id=game_data["game_id"],
                week=game_data["week"],
                season=game_data["season"],
                game_date=datetime.strptime(f"{game_data['date']} {game_data['time']}", "%Y-%m-%d %H:%M"),
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                game_time=game_data["time"],
                tv_network=game_data.get("tv", ""),
                is_prime_time=game_data.get("prime_time", False),
                venue=game_data.get("venue", "")
            )
            self.games.append(game)
    
    def _build_indices(self):
        """Build lookup indices for efficient game searching"""
        self.games_by_week = {}
        self.games_by_team = {}
        self.games_by_date = {}
        
        for game in self.games:
            # Index by week
            if game.week not in self.games_by_week:
                self.games_by_week[game.week] = []
            self.games_by_week[game.week].append(game)
            
            # Index by team
            for team in [game.home_team, game.away_team]:
                if team not in self.games_by_team:
                    self.games_by_team[team] = []
                self.games_by_team[team].append(game)
            
            # Index by date
            date_key = game.game_date.strftime("%Y-%m-%d")
            if date_key not in self.games_by_date:
                self.games_by_date[date_key] = []
            self.games_by_date[date_key].append(game)
    
    def find_game(self, home_team: str = None, away_team: str = None, 
                  week: int = None, date: str = None) -> List[NFLGame]:
        """
        Find games matching the given criteria
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation  
            week: Week number
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of matching games
        """
        candidates = self.games.copy()
        
        # Filter by week
        if week is not None:
            candidates = [g for g in candidates if g.week == week]
        
        # Filter by date
        if date is not None:
            candidates = [g for g in candidates if g.game_date.strftime("%Y-%m-%d") == date]
        
        # Filter by home team
        if home_team is not None:
            candidates = [g for g in candidates if g.home_team == home_team.upper()]
        
        # Filter by away team  
        if away_team is not None:
            candidates = [g for g in candidates if g.away_team == away_team.upper()]
        
        return candidates
    
    def find_matchup(self, team1: str, team2: str, week_range: tuple = None) -> List[NFLGame]:
        """
        Find games between two specific teams (regardless of home/away)
        
        Args:
            team1: First team abbreviation
            team2: Second team abbreviation
            week_range: Optional (min_week, max_week) tuple
            
        Returns:
            List of matching games
        """
        team1 = team1.upper()
        team2 = team2.upper()
        
        matches = []
        for game in self.games:
            teams_in_game = {game.home_team, game.away_team}
            if {team1, team2} == teams_in_game:
                if week_range is None or (week_range[0] <= game.week <= week_range[1]):
                    matches.append(game)
        
        return matches
    
    def get_team_schedule(self, team: str, max_games: int = None) -> List[NFLGame]:
        """Get all games for a specific team"""
        team = team.upper()
        team_games = self.games_by_team.get(team, [])
        
        # Sort by game date
        team_games.sort(key=lambda g: g.game_date)
        
        if max_games:
            return team_games[:max_games]
        return team_games
    
    def get_week_games(self, week: int) -> List[NFLGame]:
        """Get all games for a specific week"""
        return self.games_by_week.get(week, [])
    
    def get_games_by_date_range(self, start_date: str, end_date: str) -> List[NFLGame]:
        """Get games within a date range"""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        matches = []
        for game in self.games:
            if start_dt <= game.game_date <= end_dt:
                matches.append(game)
        
        return sorted(matches, key=lambda g: g.game_date)
    
    def generate_game_id(self, home_team: str, away_team: str, 
                        game_date: datetime, week: int = None) -> str:
        """Generate standardized game ID"""
        date_str = game_date.strftime("%Y%m%d")
        week_str = f"_week{week}" if week else ""
        return f"nfl_{game_date.year}{week_str}_{away_team.lower()}_{home_team.lower()}_{date_str}"
    
    def is_game_today(self, game: NFLGame) -> bool:
        """Check if game is scheduled for today"""
        today = datetime.now().date()
        return game.game_date.date() == today
    
    def is_game_this_week(self, game: NFLGame) -> bool:
        """Check if game is in current week"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start.date() <= game.game_date.date() <= week_end.date()


def create_extended_schedule():
    """Create extended schedule with more sample games for testing"""
    extended_games = []
    
    # Week 1 games (more complete)
    week1_games = [
        ("KC", "BAL", "2024-09-05", "20:20", "NBC", True),
        ("PHI", "GB", "2024-09-06", "20:15", "NBC", True), 
        ("BUF", "ARI", "2024-09-08", "13:00", "CBS", False),
        ("PIT", "ATL", "2024-09-08", "13:00", "FOX", False),
        ("HOU", "IND", "2024-09-08", "13:00", "CBS", False),
        ("CHI", "TEN", "2024-09-08", "13:00", "FOX", False),
        ("CIN", "NE", "2024-09-08", "13:00", "CBS", False),
        ("MIA", "JAX", "2024-09-08", "13:00", "CBS", False),
        ("MIN", "NYG", "2024-09-08", "13:00", "FOX", False),
        ("CLE", "DAL", "2024-09-08", "16:25", "FOX", False),
        ("LV", "LAC", "2024-09-08", "16:25", "CBS", False),
        ("SEA", "DEN", "2024-09-08", "16:25", "CBS", False),
        ("CAR", "NO", "2024-09-08", "13:00", "FOX", False),
        ("WAS", "TB", "2024-09-08", "16:25", "FOX", False),
        ("NYJ", "SF", "2024-09-09", "20:15", "ESPN", True),
        ("LAR", "DET", "2024-09-08", "20:20", "NBC", True),
    ]
    
    for i, (home, away, date, time, tv, prime) in enumerate(week1_games):
        game_data = {
            "game_id": f"2024_week1_{away.lower()}_{home.lower()}",
            "week": 1,
            "season": 2024,
            "date": date,
            "time": time,
            "home_team": home,
            "away_team": away,
            "tv": tv,
            "prime_time": prime
        }
        extended_games.append(game_data)
    
    # Add some Week 2 games for variety
    week2_games = [
        ("NO", "DAL", "2024-09-15", "13:00", "FOX", False),
        ("DEN", "PIT", "2024-09-15", "16:25", "CBS", False),
        ("IND", "GB", "2024-09-15", "13:00", "FOX", False),
        ("SF", "MIN", "2024-09-15", "13:00", "CBS", False),
        ("NYG", "WAS", "2024-09-15", "13:00", "FOX", False),
        ("LAC", "CAR", "2024-09-15", "13:00", "CBS", False),
        ("LV", "BAL", "2024-09-15", "13:00", "CBS", False),
        ("TB", "DET", "2024-09-15", "13:00", "FOX", False),
        ("SEA", "NE", "2024-09-15", "13:00", "FOX", False),
        ("NYJ", "TEN", "2024-09-15", "13:00", "CBS", False),
        ("CLE", "JAX", "2024-09-15", "13:00", "CBS", False),
        ("KC", "CIN", "2024-09-15", "16:25", "CBS", False),
        ("LAR", "ARI", "2024-09-15", "16:05", "FOX", False),
        ("CHI", "HOU", "2024-09-15", "20:20", "NBC", True),
        ("ATL", "PHI", "2024-09-16", "20:15", "ESPN", True),
    ]
    
    for home, away, date, time, tv, prime in week2_games:
        game_data = {
            "game_id": f"2024_week2_{away.lower()}_{home.lower()}",
            "week": 2,
            "season": 2024,
            "date": date,
            "time": time,
            "home_team": home,
            "away_team": away,
            "tv": tv,
            "prime_time": prime
        }
        extended_games.append(game_data)
    
    return extended_games


def validate_schedule_data():
    """Validate schedule data and functionality"""
    print("=== NFL SCHEDULE DATA VALIDATION ===")
    
    # Test basic schedule manager
    manager = NFLScheduleManager()
    
    print(f"OK Loaded {len(manager.games)} sample games")
    print(f"OK Games indexed by {len(manager.games_by_week)} weeks")
    print(f"OK Games indexed for {len(manager.games_by_team)} teams")
    
    # Test game finding
    kc_games = manager.get_team_schedule("KC")
    print(f"OK Found {len(kc_games)} games for Kansas City")
    
    week1_games = manager.get_week_games(1)
    print(f"OK Found {len(week1_games)} games in Week 1")
    
    # Test matchup finding
    kc_bal = manager.find_matchup("KC", "BAL")
    if kc_bal:
        game = kc_bal[0]
        print(f"OK Found KC vs BAL matchup: {game.away_team} @ {game.home_team} on {game.game_date.strftime('%Y-%m-%d')}")
    
    # Test game ID generation
    test_date = datetime(2024, 9, 8, 13, 0)
    test_id = manager.generate_game_id("KC", "DEN", test_date, 1)
    print(f"OK Generated game ID: {test_id}")
    
    # Test date range searching
    week1_start = "2024-09-05"
    week1_end = "2024-09-09"
    week1_range_games = manager.get_games_by_date_range(week1_start, week1_end)
    print(f"OK Found {len(week1_range_games)} games in date range {week1_start} to {week1_end}")
    
    print("Schedule validation successful!")


def export_schedule_data():
    """Export schedule data for use in other modules"""
    manager = NFLScheduleManager()
    
    # Export comprehensive schedule data
    export_data = {
        "season": "2024",
        "games": [],
        "key_dates": NFL_2024_KEY_DATES,
        "season_2025_preview": NFL_2025_PREVIEW,
        "generated_at": datetime.now().isoformat()
    }
    
    # Convert games to serializable format
    for game in manager.games:
        game_dict = {
            "game_id": game.game_id,
            "week": game.week,
            "season": game.season,
            "game_date": game.game_date.isoformat(),
            "home_team": game.home_team,
            "away_team": game.away_team,
            "game_time": game.game_time,
            "status": game.status,
            "tv_network": game.tv_network,
            "is_playoff": game.is_playoff,
            "is_prime_time": game.is_prime_time,
            "venue": game.venue
        }
        export_data["games"].append(game_dict)
    
    # Add team schedules
    export_data["team_schedules"] = {}
    for team in manager.games_by_team.keys():
        team_games = manager.get_team_schedule(team)
        export_data["team_schedules"][team] = [g.game_id for g in team_games]
    
    # Add week schedules  
    export_data["week_schedules"] = {}
    for week in manager.games_by_week.keys():
        week_games = manager.get_week_games(week)
        export_data["week_schedules"][week] = [g.game_id for g in week_games]
    
    output_file = 'nfl_schedule_2024.json'
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Schedule data exported to {output_file}")
    return output_file


if __name__ == "__main__":
    # Validate schedule functionality
    validate_schedule_data()
    
    # Export schedule data
    export_file = export_schedule_data()
    
    print(f"\n=== NFL SCHEDULE DATA SUMMARY ===")
    print(f"Season: {NFL_2024_KEY_DATES['season_start']} to {NFL_2024_KEY_DATES['season_end']}")
    print(f"Regular season weeks: {NFL_2024_KEY_DATES['regular_season_weeks']}")
    print(f"Games per team: {NFL_2024_KEY_DATES['games_per_team']}")
    print(f"Playoffs start: {NFL_2024_KEY_DATES['playoff_start']}")
    print(f"Super Bowl: {NFL_2024_KEY_DATES['super_bowl']}")
    
    print(f"\n2025 Season Preview:")
    print(f"Season start: {NFL_2025_PREVIEW['season_start']}")
    print(f"Schedule release: {NFL_2025_PREVIEW['schedule_release']}")
    print(f"International games: {NFL_2025_PREVIEW['international_games']}")
    print(f"Super Bowl location: {NFL_2025_PREVIEW['super_bowl_location']}")
    
    # Show some example game lookups
    print(f"\n=== EXAMPLE GAME LOOKUPS ===")
    manager = NFLScheduleManager()
    
    # Show team schedule
    kc_schedule = manager.get_team_schedule("KC", 3)
    print(f"Kansas City first 3 games:")
    for game in kc_schedule:
        vs_team = game.away_team if game.home_team == "KC" else game.home_team
        home_away = "vs" if game.home_team == "KC" else "@"
        print(f"  Week {game.week}: {home_away} {vs_team} on {game.game_date.strftime('%m/%d/%Y')}")
    
    # Show week games
    week1 = manager.get_week_games(1)
    print(f"\nWeek 1 games ({len(week1)} total):")
    for game in week1[:3]:  # Show first 3
        print(f"  {game.away_team} @ {game.home_team} - {game.game_date.strftime('%m/%d %H:%M')} ({game.tv_network})")