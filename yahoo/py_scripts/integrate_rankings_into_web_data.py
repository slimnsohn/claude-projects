#!/usr/bin/env python3
"""
Integrate Player Rankings into Web Data
Add preseason rankings (draft order) and auction values to player season stats.
"""

import json
import os
from collections import defaultdict

def integrate_rankings_for_year(year):
    """
    Integrate ranking data into the season stats for a specific year.
    """
    print(f"Processing rankings for {year}...")
    
    # Check if we have ranking data for this year
    ranking_file = f'league_data/{year}/processed_data/player_rankings.json'
    if not os.path.exists(ranking_file):
        print(f"  No ranking data found for {year}")
        return {}
    
    # Load ranking data
    with open(ranking_file, 'r', encoding='utf-8') as f:
        ranking_data = json.load(f)
    
    # Extract preseason rankings and draft costs
    player_rankings = {}
    
    if 'preseason_rankings' in ranking_data:
        for player in ranking_data['preseason_rankings']:
            player_id = str(player['player_id'])
            player_rankings[player_id] = {
                'preseason_rank': player['preseason_rank'],
                'draft_cost': player['draft_cost'],
                'draft_type': 'auction' if player['draft_cost'] > 0 else 'snake'
            }
    
    print(f"  Found rankings for {len(player_rankings)} players")
    return player_rankings

def update_web_data_with_rankings():
    """
    Update the web data files to include ranking information in season stats.
    """
    print("=== INTEGRATING RANKINGS INTO WEB DATA ===\\n")
    
    # Load current web data
    web_data_file = 'html_reports/data/players.json'
    if not os.path.exists(web_data_file):
        print("ERROR: Web data file not found. Please run generate_complete_web_data.py first.")
        return
    
    with open(web_data_file, 'r', encoding='utf-8') as f:
        web_data = json.load(f)
    
    players = web_data['players']
    print(f"Loaded web data for {len(players)} players")
    
    # Load rankings for available years
    years_with_rankings = []
    all_rankings = {}
    
    for year in range(2010, 2025):
        rankings = integrate_rankings_for_year(year)
        if rankings:
            all_rankings[year] = rankings
            years_with_rankings.append(year)
    
    print(f"\\nFound ranking data for years: {years_with_rankings}")
    
    # Update player season stats with ranking information
    updated_players = 0
    added_rankings = 0
    
    for player_id, player_data in players.items():
        player_updated = False
        
        # Check if this is an NBA player with seasons
        if 'seasons' in player_data and player_data['seasons']:
            
            # Check each season to see if we can add ranking data
            for year_str, season_stats in player_data['seasons'].items():
                year = int(year_str)
                
                if year in all_rankings:
                    # Look for this player in the draft data for that year
                    # We need to find the yahoo_id for this player
                    yahoo_id = None
                    
                    # For NBA players, we need to reverse-lookup their Yahoo ID
                    # Check if they have draft history that year
                    if 'yahoo_draft_history' in player_data:
                        for draft_entry in player_data['yahoo_draft_history']:
                            if draft_entry['year'] == year:
                                yahoo_id = draft_entry.get('yahoo_id')
                                break
                    
                    # If we found the yahoo_id, add ranking data
                    if yahoo_id and yahoo_id in all_rankings[year]:
                        ranking_info = all_rankings[year][yahoo_id]
                        
                        # Add ranking data to season stats
                        season_stats['preseason_rank'] = ranking_info['preseason_rank']
                        season_stats['draft_cost'] = ranking_info['draft_cost']
                        season_stats['draft_type'] = ranking_info['draft_type']
                        
                        player_updated = True
                        added_rankings += 1
        
        # Also check Yahoo-only players
        elif player_data.get('data_source') == 'yahoo_only':
            if 'yahoo_draft_history' in player_data:
                for draft_entry in player_data['yahoo_draft_history']:
                    year = draft_entry['year']
                    yahoo_id = draft_entry.get('yahoo_id')
                    
                    if year in all_rankings and yahoo_id in all_rankings[year]:
                        ranking_info = all_rankings[year][yahoo_id]
                        
                        # For Yahoo-only players, add ranking info to draft history
                        draft_entry['preseason_rank'] = ranking_info['preseason_rank']
                        draft_entry['confirmed_draft_cost'] = ranking_info['draft_cost']
                        draft_entry['confirmed_draft_type'] = ranking_info['draft_type']
                        
                        player_updated = True
                        added_rankings += 1
        
        if player_updated:
            updated_players += 1
    
    print(f"\\nUpdate Summary:")
    print(f"  Updated {updated_players} players")
    print(f"  Added {added_rankings} ranking entries")
    
    # Save updated web data
    with open(web_data_file, 'w', encoding='utf-8') as f:
        json.dump(web_data, f, indent=2, ensure_ascii=False)
    
    print(f"\\nUpdated web data saved to {web_data_file}")
    
    # Also create a rankings summary
    rankings_summary = {
        'years_with_data': years_with_rankings,
        'total_players_per_year': {year: len(rankings) for year, rankings in all_rankings.items()},
        'total_ranking_entries': sum(len(rankings) for rankings in all_rankings.values()),
        'integration_stats': {
            'players_updated': updated_players,
            'ranking_entries_added': added_rankings
        }
    }
    
    with open('html_reports/data/rankings_summary.json', 'w', encoding='utf-8') as f:
        json.dump(rankings_summary, f, indent=2)
    
    print(f"Rankings summary saved to html_reports/data/rankings_summary.json")

def create_rankings_for_2024_manual():
    """
    Manually create ranking data for 2024 since we have that data.
    This is a backup in case the full API extraction doesn't work.
    """
    print("Creating manual ranking data for 2024...")
    
    # Load the existing 2024 draft data
    draft_file = 'league_data/2024/processed_data/draft_analysis.json'
    if not os.path.exists(draft_file):
        print("ERROR: 2024 draft data not found")
        return
    
    with open(draft_file, 'r') as f:
        draft_data = json.load(f)
    
    if 'picks' not in draft_data:
        print("ERROR: No picks found in draft data")
        return
    
    # Create ranking data from draft picks
    ranking_data = {
        'year': 2024,
        'league_key': '454.l.44006',
        'preseason_rankings': [],
        'end_season_rankings': []
    }
    
    # Sort picks by pick number (preseason ranking)
    picks = sorted(draft_data['picks'], key=lambda x: x.get('pick_number', x.get('round', 999)))
    
    for pick in picks:
        ranking_data['preseason_rankings'].append({
            'player_id': pick['player_id'],
            'player_name': pick.get('player_name', f"Player {pick['player_id']}"),
            'preseason_rank': pick.get('pick_number', len(ranking_data['preseason_rankings']) + 1),
            'draft_cost': pick['draft_cost']
        })
    
    # Save ranking data
    output_dir = 'league_data/2024/processed_data'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'player_rankings.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ranking_data, f, indent=2, ensure_ascii=False)
    
    print(f"Manual ranking data saved to {output_file}")

if __name__ == "__main__":
    # First create manual 2024 data if needed
    if not os.path.exists('league_data/2024/processed_data/player_rankings.json'):
        create_rankings_for_2024_manual()
    
    # Then integrate all available rankings
    update_web_data_with_rankings()