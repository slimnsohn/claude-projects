"""
NFL-Only Sports Configuration - Stripped down for core functionality
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SportConfig:
    """Configuration for NFL"""
    name: str
    pinnacle_key: str  # OddsAPI sport key
    kalshi_keywords: List[str]  # Keywords to search for in Kalshi
    kalshi_tickers: List[str]  # Known ticker patterns
    team_aliases: Dict[str, List[str]]  # Team name variations
    match_confidence_threshold: float  # Minimum confidence for alignment
    time_threshold_hours: float  # Max time difference for matching games
    min_edge_threshold: float  # Minimum edge to consider opportunity
    season_months: List[int]  # Months when sport is active (1-12)

# NFL-only configuration
SPORTS_CONFIG = {
    'nfl': SportConfig(
        name='NFL',
        pinnacle_key='americanfootball_nfl',
        kalshi_keywords=[
            'nfl', 'football', 'patriots', 'cowboys', 'steelers', 'packers', 
            'giants', 'eagles', 'broncos', 'seahawks', 'chiefs', 'raiders',
            'chargers', 'rams', 'saints', 'falcons', 'panthers', 'buccaneers',
            'dolphins', 'jets', 'bills', 'ravens', 'browns', 'bengals',
            'titans', 'colts', 'jaguars', 'texans', 'bears', 'lions',
            'vikings', 'cardinals', 'niners', '49ers'
        ],
        kalshi_tickers=['KXNFLGAME'],
        team_aliases={
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
            'WAS': ['Washington Commanders', 'Commanders']
        },
        match_confidence_threshold=0.5,
        time_threshold_hours=12.0,
        min_edge_threshold=0.03,
        season_months=[9, 10, 11, 12, 1, 2]  # September through February
    )
}

def get_sport_config(sport_key: str) -> Optional[SportConfig]:
    """Get configuration for a specific sport"""
    return SPORTS_CONFIG.get(sport_key.lower())

def get_available_sports() -> List[str]:
    """Get list of available sport keys (NFL only)"""
    return ['nfl']

def get_supported_sports_display() -> str:
    """Get human-readable list of supported sports"""
    return "NFL"

def is_sport_in_season(sport_key: str = 'nfl', month: int = None) -> bool:
    """Check if NFL is currently in season"""
    if month is None:
        from datetime import datetime
        month = datetime.now().month
    
    config = get_sport_config('nfl')
    return month in config.season_months if config else False

def get_current_season_sports() -> List[str]:
    """Get list of sports currently in season (NFL only)"""
    return ['nfl'] if is_sport_in_season('nfl') else []

if __name__ == "__main__":
    print("NFL Sports Configuration:")
    print("=" * 30)
    config = SPORTS_CONFIG['nfl']
    print(f"NFL: {config.name}")
    print(f"  Season: {config.season_months}")
    print(f"  Teams: {len(config.team_aliases)} defined")
    print(f"  Keywords: {len(config.kalshi_keywords)} defined")
    print()
    
    in_season = is_sport_in_season('nfl')
    print(f"NFL Currently in Season: {'YES' if in_season else 'NO'}")