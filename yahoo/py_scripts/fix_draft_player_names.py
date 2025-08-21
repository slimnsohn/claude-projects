#!/usr/bin/env python3
"""
Fix draft data by adding player names and debug player database loading.
"""

import json
import os

def load_player_mapping():
    """Load comprehensive player mapping to get names for player IDs."""
    
    # Load NBA player mapping
    nba_mapping = {}
    nba_file = 'historical_nba_stats/player_mappings/nba_player_mapping.json'
    if os.path.exists(nba_file):
        with open(nba_file, 'r') as f:
            nba_data = json.load(f)
            for player_id, player_info in nba_data.items():
                nba_mapping[player_id] = player_info['name']
    
    # Load Yahoo-NBA mapping
    yahoo_mapping = {}
    yahoo_file = 'historical_nba_stats/player_mappings/yahoo_nba_mapping.json'
    if os.path.exists(yahoo_file):
        with open(yahoo_file, 'r') as f:
            yahoo_data = json.load(f)
            for yahoo_id, mapping_info in yahoo_data.items():
                nba_id = mapping_info['nba_id']
                if nba_id in nba_mapping:
                    yahoo_mapping[yahoo_id] = nba_mapping[nba_id]
    
    # Load comprehensive mapping
    comprehensive_file = 'historical_nba_stats/player_mappings/comprehensive_mapping.json'
    if os.path.exists(comprehensive_file):
        with open(comprehensive_file, 'r') as f:
            comp_data = json.load(f)
            for yahoo_id, mapping_info in comp_data.get('mapped_players', {}).items():
                nba_id = mapping_info['nba_id']
                if nba_id in nba_mapping:
                    yahoo_mapping[yahoo_id] = nba_mapping[nba_id]
    
    print(f"Loaded names for {len(yahoo_mapping)} Yahoo players")
    return yahoo_mapping, nba_mapping

def fix_draft_data_with_names():
    """Add player names to all draft data files."""
    
    print("=== FIXING DRAFT DATA WITH PLAYER NAMES ===\\n")
    
    # Load player mappings
    yahoo_mapping, nba_mapping = load_player_mapping()
    
    fixed_years = []
    
    for year in range(2010, 2025):
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            print(f"Processing {year}...")
            
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                
                picks_updated = 0
                
                for pick in draft_data.get('picks', []):
                    player_id = str(pick['player_id'])
                    player_name = None
                    
                    # Try to find player name in mappings
                    if player_id in yahoo_mapping:
                        player_name = yahoo_mapping[player_id]
                    elif player_id in nba_mapping:
                        player_name = nba_mapping[player_id]
                    
                    if player_name:
                        pick['player_name'] = player_name
                        picks_updated += 1
                    else:
                        pick['player_name'] = f"Player {player_id}"
                
                # Save updated data
                with open(draft_file, 'w', encoding='utf-8') as f:
                    json.dump(draft_data, f, indent=2, ensure_ascii=False)
                
                print(f"  Updated {picks_updated}/{len(draft_data.get('picks', []))} player names")
                fixed_years.append(year)
                
            except Exception as e:
                print(f"  Error processing {year}: {e}")
    
    print(f"\\nFixed draft data for {len(fixed_years)} years: {fixed_years}")

def debug_player_database():
    """Debug the player database loading issue."""
    
    print("\\n=== DEBUGGING PLAYER DATABASE ===\\n")
    
    # Check if web data files exist and are valid
    files_to_check = [
        'html_reports/data/players.json',
        'html_reports/data/insights.json', 
        'html_reports/data/metadata.json',
        'html_reports/data/player_index.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'players.json' in file_path:
                    print(f"✅ {file_path}: {len(data.get('players', {}))} players")
                    
                    # Check structure
                    if 'players' in data:
                        first_player_id = list(data['players'].keys())[0]
                        first_player = data['players'][first_player_id]
                        print(f"   Sample player structure: {list(first_player.keys())}")
                        print(f"   Sample player name: {first_player.get('player_name', 'NO NAME')}")
                    else:
                        print(f"   ❌ No 'players' key in data structure!")
                        print(f"   Data keys: {list(data.keys())}")
                        
                elif 'insights.json' in file_path:
                    print(f"✅ {file_path}: {len(data)} insight categories")
                elif 'metadata.json' in file_path:
                    print(f"✅ {file_path}: {list(data.keys())}")
                elif 'player_index.json' in file_path:
                    print(f"✅ {file_path}: {len(data)} index entries")
                    
            except json.JSONDecodeError as e:
                print(f"❌ {file_path}: JSON decode error - {e}")
            except Exception as e:
                print(f"❌ {file_path}: Error - {e}")
        else:
            print(f"❌ {file_path}: File not found")
    
    # Check if data structure is correct for embedding
    players_file = 'html_reports/data/players.json'
    if os.path.exists(players_file):
        with open(players_file, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
            
        print(f"\\nPlayers data structure analysis:")
        print(f"  Top level keys: {list(players_data.keys())}")
        
        if 'players' in players_data:
            players = players_data['players']
            print(f"  Number of players: {len(players)}")
            
            # Check a few sample players
            sample_ids = list(players.keys())[:3]
            for player_id in sample_ids:
                player = players[player_id]
                print(f"  Player {player_id}: name='{player.get('player_name', 'NO NAME')}', seasons={len(player.get('seasons', {}))}")

def regenerate_web_data():
    """Regenerate web data to make sure it's current."""
    
    print("\\n=== REGENERATING WEB DATA ===\\n")
    
    try:
        # Import and run the web data generation
        import generate_complete_web_data
        generate_complete_web_data.generate_complete_web_data()
        print("✅ Web data regenerated successfully")
        
    except Exception as e:
        print(f"❌ Error regenerating web data: {e}")

def main():
    """Main function to fix all issues."""
    
    # Fix draft data with player names
    fix_draft_data_with_names()
    
    # Debug player database
    debug_player_database()
    
    # Regenerate web data
    regenerate_web_data()
    
    # Debug again after regeneration
    debug_player_database()

if __name__ == "__main__":
    main()