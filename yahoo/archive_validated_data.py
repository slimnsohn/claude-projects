#!/usr/bin/env python3
"""
Archive Validated Standings Data
Create secure backup of user-validated standings data for projection analysis
"""

import json
import csv
import os
import shutil
from datetime import datetime

def create_validated_data_archive():
    """Create secure archive of validated standings data."""
    
    print("=== ARCHIVING VALIDATED STANDINGS DATA ===")
    
    # Create archive directory structure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = f"validated_data_archive"
    
    # Create directory if it doesn't exist
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(f"{archive_dir}/standings", exist_ok=True)
    os.makedirs(f"{archive_dir}/documentation", exist_ok=True)
    
    # Copy validated flat data files
    source_files = [
        'corrected_standings_flat_data.json',
        'corrected_standings_flat_data.csv',
        'sign_off_on_owner_standings.html'
    ]
    
    for file_name in source_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, f"{archive_dir}/standings/")
            print(f"Archived: {file_name}")
    
    # Create validation record
    validation_record = {
        "validation_date": datetime.now().isoformat(),
        "data_validated_by": "User",
        "validation_status": "APPROVED",
        "data_source": "Yahoo Fantasy API raw standings",
        "mapping_correction": {
            "original_mapping": "playoff_seed=playoff_seed, rank=regular_season_rank",
            "corrected_mapping": "playoff_seed=regular_season_standing, rank=playoff_results"
        },
        "coverage": {
            "years": "2010-2024",
            "total_seasons": 15,
            "total_team_records": 158
        },
        "data_quality": "Complete and validated",
        "intended_use": "Draft projection vs actual results analysis",
        "notes": [
            "All regular season standings verified as correct",
            "All playoff results verified as correct", 
            "Data mapping corrected from API response labels",
            "Ready for historical projection analysis"
        ]
    }
    
    # Save validation record
    with open(f"{archive_dir}/documentation/validation_record.json", 'w', encoding='utf-8') as f:
        json.dump(validation_record, f, indent=2)
    
    # Create data dictionary
    data_dictionary = {
        "file_descriptions": {
            "corrected_standings_flat_data.json": "Complete standings data in JSON format",
            "corrected_standings_flat_data.csv": "Complete standings data in CSV format", 
            "sign_off_on_owner_standings.html": "Validation page used for user approval"
        },
        "field_definitions": {
            "year": "Season year (2010-2024)",
            "team_name": "Fantasy team name",
            "regular_season_standing": "Final regular season league position (1=first place)",
            "playoff_result": "Tournament outcome position (1=champion)",
            "wins": "Regular season wins",
            "losses": "Regular season losses", 
            "ties": "Regular season ties",
            "win_percentage": "Regular season win percentage",
            "games_back": "Games behind first place team",
            "team_key": "Yahoo API team identifier"
        },
        "analysis_ready_for": [
            "Draft projection accuracy analysis",
            "Strategy effectiveness measurement",
            "Historical performance correlation",
            "Championship prediction modeling"
        ]
    }
    
    with open(f"{archive_dir}/documentation/data_dictionary.json", 'w', encoding='utf-8') as f:
        json.dump(data_dictionary, f, indent=2)
    
    # Create summary statistics
    with open('corrected_standings_flat_data.json', 'r', encoding='utf-8') as f:
        standings_data = json.load(f)
    
    # Calculate summary stats
    years = sorted(list(set(record['year'] for record in standings_data)))
    teams_by_year = {}
    
    for record in standings_data:
        year = record['year']
        if year not in teams_by_year:
            teams_by_year[year] = []
        teams_by_year[year].append(record['team_name'])
    
    # Find consistent teams
    all_team_names = set()
    for year_teams in teams_by_year.values():
        all_team_names.update(year_teams)
    
    team_participation = {}
    for team in all_team_names:
        years_played = []
        for year, year_teams in teams_by_year.items():
            if team in year_teams:
                years_played.append(year)
        team_participation[team] = {
            "years_played": years_played,
            "seasons_count": len(years_played),
            "first_year": min(years_played) if years_played else None,
            "last_year": max(years_played) if years_played else None
        }
    
    summary_stats = {
        "data_overview": {
            "total_records": len(standings_data),
            "year_range": f"{min(years)}-{max(years)}",
            "seasons_count": len(years),
            "unique_teams": len(all_team_names)
        },
        "team_participation": team_participation,
        "teams_by_year": {str(year): teams for year, teams in teams_by_year.items()},
        "generation_date": datetime.now().isoformat()
    }
    
    with open(f"{archive_dir}/documentation/summary_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, indent=2)
    
    # Create README
    readme_content = f"""# Validated Fantasy Basketball Standings Archive

## Overview
This archive contains user-validated fantasy basketball standings data spanning 15 years (2010-2024).

## Validation Status
✅ **VALIDATED AND APPROVED** on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Data Correction Applied
- **Original API Labels**: `playoff_seed` and `rank` were incorrectly labeled
- **Corrected Mapping**:
  - `playoff_seed` → `regular_season_standing` (final league position)
  - `rank` → `playoff_result` (tournament outcome)

## Files Included
- `standings/corrected_standings_flat_data.json` - Complete data (JSON)
- `standings/corrected_standings_flat_data.csv` - Complete data (CSV) 
- `standings/sign_off_on_owner_standings.html` - Validation page
- `documentation/validation_record.json` - Validation details
- `documentation/data_dictionary.json` - Field definitions
- `documentation/summary_statistics.json` - Data overview

## Intended Use
This validated data enables analysis of:
- Draft projection accuracy vs actual results
- Strategy effectiveness measurement
- Historical performance patterns
- Championship prediction modeling

## Data Quality
- **Coverage**: {len(standings_data)} team records across {len(years)} seasons
- **Completeness**: 100% validated by user
- **Accuracy**: All standings and playoff results confirmed correct
- **Ready for**: Projection vs results correlation analysis

## Important Notes
- Data mapping was corrected from Yahoo API response
- User confirmed all regular season standings are accurate
- User confirmed all playoff results are accurate
- Archive created for secure long-term reference
"""

    with open(f"{archive_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\nVALIDATED DATA ARCHIVE CREATED")
    print(f"Archive Location: {archive_dir}/")
    print(f"Records Archived: {len(standings_data)} team seasons")
    print(f"Coverage: {min(years)}-{max(years)} ({len(years)} seasons)")
    print(f"Unique Teams: {len(all_team_names)}")
    print(f"Validation Status: USER APPROVED")
    
    return archive_dir

def create_analysis_ready_dataset():
    """Create analysis-ready dataset for projection correlation studies."""
    
    print("\n=== PREPARING ANALYSIS DATASET ===")
    
    with open('corrected_standings_flat_data.json', 'r', encoding='utf-8') as f:
        standings_data = json.load(f)
    
    # Create analysis-optimized structure
    analysis_dataset = {
        "metadata": {
            "purpose": "Draft projection vs actual results correlation analysis",
            "validation_status": "USER_APPROVED", 
            "data_source": "Yahoo Fantasy API (corrected mapping)",
            "coverage": "2010-2024 seasons",
            "total_records": len(standings_data),
            "created": datetime.now().isoformat()
        },
        "standings_by_year": {},
        "team_histories": {},
        "championship_data": {}
    }
    
    # Organize by year for easy projection correlation
    for record in standings_data:
        year = str(record['year'])
        if year not in analysis_dataset["standings_by_year"]:
            analysis_dataset["standings_by_year"][year] = []
        analysis_dataset["standings_by_year"][year].append(record)
    
    # Sort each year by regular season standing
    for year in analysis_dataset["standings_by_year"]:
        analysis_dataset["standings_by_year"][year].sort(key=lambda x: x['regular_season_standing'])
    
    # Create team histories for longitudinal analysis
    team_records = {}
    for record in standings_data:
        team = record['team_name']
        if team not in team_records:
            team_records[team] = []
        team_records[team].append(record)
    
    for team, records in team_records.items():
        records.sort(key=lambda x: x['year'])
        analysis_dataset["team_histories"][team] = {
            "seasons_played": len(records),
            "years_active": [r['year'] for r in records],
            "performance_by_year": records,
            "championships": len([r for r in records if r['playoff_result'] == 1]),
            "avg_regular_season_standing": sum(r['regular_season_standing'] for r in records) / len(records),
            "best_regular_season": min(r['regular_season_standing'] for r in records),
            "worst_regular_season": max(r['regular_season_standing'] for r in records)
        }
    
    # Extract championship data for analysis
    for year, year_data in analysis_dataset["standings_by_year"].items():
        champion_data = next((team for team in year_data if team['playoff_result'] == 1), None)
        if champion_data:
            analysis_dataset["championship_data"][year] = {
                "champion": champion_data['team_name'],
                "champion_regular_season_standing": champion_data['regular_season_standing'],
                "champion_record": f"{champion_data['wins']}-{champion_data['losses']}-{champion_data['ties']}",
                "champion_win_pct": champion_data['win_percentage']
            }
    
    # Save analysis dataset
    with open('validated_data_archive/analysis_ready_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_dataset, f, indent=2)
    
    print(f"Analysis dataset created: validated_data_archive/analysis_ready_dataset.json")
    print(f"Ready for projection correlation analysis")
    
    return analysis_dataset

def main():
    """Main execution."""
    
    # Create validated data archive
    archive_dir = create_validated_data_archive()
    
    # Create analysis-ready dataset
    analysis_dataset = create_analysis_ready_dataset()
    
    print(f"\nDATA NOW SECURE FOR PROJECTION ANALYSIS")
    print(f"Next step: Compare draft projections vs these validated results")

if __name__ == "__main__":
    main()