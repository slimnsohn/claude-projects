"""
NFL Team Name Standardization and Mapping
Maps between different naming conventions used by Pinnacle and Kalshi
"""

class NFLTeamMapper:
    """Maps NFL team names between different platforms"""
    
    # Map Kalshi short names to full team names
    KALSHI_TO_FULL = {
        'Arizona': 'Arizona Cardinals',
        'Atlanta': 'Atlanta Falcons', 
        'Baltimore': 'Baltimore Ravens',
        'Buffalo': 'Buffalo Bills',
        'Carolina': 'Carolina Panthers',
        'Chicago': 'Chicago Bears',
        'Cincinnati': 'Cincinnati Bengals',
        'Cleveland': 'Cleveland Browns',
        'Dallas': 'Dallas Cowboys',
        'Denver': 'Denver Broncos',
        'Detroit': 'Detroit Lions',
        'Green Bay': 'Green Bay Packers',
        'Houston': 'Houston Texans',
        'Indianapolis': 'Indianapolis Colts',
        'Jacksonville': 'Jacksonville Jaguars',
        'Kansas City': 'Kansas City Chiefs',
        'Las Vegas': 'Las Vegas Raiders',
        'Los Angeles C': 'Los Angeles Chargers',
        'Los Angeles R': 'Los Angeles Rams', 
        'Miami': 'Miami Dolphins',
        'Minnesota': 'Minnesota Vikings',
        'New England': 'New England Patriots',
        'New Orleans': 'New Orleans Saints',
        'New York G': 'New York Giants',
        'New York J': 'New York Jets',
        'Philadelphia': 'Philadelphia Eagles',
        'Pittsburgh': 'Pittsburgh Steelers',
        'San Francisco': 'San Francisco 49ers',
        'Seattle': 'Seattle Seahawks',
        'Tampa Bay': 'Tampa Bay Buccaneers',
        'Tennessee': 'Tennessee Titans',
        'Washington': 'Washington Commanders'
    }
    
    # Map full names to standardized short names for matching
    FULL_TO_STANDARD = {
        'Arizona Cardinals': 'ARI',
        'Atlanta Falcons': 'ATL',
        'Baltimore Ravens': 'BAL', 
        'Buffalo Bills': 'BUF',
        'Carolina Panthers': 'CAR',
        'Chicago Bears': 'CHI',
        'Cincinnati Bengals': 'CIN',
        'Cleveland Browns': 'CLE',
        'Dallas Cowboys': 'DAL',
        'Denver Broncos': 'DEN',
        'Detroit Lions': 'DET',
        'Green Bay Packers': 'GB',
        'Houston Texans': 'HOU',
        'Indianapolis Colts': 'IND',
        'Jacksonville Jaguars': 'JAX',
        'Kansas City Chiefs': 'KC',
        'Las Vegas Raiders': 'LV',
        'Los Angeles Chargers': 'LAC',
        'Los Angeles Rams': 'LAR',
        'Miami Dolphins': 'MIA',
        'Minnesota Vikings': 'MIN',
        'New England Patriots': 'NE',
        'New Orleans Saints': 'NO', 
        'New York Giants': 'NYG',
        'New York Jets': 'NYJ',
        'Philadelphia Eagles': 'PHI',
        'Pittsburgh Steelers': 'PIT',
        'San Francisco 49ers': 'SF',
        'Seattle Seahawks': 'SEA',
        'Tampa Bay Buccaneers': 'TB',
        'Tennessee Titans': 'TEN',
        'Washington Commanders': 'WAS'
    }
    
    @classmethod
    def standardize_team_name(cls, team_name: str, platform: str = 'unknown') -> str:
        """
        Convert team name to standardized 3-letter code
        
        Args:
            team_name: Raw team name from platform
            platform: Source platform ('kalshi' or 'pinnacle')
            
        Returns:
            Standardized 3-letter team code
        """
        if not team_name:
            return ''
            
        team_name = team_name.strip()
        
        # If it's already a standard code, return it
        if len(team_name) <= 3 and team_name.upper() in cls.FULL_TO_STANDARD.values():
            return team_name.upper()
        
        # For Kalshi short names, convert to full first
        if platform == 'kalshi' or team_name in cls.KALSHI_TO_FULL:
            full_name = cls.KALSHI_TO_FULL.get(team_name, team_name)
            return cls.FULL_TO_STANDARD.get(full_name, team_name.upper()[:3])
        
        # For full team names (Pinnacle format)
        if team_name in cls.FULL_TO_STANDARD:
            return cls.FULL_TO_STANDARD[team_name]
        
        # Fallback: try partial matching
        for full_name, code in cls.FULL_TO_STANDARD.items():
            if team_name.lower() in full_name.lower() or full_name.lower() in team_name.lower():
                return code
        
        # Last resort: use first 3 characters
        return team_name.upper()[:3]
    
    @classmethod
    def teams_match(cls, team1: str, team2: str, platform1: str = 'unknown', platform2: str = 'unknown') -> bool:
        """
        Check if two team names refer to the same team
        
        Args:
            team1: First team name
            team2: Second team name
            platform1: Source platform for team1
            platform2: Source platform for team2
            
        Returns:
            True if teams match
        """
        code1 = cls.standardize_team_name(team1, platform1)
        code2 = cls.standardize_team_name(team2, platform2)
        
        return code1 == code2 and code1 != ''
    
    @classmethod
    def games_match(cls, pinnacle_game: dict, kalshi_game: dict) -> bool:
        """
        Check if games from different platforms match
        
        Args:
            pinnacle_game: Game dict from Pinnacle
            kalshi_game: Game dict from Kalshi
            
        Returns:
            True if games match (same teams, either direction)
        """
        # Get team codes
        p_home = cls.standardize_team_name(pinnacle_game.get('home', ''), 'pinnacle')
        p_away = cls.standardize_team_name(pinnacle_game.get('away', ''), 'pinnacle')
        k_home = cls.standardize_team_name(kalshi_game.get('home', ''), 'kalshi')
        k_away = cls.standardize_team_name(kalshi_game.get('away', ''), 'kalshi')
        
        # Check both arrangements (home/away can be switched)
        match_direct = (p_home == k_home and p_away == k_away)
        match_reversed = (p_home == k_away and p_away == k_home)
        
        return match_direct or match_reversed

