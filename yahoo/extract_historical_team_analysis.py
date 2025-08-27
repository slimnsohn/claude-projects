#!/usr/bin/env python3
"""
Extract Historical Team Analysis
Calculate preseason projections and final rankings for each owner by year
"""

import json
import pandas as pd
import numpy as np
from create_2025_projections import Fantasy2025Projector

def load_final_rankings():
    """Load final rankings from available data files."""
    final_rankings = {}
    
    # Try to load from draft results CSV
    try:
        df = pd.read_csv('jsons/draft_results.csv')
        print(f"Found draft results with {len(df)} records")
        
        # Extract year-by-year rankings
        for _, row in df.iterrows():
            year = int(row['year'])
            team = row['team_name']
            final_rank = int(row.get('final_rank', 99))
            
            if year not in final_rankings:
                final_rankings[year] = {}
            
            final_rankings[year][team] = {
                'final_rank': final_rank,
                'regular_season_rank': int(row.get('regular_season_rank', final_rank)),
                'playoff_rank': int(row.get('playoff_rank', final_rank))
            }
            
    except Exception as e:
        print(f"Could not load draft_results.csv: {e}")
    
    # Try to load from 2020 ranks CSV
    try:
        df_2020 = pd.read_csv('jsons/2020_ranks_pre.csv')
        print(f"Found 2020 pre-ranks with {len(df_2020)} records")
        
        if 2020 not in final_rankings:
            final_rankings[2020] = {}
            
        for _, row in df_2020.iterrows():
            team = row['team_name']
            final_rankings[2020][team] = {
                'final_rank': int(row['final_rank']),
                'regular_season_rank': int(row.get('regular_season_rank', row['final_rank'])),
                'playoff_rank': int(row.get('playoff_rank', row['final_rank']))
            }
    except Exception as e:
        print(f"Could not load 2020_ranks_pre.csv: {e}")
    
    return final_rankings

def calculate_team_projections_by_year():
    """Calculate preseason projections for each team by year."""
    
    # Load players data
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    # Group drafts by year and team
    teams_by_year = {}
    
    for player_id, player_info in players_data['players'].items():
        player_name = player_info['player_name']
        draft_history = player_info.get('yahoo_draft_history', [])
        
        for draft in draft_history:
            year = draft['year']
            team = draft['fantasy_team']
            cost = draft.get('draft_cost', 1)
            
            if year not in teams_by_year:
                teams_by_year[year] = {}
            if team not in teams_by_year[year]:
                teams_by_year[year][team] = []
            
            teams_by_year[year][team].append({
                'player': player_name,
                'cost': cost,
                'player_data': player_info
            })
    
    # Calculate projections for each year using retrospective modeling
    team_projections_by_year = {}
    
    for target_year in sorted(teams_by_year.keys()):
        if target_year < 2015:  # Need enough training data
            continue
            
        print(f"\nCalculating projections for {target_year}...")
        
        try:
            # Create projector for this specific year
            projector = Fantasy2025Projector()
            
            # Use data available up to target year - 1 for training
            training_end = target_year - 1
            training_start = max(2010, training_end - 7)  # Use 8 years of training
            
            projector.training_years = list(range(training_start, training_end + 1))
            projector.validation_years = [target_year]
            
            # Load and prepare data
            projector.load_and_prepare_data()
            projector.define_feature_set()
            
            # Train models
            model_results, best_model = projector.train_models()
            
            # Generate projections for that year
            projections_df = projector.generate_2025_projections(best_model)
            
            # Create lookup dictionary
            player_projections = {}
            for _, row in projections_df.iterrows():
                player_projections[row['personName']] = row['projected_2025_value']
            
            # Calculate team totals
            team_projections = {}
            for team, roster in teams_by_year[target_year].items():
                total_projection = 0
                total_cost = 0
                matched_players = 0
                
                for player_info in roster:
                    player_name = player_info['player']
                    cost = player_info['cost']
                    
                    # Find projection for this player
                    projection = player_projections.get(player_name, 300)  # Default 300 for unmatched
                    if player_name in player_projections:
                        matched_players += 1
                    
                    total_projection += projection
                    total_cost += cost
                
                team_projections[team] = {
                    'total_projection': int(total_projection),
                    'total_cost': int(total_cost),
                    'roster_size': len(roster),
                    'matched_players': matched_players,
                    'avg_projection': int(total_projection / max(1, len(roster)))
                }
            
            team_projections_by_year[target_year] = team_projections
            print(f"  Calculated projections for {len(team_projections)} teams")
            
        except Exception as e:
            print(f"  Error calculating projections for {target_year}: {e}")
            continue
    
    return team_projections_by_year

