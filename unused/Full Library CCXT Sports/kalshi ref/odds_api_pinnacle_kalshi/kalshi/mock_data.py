"""
Mock Kalshi data based on previous successful API calls
Use this when the API is unavailable
"""

# Sample MLB data based on previous API responses showing 84 markets
SAMPLE_MLB_GAMES = [
    {
        'league': 'MLB',
        'favorite': 'BAL',
        'dog': 'BOS', 
        'fav_odds': -120,
        'dog_odds': 105,
        'game_time': '2025-08-26 22:36 UTC',
        'game_date': '2025-08-26',
        'source': 'kalshi',
        'status': 'open'
    },
    {
        'league': 'MLB',
        'favorite': 'TEX',
        'dog': 'LAA',
        'fav_odds': -115,
        'dog_odds': 100,
        'game_time': '2025-08-27 00:06 UTC', 
        'game_date': '2025-08-27',
        'source': 'kalshi',
        'status': 'open'
    },
    {
        'league': 'MLB',
        'favorite': 'HOU',
        'dog': 'COL',
        'fav_odds': -310,
        'dog_odds': 260,
        'game_time': '2025-08-27 00:11 UTC',
        'game_date': '2025-08-27', 
        'source': 'kalshi',
        'status': 'open'
    }
]

# Sample NFL data based on previous API responses  
SAMPLE_NFL_GAMES = [
    {
        'league': 'NFL',
        'favorite': 'LAC',
        'dog': 'LV',
        'fav_odds': -143,
        'dog_odds': 156,
        'game_time': '2025-09-15 19:00 UTC',
        'game_date': '2025-09-15',
        'source': 'kalshi',
        'status': 'open'
    }
]

def get_mock_games(league='mlb'):
    """Return mock game data when API is unavailable"""
    if league.lower() == 'mlb':
        return SAMPLE_MLB_GAMES.copy()
    elif league.lower() == 'nfl':
        return SAMPLE_NFL_GAMES.copy()
    else:
        return []