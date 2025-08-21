"""
Yahoo Fantasy League Data Structure Design
==========================================

This module defines the comprehensive data structure for 15-year fantasy analysis.
Supports three types of analysis:
1. Player-level analysis (under/over valued players)
2. Owner analysis (historical draft patterns)  
3. Draft strategy analysis (what leads to success)
"""

import os
import json
from pathlib import Path

# League configuration
LEAGUE_KEYS = {
    '2010': '249.l.40919',
    '2011': '265.l.40720', 
    '2012': '304.l.62665',
    '2013': '322.l.90972',
    '2014': '342.l.129190',
    '2015': '353.l.93240',
    '2016': '364.l.90263',
    '2017': '375.l.111279',
    '2018': '385.l.42210',
    '2019': '395.l.98368',
    '2020': '402.l.121244',
    '2021': '410.l.124782',
    '2022': '418.l.104779',
    '2023': '428.l.32747',
    '2024': '454.l.44006'
}

# The 9 stat categories our league uses + games played
STAT_CATEGORIES = {
    'games_played': {'name': 'Games Played', 'type': 'counting', 'higher_better': True},
    'fg_pct': {'name': 'Field Goal %', 'type': 'percentage', 'higher_better': True},
    'ft_pct': {'name': 'Free Throw %', 'type': 'percentage', 'higher_better': True},
    'threes_made': {'name': '3-Pointers Made', 'type': 'average', 'higher_better': True},
    'points': {'name': 'Points', 'type': 'average', 'higher_better': True},
    'rebounds': {'name': 'Rebounds', 'type': 'average', 'higher_better': True},
    'assists': {'name': 'Assists', 'type': 'average', 'higher_better': True},
    'steals': {'name': 'Steals', 'type': 'average', 'higher_better': True},
    'blocks': {'name': 'Blocks', 'type': 'average', 'higher_better': True},
    'turnovers': {'name': 'Turnovers', 'type': 'average', 'higher_better': False}
}

def create_directory_structure(base_path="C:/Users/sammy/Desktop/development/git/claude-projects/yahoo"):
    """Create the complete directory structure for the analysis"""
    
    base = Path(base_path)
    
    # Main data directory
    league_data = base / "league_data"
    league_data.mkdir(exist_ok=True)
    
    # Master data directory
    master_data = league_data / "master_data"
    master_data.mkdir(exist_ok=True)
    
    # HTML reports directory (separate from data)
    html_reports = base / "html_reports"
    html_reports.mkdir(exist_ok=True)
    
    # Create year directories
    for year in LEAGUE_KEYS.keys():
        year_dir = league_data / year
        year_dir.mkdir(exist_ok=True)
        
        # Subdirectories for each year
        (year_dir / "raw_data").mkdir(exist_ok=True)
        (year_dir / "processed_data").mkdir(exist_ok=True)
        (year_dir / "external_data").mkdir(exist_ok=True)
    
    # HTML report subdirectories
    (html_reports / "assets").mkdir(exist_ok=True)
    (html_reports / "years").mkdir(exist_ok=True)
    (html_reports / "owners").mkdir(exist_ok=True)
    (html_reports / "players").mkdir(exist_ok=True)
    (html_reports / "strategies").mkdir(exist_ok=True)
    
    return {
        'league_data': league_data,
        'master_data': master_data,
        'html_reports': html_reports
    }

def create_master_data_templates(master_data_path):
    """Create template files for master data"""
    
    # League keys master file
    league_keys_file = master_data_path / "league_keys.json"
    with open(league_keys_file, 'w') as f:
        json.dump({
            'description': 'Yahoo Fantasy League Keys for 15-year analysis',
            'total_seasons': len(LEAGUE_KEYS),
            'date_range': '2010-2024',
            'league_keys': LEAGUE_KEYS
        }, f, indent=2)
    
    # Stat categories master file
    stat_categories_file = master_data_path / "stat_categories.json"
    with open(stat_categories_file, 'w') as f:
        json.dump({
            'description': 'Fantasy league statistical categories',
            'total_categories': len(STAT_CATEGORIES),
            'categories': STAT_CATEGORIES
        }, f, indent=2)
    
    # Owners master template
    owners_master_file = master_data_path / "owners_master.json"
    owners_template = {
        'description': 'Master owner tracking across all 15 seasons',
        'last_updated': None,
        'total_unique_owners': 0,
        'current_participants': [],
        'owners': {
            # Will be populated as: 
            # "owner_id": {
            #     "name": "Owner Name",
            #     "team_names_by_year": {"2010": "Team Name"},
            #     "participation_years": ["2010", "2011"],
            #     "is_current_participant": True,
            #     "total_seasons": 2,
            #     "draft_tendencies": {}
            # }
        }
    }
    with open(owners_master_file, 'w') as f:
        json.dump(owners_template, f, indent=2)
    
    # Players master template  
    players_master_file = master_data_path / "players_master.json"
    players_template = {
        'description': 'Master player database with cross-year tracking',
        'last_updated': None,
        'total_unique_players': 0,
        'players': {
            # Will be populated as:
            # "player_id": {
            #     "name": "Player Name",
            #     "alternative_names": ["Alt Name 1"],
            #     "nba_teams_by_year": {"2010": "LAL"},
            #     "positions": ["PG", "SG"],
            #     "years_drafted": ["2010", "2011"],
            #     "career_fantasy_value": {}
            # }
        }
    }
    with open(players_master_file, 'w') as f:
        json.dump(players_template, f, indent=2)

