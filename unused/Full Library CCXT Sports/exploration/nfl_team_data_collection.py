"""
NFL Team Data Collection
Comprehensive collection of NFL team data with multiple name variations
"""

import json
from typing import Dict, List, Any
from datetime import datetime

# Complete NFL team data for 2024-2025 season
NFL_TEAMS_2024 = {
    # AFC East
    'BUF': {
        'name': 'Buffalo Bills',
        'city': 'Buffalo',
        'state': 'NY',
        'nickname': 'Bills',
        'abbreviations': ['BUF', 'BUFF'],
        'alternative_names': [
            'Buffalo Bills', 'Bills', 'Buffalo'
        ],
        'conference': 'AFC',
        'division': 'East',
        'colors': ['navy', 'red', 'white'],
        'stadium': 'Highmark Stadium'
    },
    'MIA': {
        'name': 'Miami Dolphins',
        'city': 'Miami',
        'state': 'FL',
        'nickname': 'Dolphins',
        'abbreviations': ['MIA', 'MIAMI'],
        'alternative_names': [
            'Miami Dolphins', 'Dolphins', 'Miami', 'Fins'
        ],
        'conference': 'AFC',
        'division': 'East',
        'colors': ['aqua', 'orange', 'white'],
        'stadium': 'Hard Rock Stadium'
    },
    'NE': {
        'name': 'New England Patriots',
        'city': 'Foxborough',
        'state': 'MA',
        'nickname': 'Patriots',
        'abbreviations': ['NE', 'NWE', 'PAT', 'PATS'],
        'alternative_names': [
            'New England Patriots', 'Patriots', 'New England', 'Pats'
        ],
        'conference': 'AFC',
        'division': 'East',
        'colors': ['navy', 'red', 'silver'],
        'stadium': 'Gillette Stadium'
    },
    'NYJ': {
        'name': 'New York Jets',
        'city': 'East Rutherford',
        'state': 'NJ',
        'nickname': 'Jets',
        'abbreviations': ['NYJ', 'JETS', 'NY'],
        'alternative_names': [
            'New York Jets', 'Jets', 'NY Jets', 'N.Y. Jets'
        ],
        'conference': 'AFC',
        'division': 'East',
        'colors': ['green', 'white'],
        'stadium': 'MetLife Stadium'
    },
    
    # AFC North
    'BAL': {
        'name': 'Baltimore Ravens',
        'city': 'Baltimore',
        'state': 'MD',
        'nickname': 'Ravens',
        'abbreviations': ['BAL', 'BALT'],
        'alternative_names': [
            'Baltimore Ravens', 'Ravens', 'Baltimore'
        ],
        'conference': 'AFC',
        'division': 'North',
        'colors': ['purple', 'black', 'gold'],
        'stadium': 'M&T Bank Stadium'
    },
    'CIN': {
        'name': 'Cincinnati Bengals',
        'city': 'Cincinnati',
        'state': 'OH',
        'nickname': 'Bengals',
        'abbreviations': ['CIN', 'CINC'],
        'alternative_names': [
            'Cincinnati Bengals', 'Bengals', 'Cincinnati'
        ],
        'conference': 'AFC',
        'division': 'North',
        'colors': ['orange', 'black', 'white'],
        'stadium': 'Paycor Stadium'
    },
    'CLE': {
        'name': 'Cleveland Browns',
        'city': 'Cleveland',
        'state': 'OH',
        'nickname': 'Browns',
        'abbreviations': ['CLE', 'CLEV'],
        'alternative_names': [
            'Cleveland Browns', 'Browns', 'Cleveland'
        ],
        'conference': 'AFC',
        'division': 'North',
        'colors': ['brown', 'orange', 'white'],
        'stadium': 'FirstEnergy Stadium'
    },
    'PIT': {
        'name': 'Pittsburgh Steelers',
        'city': 'Pittsburgh',
        'state': 'PA',
        'nickname': 'Steelers',
        'abbreviations': ['PIT', 'PITT'],
        'alternative_names': [
            'Pittsburgh Steelers', 'Steelers', 'Pittsburgh'
        ],
        'conference': 'AFC',
        'division': 'North',
        'colors': ['black', 'gold'],
        'stadium': 'Acrisure Stadium'
    },
    
    # AFC South
    'HOU': {
        'name': 'Houston Texans',
        'city': 'Houston',
        'state': 'TX',
        'nickname': 'Texans',
        'abbreviations': ['HOU', 'HOUS', 'HTX'],
        'alternative_names': [
            'Houston Texans', 'Texans', 'Houston'
        ],
        'conference': 'AFC',
        'division': 'South',
        'colors': ['navy', 'red', 'white'],
        'stadium': 'NRG Stadium'
    },
    'IND': {
        'name': 'Indianapolis Colts',
        'city': 'Indianapolis',
        'state': 'IN',
        'nickname': 'Colts',
        'abbreviations': ['IND', 'INDY'],
        'alternative_names': [
            'Indianapolis Colts', 'Colts', 'Indianapolis', 'Indy'
        ],
        'conference': 'AFC',
        'division': 'South',
        'colors': ['blue', 'white'],
        'stadium': 'Lucas Oil Stadium'
    },
    'JAX': {
        'name': 'Jacksonville Jaguars',
        'city': 'Jacksonville',
        'state': 'FL',
        'nickname': 'Jaguars',
        'abbreviations': ['JAX', 'JAC', 'JAGS'],
        'alternative_names': [
            'Jacksonville Jaguars', 'Jaguars', 'Jacksonville', 'Jags'
        ],
        'conference': 'AFC',
        'division': 'South',
        'colors': ['teal', 'gold', 'black'],
        'stadium': 'TIAA Bank Field'
    },
    'TEN': {
        'name': 'Tennessee Titans',
        'city': 'Nashville',
        'state': 'TN',
        'nickname': 'Titans',
        'abbreviations': ['TEN', 'TENN'],
        'alternative_names': [
            'Tennessee Titans', 'Titans', 'Tennessee'
        ],
        'conference': 'AFC',
        'division': 'South',
        'colors': ['navy', 'red', 'silver'],
        'stadium': 'Nissan Stadium'
    },
    
    # AFC West
    'DEN': {
        'name': 'Denver Broncos',
        'city': 'Denver',
        'state': 'CO',
        'nickname': 'Broncos',
        'abbreviations': ['DEN', 'DENV'],
        'alternative_names': [
            'Denver Broncos', 'Broncos', 'Denver'
        ],
        'conference': 'AFC',
        'division': 'West',
        'colors': ['orange', 'navy', 'white'],
        'stadium': 'Empower Field at Mile High'
    },
    'KC': {
        'name': 'Kansas City Chiefs',
        'city': 'Kansas City',
        'state': 'MO',
        'nickname': 'Chiefs',
        'abbreviations': ['KC', 'KAN', 'CHIEF'],
        'alternative_names': [
            'Kansas City Chiefs', 'Chiefs', 'Kansas City', 'KC Chiefs'
        ],
        'conference': 'AFC',
        'division': 'West',
        'colors': ['red', 'gold', 'white'],
        'stadium': 'Arrowhead Stadium'
    },
    'LV': {
        'name': 'Las Vegas Raiders',
        'city': 'Las Vegas',
        'state': 'NV',
        'nickname': 'Raiders',
        'abbreviations': ['LV', 'LAS', 'RAID', 'OAK'],  # Still sometimes called OAK
        'alternative_names': [
            'Las Vegas Raiders', 'Raiders', 'Las Vegas', 'LV Raiders',
            'Oakland Raiders'  # Historical reference
        ],
        'conference': 'AFC',
        'division': 'West',
        'colors': ['silver', 'black'],
        'stadium': 'Allegiant Stadium'
    },
    'LAC': {
        'name': 'Los Angeles Chargers',
        'city': 'Los Angeles',
        'state': 'CA',
        'nickname': 'Chargers',
        'abbreviations': ['LAC', 'CHAR', 'SD'],  # Still sometimes called SD
        'alternative_names': [
            'Los Angeles Chargers', 'Chargers', 'Los Angeles', 'LA Chargers',
            'San Diego Chargers'  # Historical reference
        ],
        'conference': 'AFC',
        'division': 'West',
        'colors': ['powder blue', 'gold', 'white'],
        'stadium': 'SoFi Stadium'
    },
    
    # NFC East
    'DAL': {
        'name': 'Dallas Cowboys',
        'city': 'Dallas',
        'state': 'TX',
        'nickname': 'Cowboys',
        'abbreviations': ['DAL', 'DALL'],
        'alternative_names': [
            'Dallas Cowboys', 'Cowboys', 'Dallas'
        ],
        'conference': 'NFC',
        'division': 'East',
        'colors': ['navy', 'silver', 'white'],
        'stadium': 'AT&T Stadium'
    },
    'NYG': {
        'name': 'New York Giants',
        'city': 'East Rutherford',
        'state': 'NJ',
        'nickname': 'Giants',
        'abbreviations': ['NYG', 'GIANT', 'NY'],
        'alternative_names': [
            'New York Giants', 'Giants', 'NY Giants', 'N.Y. Giants'
        ],
        'conference': 'NFC',
        'division': 'East',
        'colors': ['blue', 'red', 'white'],
        'stadium': 'MetLife Stadium'
    },
    'PHI': {
        'name': 'Philadelphia Eagles',
        'city': 'Philadelphia',
        'state': 'PA',
        'nickname': 'Eagles',
        'abbreviations': ['PHI', 'PHIL'],
        'alternative_names': [
            'Philadelphia Eagles', 'Eagles', 'Philadelphia', 'Philly'
        ],
        'conference': 'NFC',
        'division': 'East',
        'colors': ['midnight green', 'silver', 'black'],
        'stadium': 'Lincoln Financial Field'
    },
    'WAS': {
        'name': 'Washington Commanders',
        'city': 'Washington',
        'state': 'DC',
        'nickname': 'Commanders',
        'abbreviations': ['WAS', 'WASH', 'WSH'],
        'alternative_names': [
            'Washington Commanders', 'Commanders', 'Washington',
            'Washington Football Team', 'WFT'  # Previous names
        ],
        'conference': 'NFC',
        'division': 'East',
        'colors': ['burgundy', 'gold'],
        'stadium': 'FedExField'
    },
    
    # NFC North
    'CHI': {
        'name': 'Chicago Bears',
        'city': 'Chicago',
        'state': 'IL',
        'nickname': 'Bears',
        'abbreviations': ['CHI', 'CHIC'],
        'alternative_names': [
            'Chicago Bears', 'Bears', 'Chicago'
        ],
        'conference': 'NFC',
        'division': 'North',
        'colors': ['navy', 'orange', 'white'],
        'stadium': 'Soldier Field'
    },
    'DET': {
        'name': 'Detroit Lions',
        'city': 'Detroit',
        'state': 'MI',
        'nickname': 'Lions',
        'abbreviations': ['DET', 'DETR'],
        'alternative_names': [
            'Detroit Lions', 'Lions', 'Detroit'
        ],
        'conference': 'NFC',
        'division': 'North',
        'colors': ['honolulu blue', 'silver', 'white'],
        'stadium': 'Ford Field'
    },
    'GB': {
        'name': 'Green Bay Packers',
        'city': 'Green Bay',
        'state': 'WI',
        'nickname': 'Packers',
        'abbreviations': ['GB', 'GBP', 'PACK'],
        'alternative_names': [
            'Green Bay Packers', 'Packers', 'Green Bay'
        ],
        'conference': 'NFC',
        'division': 'North',
        'colors': ['green', 'gold'],
        'stadium': 'Lambeau Field'
    },
    'MIN': {
        'name': 'Minnesota Vikings',
        'city': 'Minneapolis',
        'state': 'MN',
        'nickname': 'Vikings',
        'abbreviations': ['MIN', 'MINN'],
        'alternative_names': [
            'Minnesota Vikings', 'Vikings', 'Minnesota'
        ],
        'conference': 'NFC',
        'division': 'North',
        'colors': ['purple', 'gold', 'white'],
        'stadium': 'U.S. Bank Stadium'
    },
    
    # NFC South
    'ATL': {
        'name': 'Atlanta Falcons',
        'city': 'Atlanta',
        'state': 'GA',
        'nickname': 'Falcons',
        'abbreviations': ['ATL', 'ATLA'],
        'alternative_names': [
            'Atlanta Falcons', 'Falcons', 'Atlanta'
        ],
        'conference': 'NFC',
        'division': 'South',
        'colors': ['red', 'black', 'silver'],
        'stadium': 'Mercedes-Benz Stadium'
    },
    'CAR': {
        'name': 'Carolina Panthers',
        'city': 'Charlotte',
        'state': 'NC',
        'nickname': 'Panthers',
        'abbreviations': ['CAR', 'CARO'],
        'alternative_names': [
            'Carolina Panthers', 'Panthers', 'Carolina'
        ],
        'conference': 'NFC',
        'division': 'South',
        'colors': ['black', 'panther blue', 'silver'],
        'stadium': 'Bank of America Stadium'
    },
    'NO': {
        'name': 'New Orleans Saints',
        'city': 'New Orleans',
        'state': 'LA',
        'nickname': 'Saints',
        'abbreviations': ['NO', 'NOS', 'NOLA'],
        'alternative_names': [
            'New Orleans Saints', 'Saints', 'New Orleans'
        ],
        'conference': 'NFC',
        'division': 'South',
        'colors': ['black', 'gold'],
        'stadium': 'Caesars Superdome'
    },
    'TB': {
        'name': 'Tampa Bay Buccaneers',
        'city': 'Tampa',
        'state': 'FL',
        'nickname': 'Buccaneers',
        'abbreviations': ['TB', 'TAM', 'BUCS'],
        'alternative_names': [
            'Tampa Bay Buccaneers', 'Buccaneers', 'Tampa Bay', 'Bucs', 'Tampa'
        ],
        'conference': 'NFC',
        'division': 'South',
        'colors': ['red', 'orange', 'black'],
        'stadium': 'Raymond James Stadium'
    },
    
    # NFC West
    'ARI': {
        'name': 'Arizona Cardinals',
        'city': 'Glendale',
        'state': 'AZ',
        'nickname': 'Cardinals',
        'abbreviations': ['ARI', 'ARIZ', 'CARD'],
        'alternative_names': [
            'Arizona Cardinals', 'Cardinals', 'Arizona'
        ],
        'conference': 'NFC',
        'division': 'West',
        'colors': ['red', 'black', 'white'],
        'stadium': 'State Farm Stadium'
    },
    'LAR': {
        'name': 'Los Angeles Rams',
        'city': 'Los Angeles',
        'state': 'CA',
        'nickname': 'Rams',
        'abbreviations': ['LAR', 'RAMS', 'STL'],  # Still sometimes called STL
        'alternative_names': [
            'Los Angeles Rams', 'Rams', 'Los Angeles', 'LA Rams',
            'St. Louis Rams'  # Historical reference
        ],
        'conference': 'NFC',
        'division': 'West',
        'colors': ['ram royal', 'sol', 'bone'],
        'stadium': 'SoFi Stadium'
    },
    'SF': {
        'name': 'San Francisco 49ers',
        'city': 'Santa Clara',
        'state': 'CA',
        'nickname': '49ers',
        'abbreviations': ['SF', 'SFO', '49ER'],
        'alternative_names': [
            'San Francisco 49ers', '49ers', 'San Francisco', 'Niners', 'SF 49ers'
        ],
        'conference': 'NFC',
        'division': 'West',
        'colors': ['red', 'gold'],
        'stadium': "Levi's Stadium"
    },
    'SEA': {
        'name': 'Seattle Seahawks',
        'city': 'Seattle',
        'state': 'WA',
        'nickname': 'Seahawks',
        'abbreviations': ['SEA', 'SEAT'],
        'alternative_names': [
            'Seattle Seahawks', 'Seahawks', 'Seattle', 'Hawks'
        ],
        'conference': 'NFC',
        'division': 'West',
        'colors': ['college navy', 'action green', 'wolf grey'],
        'stadium': 'Lumen Field'
    }
}