def combine_projections_and_rankings():
    """Combine preseason projections with final rankings."""
    
    print("Loading final rankings...")
    final_rankings = load_final_rankings()
    
    print("Calculating team projections...")
    team_projections = calculate_team_projections_by_year()
    
    # Combine data
    combined_results = {}
    
    for year in sorted(set(list(final_rankings.keys()) + list(team_projections.keys()))):
        year_rankings = final_rankings.get(year, {})
        year_projections = team_projections.get(year, {})
        
        combined_results[year] = []
        
        # Get all teams from both sources
        all_teams = set(list(year_rankings.keys()) + list(year_projections.keys()))
        
        for team in all_teams:
            ranking_data = year_rankings.get(team, {})
            projection_data = year_projections.get(team, {})
            
            combined_results[year].append({
                'team': team,
                'year': year,
                'preseason_projection': projection_data.get('total_projection', 0),
                'total_cost': projection_data.get('total_cost', 0),
                'roster_size': projection_data.get('roster_size', 0),
                'matched_players': projection_data.get('matched_players', 0),
                'final_rank': ranking_data.get('final_rank', 99),
                'regular_season_rank': ranking_data.get('regular_season_rank', 99),
                'playoff_rank': ranking_data.get('playoff_rank', 99)
            })
        
        # Sort by final rank
        combined_results[year].sort(key=lambda x: x['final_rank'])
    
    return combined_results

def print_historical_analysis():
    """Print the historical analysis results."""
    
    results = combine_projections_and_rankings()
    
    print("\n" + "="*80)
    print("HISTORICAL TEAM ANALYSIS: PRESEASON PROJECTIONS vs FINAL RANKINGS")
    print("="*80)
    
    for year in sorted(results.keys(), reverse=True):
        year_data = results[year]
        
        print(f"\n🏀 {year} SEASON")
        print("-" * 60)
        print(f"{'Team':<25} {'Projection':<12} {'Cost':<8} {'Roster':<8} {'Final Rank':<12}")
        print("-" * 60)
        
        for team_data in year_data:
            team = team_data['team'][:24]  # Truncate long names
            projection = team_data['preseason_projection']
            cost = team_data['total_cost']
            roster = team_data['roster_size']
            final_rank = team_data['final_rank']
            
            # Add indicators for performance
            indicator = ""
            if projection >= 7500:
                indicator = "🏆"
            elif projection >= 7000:
                indicator = "⭐"
            elif projection >= 6500:
                indicator = "💪"
            
            rank_display = f"#{final_rank}" if final_rank < 99 else "N/A"
            
            print(f"{team:<25} {projection:<12} ${cost:<7} {roster:<8} {rank_display:<12} {indicator}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    
    all_data = []
    for year_data in results.values():
        all_data.extend(year_data)
    
    # Filter only teams with both projection and ranking data
    complete_data = [d for d in all_data if d['preseason_projection'] > 0 and d['final_rank'] < 99]
    
    if complete_data:
        projections = [d['preseason_projection'] for d in complete_data]
        ranks = [d['final_rank'] for d in complete_data]
        
        print(f"Total team seasons analyzed: {len(complete_data)}")
        print(f"Average preseason projection: {np.mean(projections):.0f}")
        print(f"Projection range: {min(projections):.0f} - {max(projections):.0f}")
        
        # Tier analysis
        tier_analysis = {
            'Championship (7500+)': [d for d in complete_data if d['preseason_projection'] >= 7500],
            'Elite (7000-7499)': [d for d in complete_data if 7000 <= d['preseason_projection'] < 7500],
            'Strong (6500-6999)': [d for d in complete_data if 6500 <= d['preseason_projection'] < 7000],
            'Average (6000-6499)': [d for d in complete_data if 6000 <= d['preseason_projection'] < 6500],
            'Below Average (<6000)': [d for d in complete_data if d['preseason_projection'] < 6000],
        }
        
        print(f"\nTIER PERFORMANCE:")
        for tier_name, tier_data in tier_analysis.items():
            if tier_data:
                avg_rank = np.mean([d['final_rank'] for d in tier_data])
                top_4_pct = len([d for d in tier_data if d['final_rank'] <= 4]) / len(tier_data) * 100
                print(f"{tier_name}: {len(tier_data)} teams, avg rank {avg_rank:.1f}, {top_4_pct:.0f}% top-4 finish")

def save_results_to_json():
    """Save results to JSON for use in web interface."""
    
    results = combine_projections_and_rankings()
    
    # Save to JSON file
    output_file = 'html_reports/data/historical_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nHistorical analysis saved to: {output_file}")

def main():
    """Main execution function."""
    print("=== EXTRACTING HISTORICAL TEAM ANALYSIS ===")
    
    # Print the analysis
    print_historical_analysis()
    
    # Save to JSON
    save_results_to_json()

if __name__ == "__main__":
    main()