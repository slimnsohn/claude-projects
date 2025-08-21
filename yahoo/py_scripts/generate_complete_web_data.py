import pandas as pd
import json
import os
from collections import defaultdict
import numpy as np

def generate_complete_web_data():
    """
    Generate web data including ALL draft history from all years,
    not just players with NBA mapping.
    """
    
    print("=== GENERATING COMPLETE WEB DATA ===\n")
    
    # Load player mapping
    print("Loading player mappings...")
    
    # Load comprehensive mapping
    comprehensive_file = 'historical_nba_stats/player_mappings/comprehensive_mapping.json'
    if os.path.exists(comprehensive_file):
        with open(comprehensive_file, 'r') as f:
            comprehensive_data = json.load(f)
        
        yahoo_to_nba = comprehensive_data['mapped_players']
        all_yahoo_players = comprehensive_data['all_yahoo_players']
    else:
        print("Comprehensive mapping not found, creating it first...")
        import create_comprehensive_player_mapping
        comprehensive_data = create_comprehensive_player_mapping.create_comprehensive_player_mapping()
        yahoo_to_nba = comprehensive_data['mapped_players']
        all_yahoo_players = comprehensive_data['all_yahoo_players']
    
    # Load NBA players
    with open('historical_nba_stats/player_mappings/nba_player_mapping.json', 'r') as f:
        nba_players = json.load(f)
    
    print(f"Loaded mappings for {len(yahoo_to_nba)} mapped Yahoo players")
    print(f"Loaded {len(all_yahoo_players)} total Yahoo players")
    print(f"Loaded {len(nba_players)} NBA players")
    
    # Load NBA stats for all years
    print("Loading NBA performance data...")
    all_nba_stats = {}
    years = range(2010, 2025)
    
    for year in years:
        nba_file = f'historical_nba_stats/{year}/fantasy_relevant_stats.csv'
        if os.path.exists(nba_file):
            df = pd.read_csv(nba_file)
            all_nba_stats[year] = df
            print(f"  {year}: {len(df)} players")
    
    # Load Yahoo draft data for all years
    print("Loading Yahoo draft data...")
    all_yahoo_drafts = {}
    all_draft_history = defaultdict(list)  # Track ALL draft history
    
    for year in years:
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            with open(draft_file, 'r') as f:
                draft_data = json.load(f)
                all_yahoo_drafts[year] = draft_data
                
                # Process ALL draft picks, not just mapped ones
                if 'picks' in draft_data:
                    for pick in draft_data['picks']:
                        yahoo_id = str(pick['player_id'])
                        draft_info = {
                            'year': year,
                            'draft_cost': pick['draft_cost'],
                            'fantasy_team': pick['fantasy_team'],
                            'pick_number': pick.get('pick_number', 0),
                            'is_snake_draft': pick['draft_cost'] == 0,
                            'yahoo_id': yahoo_id
                        }
                        all_draft_history[yahoo_id].append(draft_info)
                
                print(f"  {year}: {len(draft_data.get('picks', []))} draft picks")
    
    # Create comprehensive player profiles (NBA players + unmapped Yahoo players)
    print("Building comprehensive player profiles...")
    
    player_profiles = {}
    draft_value_analysis = {}
    
    # First, process all NBA players with their seasons
    for year, nba_df in all_nba_stats.items():
        for _, player_row in nba_df.iterrows():
            nba_id = str(player_row['personId'])
            player_name = player_row['personName']
            
            # Initialize player profile if not exists
            if nba_id not in player_profiles:
                player_profiles[nba_id] = {
                    'player_id': nba_id,
                    'player_name': player_name,
                    'last_name': player_name.split()[-1],
                    'first_name': ' '.join(player_name.split()[:-1]),
                    'seasons': {},
                    'career_summary': {},
                    'yahoo_draft_history': [],
                    'value_analysis': {},
                    'data_source': 'nba_mapped'
                }
            
            # Add season stats (same as before)
            season_stats = {
                'year': year,
                'games_played': int(player_row['games_played']),
                'team': player_row.get('teamTricode', ''),
                'fg_pct': round(float(player_row['field_goal_percentage']), 3),
                'ft_pct': round(float(player_row['free_throw_percentage']), 3),
                'threepm_pg': round(float(player_row['threepointers_per_game']), 2),
                'pts_pg': round(float(player_row['points_per_game']), 2),
                'reb_pg': round(float(player_row['rebounds_per_game']), 2),
                'ast_pg': round(float(player_row['assists_per_game']), 2),
                'stl_pg': round(float(player_row['steals_per_game']), 2),
                'blk_pg': round(float(player_row['blocks_per_game']), 2),
                'to_pg': round(float(player_row['turnovers_per_game']), 2)
            }
            
            player_profiles[nba_id]['seasons'][year] = season_stats
    
    # Add draft history to NBA players
    print("Adding draft history to NBA players...")
    mapped_draft_count = 0
    
    for yahoo_id, draft_history in all_draft_history.items():
        if yahoo_id in yahoo_to_nba:
            nba_id = yahoo_to_nba[yahoo_id]['nba_id']
            if nba_id in player_profiles:
                player_profiles[nba_id]['yahoo_draft_history'] = draft_history
                mapped_draft_count += len(draft_history)
    
    # Create profiles for unmapped Yahoo players (those without NBA stats)
    print("Creating profiles for unmapped Yahoo players...")
    unmapped_draft_count = 0
    
    for yahoo_id, draft_history in all_draft_history.items():
        if yahoo_id not in yahoo_to_nba:
            # Create a profile for this unmapped player
            profile_id = f"yahoo_{yahoo_id}"
            
            player_profiles[profile_id] = {
                'player_id': profile_id,
                'player_name': f"Player {yahoo_id}",  # We don't have the real name
                'last_name': f"Player{yahoo_id}",
                'first_name': "",
                'seasons': {},  # No NBA stats available
                'career_summary': {},
                'yahoo_draft_history': draft_history,
                'value_analysis': {},
                'data_source': 'yahoo_only',
                'yahoo_id': yahoo_id
            }
            unmapped_draft_count += len(draft_history)
    
    print(f"Draft history added:")
    print(f"  Mapped NBA players: {mapped_draft_count} draft entries")
    print(f"  Unmapped Yahoo players: {unmapped_draft_count} draft entries") 
    
    # Calculate career summaries and value analysis (same logic as before)
    print("Calculating career summaries and value analysis...")
    
    insights_data = {
        'top_values': [],
        'biggest_busts': [],
        'consistent_performers': [],
        'snake_draft_years': list(range(2010, 2016)),  # Years with $0 costs (2010-2015)
        'auction_draft_years': list(range(2016, 2025)),  # Years with auction costs (2016-2024)
        'total_draft_entries': sum(len(h) for h in all_draft_history.values())
    }
    
    # Process career summaries for NBA players
    for profile_id, profile in player_profiles.items():
        if profile['data_source'] == 'nba_mapped':
            seasons = profile['seasons']
            drafts = profile['yahoo_draft_history']
            
            if seasons:
                # Calculate career averages (same as before)
                career_stats = defaultdict(list)
                for year_stats in seasons.values():
                    for stat, value in year_stats.items():
                        if stat not in ['year', 'team'] and isinstance(value, (int, float)):
                            career_stats[stat].append(value)
                
                career_summary = {}
                for stat, values in career_stats.items():
                    if values:
                        career_summary[f'{stat}_avg'] = round(np.mean(values), 2)
                        career_summary[f'{stat}_best'] = round(max(values), 2) if stat != 'to_pg' else round(min(values), 2)
                
                career_summary['total_seasons'] = len(seasons)
                career_summary['total_games'] = sum([s['games_played'] for s in seasons.values()])
                career_summary['years_active'] = f"{min(seasons.keys())}-{max(seasons.keys())}"
                
                profile['career_summary'] = career_summary
                
                # Value analysis for auction years only
                auction_drafts = [d for d in drafts if d['draft_cost'] > 0]
                if auction_drafts:
                    total_cost = sum([d['draft_cost'] for d in auction_drafts])
                    avg_cost = round(total_cost / len(auction_drafts), 1)
                    
                    production_score = (
                        career_summary.get('pts_pg_avg', 0) +
                        career_summary.get('reb_pg_avg', 0) +
                        career_summary.get('ast_pg_avg', 0) -
                        career_summary.get('to_pg_avg', 0)
                    )
                    
                    value_score = production_score / max(avg_cost, 1) * 10
                    
                    profile['value_analysis'] = {
                        'times_drafted': len(drafts),
                        'auction_drafts': len(auction_drafts),
                        'snake_drafts': len(drafts) - len(auction_drafts),
                        'total_cost': total_cost,
                        'avg_cost': avg_cost,
                        'production_score': round(production_score, 2),
                        'value_score': round(value_score, 2),
                        'cost_range': f"${min([d['draft_cost'] for d in auction_drafts])}-${max([d['draft_cost'] for d in auction_drafts])}" if auction_drafts else "N/A"
                    }
                    
                    # Add to insights for auction years
                    if value_score > 2.0 and len(auction_drafts) >= 2:
                        insights_data['top_values'].append({
                            'player_name': profile['player_name'],
                            'profile_id': profile_id,
                            'value_score': round(value_score, 2),
                            'avg_cost': avg_cost,
                            'production_score': round(production_score, 2)
                        })
        else:
            # For Yahoo-only players, just add basic draft info
            drafts = profile['yahoo_draft_history']
            auction_drafts = [d for d in drafts if d['draft_cost'] > 0]
            
            profile['value_analysis'] = {
                'times_drafted': len(drafts),
                'auction_drafts': len(auction_drafts),
                'snake_drafts': len(drafts) - len(auction_drafts),
                'total_cost': sum([d['draft_cost'] for d in auction_drafts]),
                'avg_cost': round(sum([d['draft_cost'] for d in auction_drafts]) / max(len(auction_drafts), 1), 1) if auction_drafts else 0,
                'production_score': 0,  # No NBA stats available
                'value_score': 0,
                'cost_range': "Unknown (no NBA data)"
            }
    
    # Sort insights data
    insights_data['top_values'].sort(key=lambda x: x['value_score'], reverse=True)
    insights_data['top_values'] = insights_data['top_values'][:20]
    
    # Sort all players by last name (NBA players first, then Yahoo-only)
    sorted_players = sorted(player_profiles.items(), key=lambda x: (
        x[1]['data_source'] == 'yahoo_only',  # NBA players first
        x[1]['last_name']
    ))
    
    # Create web-ready data structure
    web_data = {
        'players': dict(sorted_players),
        'insights': insights_data,
        'metadata': {
            'total_players': len(player_profiles),
            'nba_mapped_players': len([p for p in player_profiles.values() if p['data_source'] == 'nba_mapped']),
            'yahoo_only_players': len([p for p in player_profiles.values() if p['data_source'] == 'yahoo_only']),
            'players_with_drafts': len([p for p in player_profiles.values() if p['yahoo_draft_history']]),
            'total_draft_entries': insights_data['total_draft_entries'],
            'snake_draft_years': '2010-2015',
            'auction_draft_years': '2016-2024',
            'years_covered': f"{min(all_nba_stats.keys())}-{max(all_nba_stats.keys())}",
            'last_updated': '2025-08-18'
        }
    }
    
    # Save data files
    print("Saving web data files...")
    
    with open('html_reports/data/players.json', 'w') as f:
        json.dump({'players': dict(sorted_players)}, f, indent=2)
    
    with open('html_reports/data/insights.json', 'w') as f:
        json.dump(insights_data, f, indent=2)
    
    with open('html_reports/data/metadata.json', 'w') as f:
        json.dump(web_data['metadata'], f, indent=2)
    
    # Create searchable player index
    player_index = []
    for profile_id, profile in sorted_players:
        player_index.append({
            'id': profile_id,
            'name': profile['player_name'],
            'last_name': profile['last_name'],
            'first_name': profile['first_name'],
            'seasons': len(profile['seasons']),
            'drafted': len(profile['yahoo_draft_history']) > 0,
            'years_active': profile['career_summary'].get('years_active', ''),
            'avg_points': profile['career_summary'].get('pts_pg_avg', 0),
            'data_source': profile['data_source']
        })
    
    with open('html_reports/data/player_index.json', 'w') as f:
        json.dump(player_index, f, indent=2)
    
    print(f"\n=== COMPLETE WEB DATA GENERATION COMPLETE ===")
    print(f"Generated data for {len(player_profiles)} total players:")
    print(f"  NBA players with stats: {web_data['metadata']['nba_mapped_players']}")
    print(f"  Yahoo-only players: {web_data['metadata']['yahoo_only_players']}")
    print(f"  Players with draft history: {web_data['metadata']['players_with_drafts']}")
    print(f"  Total draft entries: {web_data['metadata']['total_draft_entries']}")
    snake_entries = sum(len([d for d in p['yahoo_draft_history'] if d['draft_cost'] == 0]) for p in player_profiles.values())
    auction_entries = sum(len([d for d in p['yahoo_draft_history'] if d['draft_cost'] > 0]) for p in player_profiles.values())
    print(f"  Snake draft years (2010-2015): {snake_entries} entries")
    print(f"  Auction draft years (2016-2024): {auction_entries} entries")
    print("Data files saved to html_reports/data/")

if __name__ == "__main__":
    generate_complete_web_data()