def get_all_team_variations() -> Dict[str, List[str]]:
    """Get all possible name variations for each team"""
    variations = {}
    
    for abbrev, team_data in NFL_TEAMS_2024.items():
        all_names = set()
        
        # Add primary abbreviation
        all_names.add(abbrev)
        
        # Add all abbreviations
        all_names.update(team_data['abbreviations'])
        
        # Add all alternative names
        all_names.update(team_data['alternative_names'])
        
        # Add additional variations
        all_names.add(team_data['name'])
        all_names.add(team_data['nickname'])
        all_names.add(team_data['city'])
        all_names.add(f"{team_data['city']} {team_data['nickname']}")
        
        variations[abbrev] = list(all_names)
    
    return variations


def create_reverse_lookup() -> Dict[str, str]:
    """Create reverse lookup from any name variation to standard abbreviation"""
    reverse_lookup = {}
    
    for abbrev, team_data in NFL_TEAMS_2024.items():
        variations = get_all_team_variations()[abbrev]
        
        for variation in variations:
            # Store both original case and uppercase
            reverse_lookup[variation.upper()] = abbrev
            reverse_lookup[variation] = abbrev
    
    return reverse_lookup


def get_team_by_name(search_name: str) -> Dict[str, Any]:
    """Get team data by any name variation"""
    reverse_lookup = create_reverse_lookup()
    
    # Try exact match first
    if search_name in reverse_lookup:
        abbrev = reverse_lookup[search_name]
        return NFL_TEAMS_2024[abbrev]
    
    # Try uppercase match
    if search_name.upper() in reverse_lookup:
        abbrev = reverse_lookup[search_name.upper()]
        return NFL_TEAMS_2024[abbrev]
    
    return None


