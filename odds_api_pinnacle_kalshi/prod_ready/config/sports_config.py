"""
Sports Configuration Module - Centralized Sport Definitions
Easy hook for adding new leagues to the mispricing detection system
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SportConfig:
    """Configuration for a specific sport"""
    name: str
    pinnacle_key: str  # OddsAPI sport key
    kalshi_keywords: List[str]  # Keywords to search for in Kalshi
    kalshi_tickers: List[str]  # Known ticker patterns
    team_aliases: Dict[str, List[str]]  # Team name variations
    match_confidence_threshold: float  # Minimum confidence for alignment
    time_threshold_hours: float  # Max time difference for matching games
    min_edge_threshold: float  # Minimum edge to consider opportunity
    season_months: List[int]  # Months when sport is active (1-12)

# Centralized sports configuration
SPORTS_CONFIG = {
    'mlb': SportConfig(
        name='MLB',
        pinnacle_key='baseball_mlb',
        kalshi_keywords=[
            'mlbgame', 'baseball', 'mlb', 'athletics', 'twins', 'yankees', 'dodgers', 
            'giants', 'cubs', 'red sox', 'mets', 'braves', 'astros', 'cardinals',
            'angels', 'rangers', 'mariners', 'rays', 'orioles', 'royals', 'tigers',
            'phillies', 'pirates', 'nationals', 'marlins', 'rockies', 'padres'
        ],
        kalshi_tickers=['KXMLBGAME'],
        team_aliases={
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
            'SEA': ['Seattle Mariners', 'Mariners']
        },
        match_confidence_threshold=0.4,
        time_threshold_hours=6.0,
        min_edge_threshold=0.02,
        season_months=[3, 4, 5, 6, 7, 8, 9, 10]  # March through October
    ),
    
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
    ),
    
    'nba': SportConfig(
        name='NBA',
        pinnacle_key='basketball_nba',
        kalshi_keywords=[
            'nba', 'basketball', 'lakers', 'warriors', 'celtics', 'heat',
            'spurs', 'bulls', 'knicks', 'nets', 'sixers', 'clippers',
            'nuggets', 'suns', 'mavericks', 'rockets', 'bucks', 'raptors',
            'jazz', 'blazers', 'kings', 'grizzlies', 'pelicans', 'magic',
            'hornets', 'pistons', 'cavaliers', 'pacers', 'hawks', 'wizards',
            'thunder', 'timberwolves'
        ],
        kalshi_tickers=['KXNBAGAME'],
        team_aliases={
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
            'WAS': ['Washington Wizards', 'Wizards']
        },
        match_confidence_threshold=0.5,
        time_threshold_hours=8.0,
        min_edge_threshold=0.025,
        season_months=[10, 11, 12, 1, 2, 3, 4, 5, 6]  # October through June
    ),
    
    'nhl': SportConfig(
        name='NHL',
        pinnacle_key='icehockey_nhl',
        kalshi_keywords=[
            'nhl', 'hockey', 'rangers', 'bruins', 'maple leafs', 'canadiens',
            'blackhawks', 'red wings', 'penguins', 'flyers', 'capitals',
            'devils', 'islanders', 'lightning', 'panthers', 'hurricanes',
            'blue jackets', 'predators', 'blues', 'wild', 'avalanche',
            'stars', 'kings', 'ducks', 'sharks', 'flames', 'oilers',
            'canucks', 'golden knights', 'coyotes', 'jets', 'senators',
            'sabres', 'kraken'
        ],
        kalshi_tickers=['KXNHLGAME'],
        team_aliases={
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
        },
        match_confidence_threshold=0.5,
        time_threshold_hours=8.0,
        min_edge_threshold=0.03,
        season_months=[10, 11, 12, 1, 2, 3, 4, 5, 6]  # October through June
    ),
    
    'college_football': SportConfig(
        name='College Football',
        pinnacle_key='americanfootball_ncaaf',
        kalshi_keywords=[
            'college football', 'ncaaf', 'cfb', 'alabama', 'georgia', 'ohio state',
            'michigan', 'notre dame', 'texas', 'oklahoma', 'lsu', 'florida',
            'clemson', 'oregon', 'penn state', 'wisconsin', 'auburn', 'miami',
            'usc', 'nebraska', 'tennessee', 'florida state', 'virginia tech'
        ],
        kalshi_tickers=['KXNCAAFGAME'],
        team_aliases={},  # Would need extensive college team mapping
        match_confidence_threshold=0.6,
        time_threshold_hours=12.0,
        min_edge_threshold=0.04,
        season_months=[8, 9, 10, 11, 12, 1]  # August through January
    ),
    
    'college_basketball': SportConfig(
        name='College Basketball',
        pinnacle_key='basketball_ncaab',
        kalshi_keywords=[
            'college basketball', 'ncaab', 'cbb', 'duke', 'north carolina',
            'kentucky', 'kansas', 'villanova', 'gonzaga', 'ucla', 'arizona',
            'michigan state', 'syracuse', 'louisville', 'indiana', 'march madness'
        ],
        kalshi_tickers=[],  # College basketball not found on Kalshi
        team_aliases={},  # Would need extensive college team mapping
        match_confidence_threshold=0.6,
        time_threshold_hours=8.0,
        min_edge_threshold=0.035,
        season_months=[11, 12, 1, 2, 3, 4]  # November through April
    ),
    
    'wnba': SportConfig(
        name='WNBA',
        pinnacle_key='basketball_wnba',
        kalshi_keywords=[
            'wnba', 'womens basketball', 'liberty', 'sparks', 'storm', 'lynx',
            'sky', 'fever', 'mystics', 'dream', 'wings', 'sun', 'mercury', 'aces'
        ],
        kalshi_tickers=['KXWNBAGAME'],
        team_aliases={
            'ATL': ['Atlanta Dream', 'Dream'],
            'CHI': ['Chicago Sky', 'Sky'],
            'CONN': ['Connecticut Sun', 'Sun'],
            'DAL': ['Dallas Wings', 'Wings'],
            'IND': ['Indiana Fever', 'Fever'],
            'LV': ['Las Vegas Aces', 'Aces'],
            'MIN': ['Minnesota Lynx', 'Lynx'],
            'NY': ['New York Liberty', 'Liberty'],
            'PHX': ['Phoenix Mercury', 'Mercury'],
            'SEA': ['Seattle Storm', 'Storm'],
            'WAS': ['Washington Mystics', 'Mystics']
        },
        match_confidence_threshold=0.5,
        time_threshold_hours=6.0,
        min_edge_threshold=0.03,
        season_months=[5, 6, 7, 8, 9, 10]  # May through October
    ),
    
    'ufc': SportConfig(
        name='UFC',
        pinnacle_key='mixed_martial_arts',
        kalshi_keywords=[
            'ufc', 'mma', 'mixed martial arts', 'fight', 'fighter', 'octagon',
            'mcgregor', 'jones', 'adesanya', 'ngannou', 'poirier', 'diaz',
            'masvidal', 'covington', 'holloway', 'volkanovski', 'sterling',
            'ortega', 'walker', 'pavlovich'
        ],
        kalshi_tickers=['KXUFCFIGHT'],
        team_aliases={},  # UFC uses fighter names, not teams
        match_confidence_threshold=0.7,  # Higher confidence for fighter name matching
        time_threshold_hours=4.0,        # Fights are shorter events
        min_edge_threshold=0.04,         # Higher edge threshold for MMA volatility
        season_months=list(range(1, 13))  # UFC events year-round
    )
}

def get_sport_config(sport_key: str) -> Optional[SportConfig]:
    """Get configuration for a specific sport"""
    return SPORTS_CONFIG.get(sport_key.lower())

def get_available_sports() -> List[str]:
    """Get list of all available sport keys"""
    return list(SPORTS_CONFIG.keys())

def get_supported_sports_display() -> str:
    """Get human-readable list of supported sports"""
    return ", ".join([config.name for config in SPORTS_CONFIG.values()])

def is_sport_in_season(sport_key: str, month: int = None) -> bool:
    """Check if a sport is currently in season"""
    if month is None:
        from datetime import datetime
        month = datetime.now().month
    
    config = get_sport_config(sport_key)
    if not config:
        return False
    
    return month in config.season_months

def get_current_season_sports() -> List[str]:
    """Get list of sports currently in season"""
    from datetime import datetime
    current_month = datetime.now().month
    return [sport for sport in SPORTS_CONFIG.keys() if is_sport_in_season(sport, current_month)]

# Helper function for adding new sports
def create_new_sport_template(sport_name: str) -> str:
    """Generate a template for adding a new sport"""
    template = f"""
