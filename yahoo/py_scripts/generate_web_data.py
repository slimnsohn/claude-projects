import pandas as pd
import json
import os
from collections import defaultdict
import numpy as np

def generate_web_player_data():
    """
    Generate consolidated player data for web interface.
    Combines NBA stats, Yahoo draft data, and creates analysis insights.
    """
    
    print("=== GENERATING WEB DATA ===\n")
    
    # Load player mapping
    print("Loading player mappings...")
    with open('historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json', 'r') as f:
        yahoo_to_nba = json.load(f)
    
    with open('historical_nba_stats/player_mappings/nba_player_mapping.json', 'r') as f:
        nba_players = json.load(f)
    
    print(f"Loaded mappings for {len(yahoo_to_nba)} Yahoo players and {len(nba_players)} NBA players")
    
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
    
    for year in years:
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            with open(draft_file, 'r') as f:
                draft_data = json.load(f)
                all_yahoo_drafts[year] = draft_data
                print(f"  {year}: {len(draft_data.get('picks', []))} draft picks")
    
    # Create comprehensive player profiles
    print("Building comprehensive player profiles...")
    
    player_profiles = {}
    draft_value_analysis = {}
    
    # Process each NBA player
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
                    'value_analysis': {}
                }
            
            # Add season stats
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
    
    # Add Yahoo draft information
    print("Adding Yahoo draft history...")
    
    for year, draft_data in all_yahoo_drafts.items():
        if 'picks' not in draft_data:
            continue
            
        for pick in draft_data['picks']:
            yahoo_id = str(pick['player_id'])
            draft_cost = pick['draft_cost']
            team_name = pick['fantasy_team']
            
            # Find corresponding NBA player
            if yahoo_id in yahoo_to_nba:
                nba_id = yahoo_to_nba[yahoo_id]['nba_id']
                
                if nba_id in player_profiles:
                    draft_info = {
                        'year': year,
                        'draft_cost': draft_cost,
                        'fantasy_team': team_name,
                        'pick_number': pick.get('pick_number', 0)
                    }
                    player_profiles[nba_id]['yahoo_draft_history'].append(draft_info)
    
    # Calculate career summaries and value analysis
    print("Calculating career summaries and value analysis...")
    
    insights_data = {
        'top_values': [],
        'biggest_busts': [],
        'consistent_performers': [],
        'breakout_players': [],
        'position_trends': {},
        'cost_analysis': {}
    }
    
    for nba_id, profile in player_profiles.items():
        seasons = profile['seasons']
        drafts = profile['yahoo_draft_history']
        
        if not seasons:
            continue
        
        # Calculate career averages
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
        
        # Value analysis for drafted players
        if drafts:
            total_cost = sum([d['draft_cost'] for d in drafts])
            avg_cost = round(total_cost / len(drafts), 1)
            
            # Calculate value score based on production vs cost
            production_score = 0
            if career_summary.get('pts_pg_avg', 0) > 0:
                # Simple value calculation: points + rebounds + assists - turnovers
                production_score = (
                    career_summary.get('pts_pg_avg', 0) +
                    career_summary.get('reb_pg_avg', 0) +
                    career_summary.get('ast_pg_avg', 0) -
                    career_summary.get('to_pg_avg', 0)
                )
            
            value_score = production_score / max(avg_cost, 1) * 10  # Scale factor
            
            profile['value_analysis'] = {
                'times_drafted': len(drafts),
                'total_cost': total_cost,
                'avg_cost': avg_cost,
                'production_score': round(production_score, 2),
                'value_score': round(value_score, 2),
                'cost_range': f"${min([d['draft_cost'] for d in drafts])}-${max([d['draft_cost'] for d in drafts])}"
            }
            
            # Add to insights categories
            if value_score > 2.0 and len(drafts) >= 2:
                insights_data['top_values'].append({
                    'player_name': profile['player_name'],
                    'nba_id': nba_id,
                    'value_score': round(value_score, 2),
                    'avg_cost': avg_cost,
                    'production_score': round(production_score, 2)
                })
            
            elif value_score < 0.5 and avg_cost > 20:
                insights_data['biggest_busts'].append({
                    'player_name': profile['player_name'],
                    'nba_id': nba_id,
                    'value_score': round(value_score, 2),
                    'avg_cost': avg_cost,
                    'production_score': round(production_score, 2)
                })
    
    # Sort insights data
    insights_data['top_values'].sort(key=lambda x: x['value_score'], reverse=True)
    insights_data['biggest_busts'].sort(key=lambda x: x['value_score'])
    
    # Find consistent performers (low variance in production)
    for nba_id, profile in player_profiles.items():
        seasons = profile['seasons']
        if len(seasons) >= 3:  # Need at least 3 seasons
            pts_values = [s['pts_pg'] for s in seasons.values()]
            if pts_values:
                variance = np.var(pts_values)
                avg_pts = np.mean(pts_values)
                
                # Low variance relative to scoring level = consistent
                if variance < 2.0 and avg_pts > 10:
                    insights_data['consistent_performers'].append({
                        'player_name': profile['player_name'],
                        'nba_id': nba_id,
                        'avg_pts': round(avg_pts, 1),
                        'pts_variance': round(variance, 2),
                        'seasons': len(seasons)
                    })
    
    insights_data['consistent_performers'].sort(key=lambda x: x['pts_variance'])
    
    # Limit insight lists to top 20
    for key in ['top_values', 'biggest_busts', 'consistent_performers']:
        insights_data[key] = insights_data[key][:20]
    
    # Sort all players by last name
    sorted_players = sorted(player_profiles.items(), key=lambda x: x[1]['last_name'])
    
    # Create web-ready data structure
    web_data = {
        'players': dict(sorted_players),
        'insights': insights_data,
        'metadata': {
            'total_players': len(player_profiles),
            'players_with_drafts': len([p for p in player_profiles.values() if p['yahoo_draft_history']]),
            'years_covered': f"{min(all_nba_stats.keys())}-{max(all_nba_stats.keys())}",
            'last_updated': '2025-08-18'
        }
    }
    
    # Save data files
    print("Saving web data files...")
    
    # Main player data (split due to size)
    with open('html_reports/data/players.json', 'w') as f:
        json.dump({'players': dict(sorted_players)}, f, indent=2)
    
    with open('html_reports/data/insights.json', 'w') as f:
        json.dump(insights_data, f, indent=2)
    
    with open('html_reports/data/metadata.json', 'w') as f:
        json.dump(web_data['metadata'], f, indent=2)
    
    # Create searchable player index
    player_index = []
    for nba_id, profile in sorted_players:
        player_index.append({
            'id': nba_id,
            'name': profile['player_name'],
            'last_name': profile['last_name'],
            'first_name': profile['first_name'],
            'seasons': len(profile['seasons']),
            'drafted': len(profile['yahoo_draft_history']) > 0,
            'years_active': profile['career_summary'].get('years_active', ''),
            'avg_points': profile['career_summary'].get('pts_pg_avg', 0)
        })
    
    with open('html_reports/data/player_index.json', 'w') as f:
        json.dump(player_index, f, indent=2)
    
    print(f"\n=== WEB DATA GENERATION COMPLETE ===")
    print(f"Generated data for {len(player_profiles)} players")
    print(f"Players with draft history: {len([p for p in player_profiles.values() if p['yahoo_draft_history']])}")
    print(f"Top values identified: {len(insights_data['top_values'])}")
    print(f"Biggest busts identified: {len(insights_data['biggest_busts'])}")
    print(f"Consistent performers: {len(insights_data['consistent_performers'])}")
    print("Data files saved to html_reports/data/")

if __name__ == "__main__":
    generate_web_player_data()