def validate_team_data():
    """Validate NFL team data completeness and accuracy"""
    print("=== NFL TEAM DATA VALIDATION ===")
    
    # Check we have 32 teams
    assert len(NFL_TEAMS_2024) == 32, f"Expected 32 teams, got {len(NFL_TEAMS_2024)}"
    print(f"OK Found all 32 NFL teams")
    
    # Check conferences and divisions
    afc_teams = [t for t in NFL_TEAMS_2024.values() if t['conference'] == 'AFC']
    nfc_teams = [t for t in NFL_TEAMS_2024.values() if t['conference'] == 'NFC']
    
    assert len(afc_teams) == 16, f"Expected 16 AFC teams, got {len(afc_teams)}"
    assert len(nfc_teams) == 16, f"Expected 16 NFC teams, got {len(nfc_teams)}"
    print(f"OK Conference distribution correct: 16 AFC, 16 NFC")
    
    # Check divisions (4 teams each)
    divisions = {}
    for team in NFL_TEAMS_2024.values():
        div_key = f"{team['conference']} {team['division']}"
        if div_key not in divisions:
            divisions[div_key] = []
        divisions[div_key].append(team['name'])
    
    for div_name, teams in divisions.items():
        assert len(teams) == 4, f"Division {div_name} has {len(teams)} teams, expected 4"
    
    print(f"OK All 8 divisions have 4 teams each")
    
    # Check for required fields
    required_fields = ['name', 'city', 'state', 'nickname', 'abbreviations', 
                      'alternative_names', 'conference', 'division', 'stadium']
    
    for abbrev, team_data in NFL_TEAMS_2024.items():
        for field in required_fields:
            assert field in team_data, f"Team {abbrev} missing field: {field}"
    
    print(f"OK All teams have required data fields")
    
    # Test reverse lookup
    reverse_lookup = create_reverse_lookup()
    print(f"OK Created reverse lookup with {len(reverse_lookup)} name variations")
    
    # Test some common lookups
    test_cases = [
        ('KC', 'KC'),
        ('Kansas City Chiefs', 'KC'),
        ('Chiefs', 'KC'),
        ('Patriots', 'NE'),
        ('Cowboys', 'DAL'),
        ('49ers', 'SF'),
        ('Las Vegas Raiders', 'LV'),
        ('Washington Commanders', 'WAS')
    ]
    
    for search_name, expected_abbrev in test_cases:
        team = get_team_by_name(search_name)
        assert team is not None, f"Could not find team for: {search_name}"
        found_abbrev = None
        for abbrev, data in NFL_TEAMS_2024.items():
            if data == team:
                found_abbrev = abbrev
                break
        assert found_abbrev == expected_abbrev, f"Expected {expected_abbrev}, got {found_abbrev} for {search_name}"
    
    print(f"OK Team lookup tests passed")
    print("NFL team data validation successful!")


