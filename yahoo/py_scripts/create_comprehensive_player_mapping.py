import json
import pandas as pd
from difflib import SequenceMatcher
import os

def similar(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def create_comprehensive_player_mapping():
    """
    Create comprehensive player mapping using ALL draft data from all years,
    not just recent years accessible via API.
    """
    
    print("=== COMPREHENSIVE PLAYER MAPPING ===\n")
    
    # Load NBA player mapping
    print("Loading NBA player mapping...")
    with open('historical_nba_stats/player_mappings/nba_player_mapping.json', 'r') as f:
        nba_players = json.load(f)
    
    print(f"Loaded {len(nba_players)} NBA players")
    
    # Collect Yahoo players from ALL draft data files
    print("Collecting Yahoo player data from all draft files...")
    all_yahoo_players = {}
    
    years = range(2010, 2025)
    
    for year in years:
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            with open(draft_file, 'r') as f:
                draft_data = json.load(f)
                
            if 'picks' in draft_data:
                print(f"  {year}: {len(draft_data['picks'])} picks")
                
                for pick in draft_data['picks']:
                    yahoo_id = str(pick['player_id'])
                    if yahoo_id not in all_yahoo_players:
                        # We don't have name data, so we'll create a placeholder
                        all_yahoo_players[yahoo_id] = {
                            'player_id': yahoo_id,
                            'draft_years': [],
                            'total_drafts': 0
                        }
                    
                    all_yahoo_players[yahoo_id]['draft_years'].append(year)
                    all_yahoo_players[yahoo_id]['total_drafts'] += 1
    
    print(f"Found {len(all_yahoo_players)} unique Yahoo players across all years")
    
    # Load existing mapping to get names for recent players
    existing_mapping_file = 'historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json'
    existing_mapping = {}
    
    if os.path.exists(existing_mapping_file):
        with open(existing_mapping_file, 'r') as f:
            existing_mapping = json.load(f)
        print(f"Loaded {len(existing_mapping)} existing mappings")
    
    # Create NBA name lookup
    nba_by_name = {}
    for nba_id, nba_data in nba_players.items():
        nba_name = nba_data['name'].lower()
        nba_by_name[nba_name] = {
            'nba_id': nba_id,
            'name': nba_data['name']
        }
    
    print("Creating comprehensive mapping...")
    
    # Start with existing mappings
    comprehensive_mapping = existing_mapping.copy()
    
    # For players not in existing mapping, try to match by NBA stats
    unmapped_count = 0
    
    for yahoo_id, yahoo_data in all_yahoo_players.items():
        if yahoo_id not in comprehensive_mapping:
            unmapped_count += 1
            
            # Find potential NBA matches by looking through seasons where they were drafted
            potential_matches = []
            
            for year in yahoo_data['draft_years']:
                nba_file = f'historical_nba_stats/{year}/fantasy_relevant_stats.csv'
                if os.path.exists(nba_file):
                    nba_df = pd.read_csv(nba_file)
                    
                    # Get top players from that season as potential matches
                    top_players = nba_df.nlargest(50, 'points_per_game')
                    
                    for _, player in top_players.iterrows():
                        potential_matches.append({
                            'nba_id': str(player['personId']),
                            'name': player['personName'],
                            'season': year,
                            'points': player['points_per_game']
                        })
            
            # For now, we'll mark these as unmapped but trackable
            # Could add more sophisticated matching logic later
    
    print(f"Comprehensive mapping complete:")
    print(f"  Mapped players: {len(comprehensive_mapping)}")
    print(f"  Unmapped players: {unmapped_count}")
    print(f"  Total coverage: {len(comprehensive_mapping) / len(all_yahoo_players) * 100:.1f}%")
    
    # Save all Yahoo players data (even unmapped ones)
    all_players_file = 'historical_nba_stats/player_mappings/all_yahoo_players.json'
    with open(all_players_file, 'w') as f:
        json.dump(all_yahoo_players, f, indent=2)
    
    print(f"Saved all Yahoo players data to: {all_players_file}")
    
    # Update the comprehensive mapping
    comprehensive_file = 'historical_nba_stats/player_mappings/comprehensive_mapping.json'
    
    mapping_data = {
        'mapped_players': comprehensive_mapping,
        'all_yahoo_players': all_yahoo_players,
        'mapping_stats': {
            'total_yahoo_players': len(all_yahoo_players),
            'mapped_players': len(comprehensive_mapping),
            'coverage_percentage': len(comprehensive_mapping) / len(all_yahoo_players) * 100,
            'years_covered': '2010-2024'
        }
    }
    
    with open(comprehensive_file, 'w') as f:
        json.dump(mapping_data, f, indent=2)
    
    print(f"Saved comprehensive mapping to: {comprehensive_file}")
    
    return mapping_data

if __name__ == "__main__":
    create_comprehensive_player_mapping()