def test_mapper():
    """Test the team mapping functionality"""
    print("=== TESTING NFL TEAM MAPPER ===")
    
    # Test standardization
    test_cases = [
        ('Dallas Cowboys', 'pinnacle'),
        ('Dallas', 'kalshi'),
        ('Los Angeles C', 'kalshi'),
        ('Los Angeles Chargers', 'pinnacle'),
        ('New York G', 'kalshi'),
        ('New York Giants', 'pinnacle')
    ]
    
    print("Team Name Standardization:")
    for team, platform in test_cases:
        code = NFLTeamMapper.standardize_team_name(team, platform)
        print(f"  {platform:8} '{team:20}' -> {code}")
    
    # Test matching
    print("\nTeam Matching:")
    match_tests = [
        ('Dallas Cowboys', 'Dallas', 'pinnacle', 'kalshi'),
        ('Los Angeles Chargers', 'Los Angeles C', 'pinnacle', 'kalshi'),
        ('New York Giants', 'New York G', 'pinnacle', 'kalshi'),
        ('Kansas City Chiefs', 'Kansas City', 'pinnacle', 'kalshi')
    ]
    
    for team1, team2, p1, p2 in match_tests:
        matches = NFLTeamMapper.teams_match(team1, team2, p1, p2)
        print(f"  '{team1}' vs '{team2}' -> {matches}")

if __name__ == "__main__":
    test_mapper()