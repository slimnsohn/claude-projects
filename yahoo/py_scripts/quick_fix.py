#!/usr/bin/env python3
"""
Quick fix for both issues.
"""

import json
import os

def check_player_database():
    """Check player database files."""
    
    print("DEBUGGING PLAYER DATABASE:")
    
    players_file = 'html_reports/data/players.json'
    if os.path.exists(players_file):
        with open(players_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  players.json exists")
        print(f"  Top level keys: {list(data.keys())}")
        
        if 'players' in data:
            players = data['players']
            print(f"  Number of players: {len(players)}")
            
            # Sample player
            first_id = list(players.keys())[0]
            first_player = players[first_id]
            print(f"  Sample player name: {first_player.get('player_name', 'NO NAME')}")
            return True
        else:
            print(f"  ERROR: No 'players' key found!")
            return False
    else:
        print(f"  ERROR: players.json not found")
        return False

def fix_draft_names():
    """Add player names to draft data."""
    
    print("\\nFIXING DRAFT NAMES:")
    
    # Load player names from web data
    player_names = {}
    web_file = 'html_reports/data/players.json'
    
    if os.path.exists(web_file):
        with open(web_file, 'r', encoding='utf-8') as f:
            web_data = json.load(f)
        
        players = web_data.get('players', {})
        
        for player_id, player_data in players.items():
            player_name = player_data.get('player_name', f'Player {player_id}')
            player_names[player_id] = player_name
            
            # Also map Yahoo IDs
            if 'yahoo_draft_history' in player_data:
                for draft_entry in player_data['yahoo_draft_history']:
                    yahoo_id = str(draft_entry.get('yahoo_id', ''))
                    if yahoo_id:
                        player_names[yahoo_id] = player_name
        
        print(f"  Loaded {len(player_names)} player names")
    
    # Fix draft files
    fixed_count = 0
    
    for year in [2024, 2023, 2022]:  # Test with recent years first
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            with open(draft_file, 'r', encoding='utf-8') as f:
                draft_data = json.load(f)
            
            updated = 0
            for pick in draft_data.get('picks', []):
                player_id = str(pick['player_id'])
                if player_id in player_names:
                    pick['player_name'] = player_names[player_id]
                    updated += 1
                else:
                    pick['player_name'] = f"Player {player_id}"
            
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, indent=2, ensure_ascii=False)
            
            print(f"  {year}: Updated {updated}/{len(draft_data.get('picks', []))} names")
            fixed_count += 1
    
    return fixed_count

def regenerate_files():
    """Regenerate HTML files."""
    
    print("\\nREGENERATING FILES:")
    
    try:
        # Regenerate web data
        import generate_complete_web_data
        generate_complete_web_data.generate_complete_web_data()
        print("  Web data regenerated")
        
        # Regenerate standalone HTML
        import create_standalone_html
        create_standalone_html.create_standalone_html()
        print("  Standalone HTML regenerated")
        
        # Regenerate draft results
        import create_draft_results_page
        create_draft_results_page.create_draft_results_page()
        print("  Draft results page regenerated")
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """Main fix function."""
    
    print("=== QUICK FIX FOR BOTH ISSUES ===\\n")
    
    # Check current state
    db_ok = check_player_database()
    
    # Fix draft names
    draft_fixed = fix_draft_names()
    
    # Regenerate everything
    regen_ok = regenerate_files()
    
    print("\\n=== SUMMARY ===")
    print(f"Database OK: {db_ok}")
    print(f"Draft files fixed: {draft_fixed}")
    print(f"Files regenerated: {regen_ok}")

if __name__ == "__main__":
    main()