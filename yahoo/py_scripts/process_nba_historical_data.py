import pandas as pd
import json
import os
from collections import defaultdict

def process_nba_historical_data():
    """
    Process NBA historical data and organize it by season.
    Creates season-wide aggregated stats for each player.
    """
    
    print("=== NBA HISTORICAL DATA PROCESSING ===\n")
    
    base_path = "historical_nba_stats/raw_downloads/NBA-Data-2010-2024"
    
    # Load all box score files
    box_score_files = [
        "regular_season_box_scores_2010_2024_part_1.csv",
        "regular_season_box_scores_2010_2024_part_2.csv", 
        "regular_season_box_scores_2010_2024_part_3.csv"
    ]
    
    print("Loading NBA box score data...")
    all_games = []
    
    for file in box_score_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            print(f"Loading {file}...")
            df = pd.read_csv(file_path)
            all_games.append(df)
            print(f"  Loaded {len(df):,} game records")
    
    # Combine all box scores
    combined_df = pd.concat(all_games, ignore_index=True)
    print(f"\nTotal combined records: {len(combined_df):,}")
    
    # Clean data - remove DNP entries and null minutes
    print("Cleaning data...")
    original_count = len(combined_df)
    
    # Convert minutes to numeric, coercing errors to NaN
    combined_df['minutes_numeric'] = pd.to_numeric(combined_df['minutes'].astype(str).str.replace(':', '.').str.replace('DNP.*', '', regex=True), errors='coerce')
    
    # Remove rows where player didn't play (no minutes or DNP)
    combined_df = combined_df[
        (combined_df['minutes_numeric'] > 0) & 
        (~combined_df['comment'].str.contains('DNP', na=False)) &
        (combined_df['personName'].notna())
    ].copy()
    
    cleaned_count = len(combined_df)
    print(f"  Removed {original_count - cleaned_count:,} non-playing records")
    print(f"  Remaining records: {cleaned_count:,}")
    
    # Define stat columns for aggregation
    stat_columns = [
        'minutes', 'fieldGoalsMade', 'fieldGoalsAttempted', 
        'threePointersMade', 'threePointersAttempted',
        'freeThrowsMade', 'freeThrowsAttempted',
        'reboundsOffensive', 'reboundsDefensive', 'reboundsTotal',
        'assists', 'steals', 'blocks', 'turnovers', 'points'
    ]
    
    # Convert stat columns to numeric
    for col in stat_columns:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)
    
    print("\nAggregating stats by player by season...")
    
    # Group by season and player, aggregate stats
    season_stats = combined_df.groupby(['season_year', 'personId', 'personName']).agg({
        # Count games played
        'gameId': 'count',
        
        # Sum counting stats
        'minutes': 'sum',
        'fieldGoalsMade': 'sum',
        'fieldGoalsAttempted': 'sum',
        'threePointersMade': 'sum',
        'threePointersAttempted': 'sum',
        'freeThrowsMade': 'sum',
        'freeThrowsAttempted': 'sum',
        'reboundsOffensive': 'sum',
        'reboundsDefensive': 'sum', 
        'reboundsTotal': 'sum',
        'assists': 'sum',
        'steals': 'sum',
        'blocks': 'sum',
        'turnovers': 'sum',
        'points': 'sum',
        
        # Keep player info
        'position': 'first',
        'teamTricode': lambda x: ', '.join(x.unique())  # Handle trades
    }).reset_index()
    
    # Rename gameId count to games_played
    season_stats.rename(columns={'gameId': 'games_played'}, inplace=True)
    
    # Calculate per-game averages and percentages
    season_stats['minutes_per_game'] = season_stats['minutes'] / season_stats['games_played']
    season_stats['points_per_game'] = season_stats['points'] / season_stats['games_played']
    season_stats['rebounds_per_game'] = season_stats['reboundsTotal'] / season_stats['games_played']
    season_stats['assists_per_game'] = season_stats['assists'] / season_stats['games_played']
    season_stats['steals_per_game'] = season_stats['steals'] / season_stats['games_played']
    season_stats['blocks_per_game'] = season_stats['blocks'] / season_stats['games_played']
    season_stats['turnovers_per_game'] = season_stats['turnovers'] / season_stats['games_played']
    season_stats['threepointers_per_game'] = season_stats['threePointersMade'] / season_stats['games_played']
    
    # Calculate shooting percentages
    season_stats['field_goal_percentage'] = (season_stats['fieldGoalsMade'] / season_stats['fieldGoalsAttempted']).fillna(0)
    season_stats['three_point_percentage'] = (season_stats['threePointersMade'] / season_stats['threePointersAttempted']).fillna(0) 
    season_stats['free_throw_percentage'] = (season_stats['freeThrowsMade'] / season_stats['freeThrowsAttempted']).fillna(0)
    
    print(f"Aggregated stats for {len(season_stats):,} player seasons")
    
    # Create player mapping file
    print("\nCreating player mapping file...")
    player_mapping = season_stats[['personId', 'personName']].drop_duplicates().sort_values('personName')
    
    mapping_file = "historical_nba_stats/player_mappings/nba_player_mapping.json"
    os.makedirs(os.path.dirname(mapping_file), exist_ok=True)
    
    player_dict = {}
    for _, row in player_mapping.iterrows():
        player_dict[str(row['personId'])] = {
            'name': row['personName'],
            'nba_id': int(row['personId'])
        }
    
    with open(mapping_file, 'w') as f:
        json.dump(player_dict, f, indent=2)
    
    print(f"Created mapping for {len(player_dict)} unique players")
    
    # Organize data by season year
    print("\nOrganizing data by season...")
    
    unique_seasons = sorted(season_stats['season_year'].unique())
    
    for season in unique_seasons:
        # Convert season format (2010-11 -> 2011 to match league years)
        league_year = int(season.split('-')[1]) + 2000
        
        if league_year < 2010 or league_year > 2024:
            continue
            
        season_data = season_stats[season_stats['season_year'] == season].copy()
        
        print(f"Processing {season} (league year {league_year}): {len(season_data)} players")
        
        # Create year folder
        year_folder = f"historical_nba_stats/{league_year}"
        os.makedirs(year_folder, exist_ok=True)
        
        # Save comprehensive season data
        output_file = f"{year_folder}/nba_season_stats.csv"
        season_data.to_csv(output_file, index=False)
        
        # Create summary stats in fantasy-relevant format
        fantasy_stats = season_data[[
            'personId', 'personName', 'games_played', 'teamTricode',
            'field_goal_percentage', 'free_throw_percentage', 'threepointers_per_game',
            'points_per_game', 'rebounds_per_game', 'assists_per_game', 
            'steals_per_game', 'blocks_per_game', 'turnovers_per_game'
        ]].copy()
        
        # Round to reasonable decimal places
        for col in ['field_goal_percentage', 'free_throw_percentage', 'threepointers_per_game',
                   'points_per_game', 'rebounds_per_game', 'assists_per_game',
                   'steals_per_game', 'blocks_per_game', 'turnovers_per_game']:
            fantasy_stats[col] = fantasy_stats[col].round(3)
        
        fantasy_file = f"{year_folder}/fantasy_relevant_stats.csv" 
        fantasy_stats.to_csv(fantasy_file, index=False)
        
        # Create JSON summary for year
        year_summary = {
            "season": season,
            "league_year": league_year,
            "total_players": len(season_data),
            "players_with_10_plus_games": len(season_data[season_data['games_played'] >= 10]),
            "data_files": {
                "comprehensive": "nba_season_stats.csv",
                "fantasy_focused": "fantasy_relevant_stats.csv"
            },
            "stat_categories": {
                "percentages": ["field_goal_percentage", "free_throw_percentage"],
                "per_game_averages": ["threepointers_per_game", "points_per_game", "rebounds_per_game", 
                                    "assists_per_game", "steals_per_game", "blocks_per_game", "turnovers_per_game"],
                "counting_stat": ["games_played"]
            }
        }
        
        with open(f"{year_folder}/year_summary.json", 'w') as f:
            json.dump(year_summary, f, indent=2)
    
    print(f"\n=== PROCESSING COMPLETE ===")
    print(f"Organized data for seasons: {', '.join(map(str, range(2010, 2025)))}")
    print(f"Player mapping file created: {mapping_file}")
    print(f"Total unique players: {len(player_dict)}")

if __name__ == "__main__":
    process_nba_historical_data()