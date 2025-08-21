#!/usr/bin/env python3
"""
Simple fix for draft player names using existing web data.
"""

import json
import os

def get_player_names_from_web_data():
    """Extract player names from existing web data."""
    
    player_names = {}
    
    # Load web data
    web_file = 'html_reports/data/players.json'
    if os.path.exists(web_file):
        with open(web_file, 'r', encoding='utf-8') as f:
            web_data = json.load(f)
        
        players = web_data.get('players', {})
        print(f"Found web data with {len(players)} players")
        
        for player_id, player_data in players.items():
            player_name = player_data.get('player_name', f'Player {player_id}')
            
            # Also check if this player has draft history to get Yahoo IDs
            if 'yahoo_draft_history' in player_data:
                for draft_entry in player_data['yahoo_draft_history']:
                    yahoo_id = str(draft_entry.get('yahoo_id', ''))
                    if yahoo_id:
                        player_names[yahoo_id] = player_name
            
            # Use NBA player ID as well
            player_names[player_id] = player_name
    
    print(f"Extracted {len(player_names)} player name mappings")
    return player_names

def fix_draft_files_with_names():
    """Add player names to draft files."""
    
    print("=== FIXING DRAFT FILES WITH PLAYER NAMES ===\\n")
    
    # Get player names
    player_names = get_player_names_from_web_data()
    
    fixed_years = []
    
    for year in range(2010, 2025):
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            print(f"Processing {year}...")
            
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                
                picks_updated = 0
                total_picks = len(draft_data.get('picks', []))
                
                for pick in draft_data.get('picks', []):
                    player_id = str(pick['player_id'])
                    
                    # Try to find player name
                    if player_id in player_names:
                        pick['player_name'] = player_names[player_id]
                        picks_updated += 1
                    else:
                        # Fallback name
                        pick['player_name'] = f"Player {player_id}"
                
                # Save updated data
                with open(draft_file, 'w', encoding='utf-8') as f:
                    json.dump(draft_data, f, indent=2, ensure_ascii=False)
                
                print(f"  Updated {picks_updated}/{total_picks} player names")
                fixed_years.append(year)
                
            except Exception as e:
                print(f"  Error processing {year}: {e}")
    
    print(f"\\nFixed draft data for {len(fixed_years)} years")

def debug_player_database_loading():
    """Debug why the player database isn't loading."""
    
    print("\\n=== DEBUGGING PLAYER DATABASE LOADING ===\\n")
    
    # Check data files
    files = [
        ('html_reports/data/players.json', 'players'),
        ('html_reports/data/insights.json', 'insights'), 
        ('html_reports/data/metadata.json', 'metadata'),
        ('html_reports/data/player_index.json', 'player_index')
    ]
    
    all_good = True
    
    for file_path, data_type in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if data_type == 'players':
                    if 'players' in data:
                        players = data['players']
                        print(f"✅ {file_path}: {len(players)} players")
                        
                        # Check first player
                        if players:
                            first_id = list(players.keys())[0]
                            first_player = players[first_id]
                            print(f"   Sample: {first_player.get('player_name', 'NO NAME')}")
                    else:
                        print(f"❌ {file_path}: Missing 'players' key!")
                        print(f"   Keys found: {list(data.keys())}")
                        all_good = False
                        
                elif data_type == 'insights':
                    print(f"✅ {file_path}: {list(data.keys())}")
                    
                elif data_type == 'metadata':
                    print(f"✅ {file_path}: {data.get('total_players', 'unknown')} total players")
                    
                elif data_type == 'player_index':
                    print(f"✅ {file_path}: {len(data)} index entries")
                    
            except Exception as e:
                print(f"❌ {file_path}: Error loading - {e}")
                all_good = False
        else:
            print(f"❌ {file_path}: File not found")
            all_good = False
    
    # Check the standalone HTML structure
    standalone_file = 'html_reports/standalone.html'
    if os.path.exists(standalone_file):
        print(f"\\n✅ {standalone_file} exists")
        
        # Check if the data embedding looks correct
        with open(standalone_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'window.EMBEDDED_DATA' in content:
            print("✅ EMBEDDED_DATA found in HTML")
            
            # Look for the data structure
            if '"players":{"' in content:
                print("✅ Players data structure found")
            else:
                print("❌ Players data structure not found")
                
            if 'this.players = window.EMBEDDED_DATA.players;' in content:
                print("✅ Correct JavaScript data access")
            else:
                print("❌ JavaScript data access may be wrong")
                
        else:
            print("❌ EMBEDDED_DATA not found in HTML")
    
    return all_good

def main():
    """Fix both issues."""
    
    # First debug the database
    db_ok = debug_player_database_loading()
    
    # Fix draft names
    fix_draft_files_with_names()
    
    # If database had issues, try regenerating
    if not db_ok:
        print("\\n=== REGENERATING WEB DATA ===")
        try:
            import generate_complete_web_data
            generate_complete_web_data.generate_complete_web_data()
            print("✅ Web data regenerated")
        except Exception as e:
            print(f"❌ Error regenerating web data: {e}")

if __name__ == "__main__":
    main()