def export_team_data():
    """Export team data to JSON for use in other modules"""
    output_data = {
        'teams': NFL_TEAMS_2024,
        'reverse_lookup': create_reverse_lookup(),
        'variations': get_all_team_variations(),
        'generated_at': datetime.now().isoformat(),
        'season': '2024-2025'
    }
    
    output_file = 'nfl_teams_2024.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Team data exported to {output_file}")
    return output_file


if __name__ == "__main__":
    # Validate all team data
    validate_team_data()
    
    # Export for use in other modules
    export_file = export_team_data()
    
    # Show some statistics
    print(f"\n=== NFL TEAM DATA STATISTICS ===")
    print(f"Total teams: {len(NFL_TEAMS_2024)}")
    print(f"Total name variations: {sum(len(v) for v in get_all_team_variations().values())}")
    print(f"Average variations per team: {sum(len(v) for v in get_all_team_variations().values()) / len(NFL_TEAMS_2024):.1f}")
    
    # Show some examples
    print(f"\n=== EXAMPLE TEAM LOOKUPS ===")
    examples = ['KC', 'Kansas City', 'Chiefs', 'New England Patriots', 'Cowboys', '49ers']
    for example in examples:
        team = get_team_by_name(example)
        if team:
            print(f"'{example}' -> {team['name']} ({team['conference']} {team['division']})")
        else:
            print(f"'{example}' -> NOT FOUND")