# Add this to SPORTS_CONFIG dictionary:

'{sport_name.lower()}': SportConfig(
    name='{sport_name}',
    pinnacle_key='',  # OddsAPI sport key (e.g., 'tennis_wta')
    kalshi_keywords=[
        # Add relevant keywords that appear in Kalshi market titles
        '{sport_name.lower()}', 'keyword1', 'keyword2'
    ],
    kalshi_tickers=[''],  # Known ticker patterns (e.g., 'kxtennis')
    team_aliases={{
        # Add team/player mappings
        # 'SHORT': ['Full Name', 'Alternate Name']
    }},
    match_confidence_threshold=0.5,  # Adjust based on sport complexity
    time_threshold_hours=8.0,  # Adjust based on typical scheduling
    min_edge_threshold=0.03,  # Adjust based on market efficiency
    season_months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # Active months
)
"""
    return template

if __name__ == "__main__":
    # Display available sports
    print("Available Sports Configuration:")
    print("=" * 50)
    for sport_key, config in SPORTS_CONFIG.items():
        print(f"{sport_key.upper()}: {config.name}")
        print(f"  Season: {config.season_months}")
        print(f"  Teams: {len(config.team_aliases)} defined")
        print(f"  Keywords: {len(config.kalshi_keywords)} defined")
        print()
    
    print("Current Season Sports:")
    current_sports = get_current_season_sports()
    print(", ".join(sport.upper() for sport in current_sports))