def create_year_data_templates(year_path, year):
    """Create template files for a specific year"""
    
    # Raw data templates
    raw_data = year_path / "raw_data"
    
    # Processed data templates
    processed_data = year_path / "processed_data"
    
    # Draft analysis template
    draft_analysis_template = {
        'season': year,
        'league_key': LEAGUE_KEYS.get(year),
        'total_picks': None,
        'total_budget': None,
        'average_pick_cost': None,
        'picks': [
            # {
            #     "pick_number": 1,
            #     "round": 1,
            #     "player_name": "Player Name",
            #     "player_id": "unique_id",
            #     "position": "PG",
            #     "real_team": "LAL", 
            #     "fantasy_team": "Team Name",
            #     "owner_id": "owner_unique_id",
            #     "draft_cost": 65,
            #     "percent_of_budget": 32.5,
            #     "positional_rank_drafted": 1,
            #     "actual_season_stats": {},
            #     "value_metrics": {}
            # }
        ],
        'draft_summary': {
            'most_expensive_pick': None,
            'biggest_bargain': None,
            'biggest_bust': None,
            'position_spending': {}
        }
    }
    
    with open(processed_data / "draft_analysis.json", 'w') as f:
        json.dump(draft_analysis_template, f, indent=2)
    
    # Owners template for this year
    owners_year_template = {
        'season': year,
        'total_owners': None,
        'owners': {
            # "owner_id": {
            #     "name": "Owner Name",
            #     "team_name": "Fantasy Team Name",
            #     "draft_budget_used": 200,
            #     "total_picks": 15,
            #     "draft_strategy": "stars_and_scrubs",
            #     "season_record": {"wins": 10, "losses": 8},
            #     "playoff_result": "champion",
            #     "most_expensive_player": "Player Name",
            #     "best_value_pick": "Player Name"
            # }
        }
    }
    
    with open(processed_data / "owners.json", 'w') as f:
        json.dump(owners_year_template, f, indent=2)
    
    # Season summary template
    season_summary_template = {
        'season': year,
        'league_champion': None,
        'total_draft_spending': None,
        'most_valuable_position': None,
        'biggest_draft_trends': [],
        'key_insights': []
    }
    
    with open(processed_data / "season_summary.json", 'w') as f:
        json.dump(season_summary_template, f, indent=2)

def main():
    """Set up the complete data structure"""
    print("Creating Yahoo Fantasy League Data Structure...")
    print("=" * 50)
    
    # Create directory structure
    paths = create_directory_structure()
    print(f"Created base directories:")
    print(f"  - League Data: {paths['league_data']}")
    print(f"  - Master Data: {paths['master_data']}")
    print(f"  - HTML Reports: {paths['html_reports']}")
    
    # Create master data templates
    create_master_data_templates(paths['master_data'])
    print(f"\nCreated master data templates:")
    print(f"  - league_keys.json")
    print(f"  - stat_categories.json")
    print(f"  - owners_master.json")
    print(f"  - players_master.json")
    
    # Create year-specific templates
    print(f"\nCreating templates for {len(LEAGUE_KEYS)} years:")
    for year in LEAGUE_KEYS.keys():
        year_path = paths['league_data'] / year
        create_year_data_templates(year_path, year)
        print(f"  - {year} templates created")
    
    print(f"\n" + "=" * 50)
    print("Data structure setup complete!")
    print(f"\nNext steps:")
    print(f"1. Extract raw data from Yahoo API for all 15 years")
    print(f"2. Get external NBA stats for player performance")
    print(f"3. Process and analyze the data")
    print(f"4. Generate HTML reports")
    print(f"\nDirectory structure ready for analysis!")

if __name__ == "__main__":
    main()