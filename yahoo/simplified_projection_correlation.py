#!/usr/bin/env python3
"""
Simplified Projection Correlation Analysis
Focus on correlating draft projections with regular season results
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def load_validated_standings():
    """Load the validated standings data."""
    with open('validated_data_archive/analysis_ready_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_draft_data():
    """Load draft history data."""
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def estimate_player_fantasy_value(player_info, target_year):
    """Estimate player fantasy value using previous year stats."""
    
    seasons = player_info.get('seasons', {})
    
    # Use stats from year before target (available at draft time)
    prev_year = target_year - 1
    prev_stats = seasons.get(str(prev_year))
    
    if not prev_stats:
        prev_stats = seasons.get(str(prev_year - 1))  # Try 2 years back
    
    if not prev_stats:
        return 300  # Default value
    
    try:
        # Calculate fantasy value based on 9-category contribution
        games = max(prev_stats.get('games_played', 50), 20)
        multiplier = min(70 / games, 2.0)  # Adjust for games played
        
        # Category values (rough fantasy point estimation)
        fg_pct = prev_stats.get('fg_pct', 0.45) * 100
        ft_pct = prev_stats.get('ft_pct', 0.75) * 100
        threepm = prev_stats.get('threepm_pg', 0) * multiplier * 20
        pts = prev_stats.get('pts_pg', 0) * multiplier * 3
        reb = prev_stats.get('reb_pg', 0) * multiplier * 10
        ast = prev_stats.get('ast_pg', 0) * multiplier * 12
        stl = prev_stats.get('stl_pg', 0) * multiplier * 30
        blk = prev_stats.get('blk_pg', 0) * multiplier * 30
        to_penalty = prev_stats.get('to_pg', 0) * multiplier * -20
        
        total_value = fg_pct + ft_pct + threepm + pts + reb + ast + stl + blk + to_penalty
        
        # Apply games played bonus/penalty
        if games < 40:
            total_value *= 0.7
        elif games > 75:
            total_value *= 1.15
        
        return max(200, min(900, int(total_value)))
        
    except:
        return 300

def calculate_team_projections_for_year(target_year, players_data):
    """Calculate team projections using player value estimates."""
    
    print(f"  Calculating team projections for {target_year}...")
    
    team_projections = {}
    
    # Process all draft picks for this year
    for player_id, player_info in players_data['players'].items():
        player_name = player_info['player_name']
        draft_history = player_info.get('yahoo_draft_history', [])
        
        for draft in draft_history:
            if draft['year'] == target_year:
                team_name = draft['fantasy_team']
                draft_cost = draft.get('draft_cost', 1)
                
                # Initialize team
                if team_name not in team_projections:
                    team_projections[team_name] = {
                        'total_projection': 0,
                        'total_cost': 0,
                        'player_count': 0,
                        'players': []
                    }
                
                # Estimate player value
                player_value = estimate_player_fantasy_value(player_info, target_year)
                
                team_projections[team_name]['total_projection'] += player_value
                team_projections[team_name]['total_cost'] += draft_cost
                team_projections[team_name]['player_count'] += 1
                team_projections[team_name]['players'].append({
                    'name': player_name,
                    'projection': player_value,
                    'cost': draft_cost
                })
    
    print(f"    Calculated projections for {len(team_projections)} teams")
    return team_projections

def analyze_yearly_correlation(year, team_projections, year_standings):
    """Analyze correlation for a single year."""
    
    # Match projections with standings
    matched_data = []
    
    for team_result in year_standings:
        team_name = team_result['team_name']
        if team_name in team_projections:
            matched_data.append({
                'team': team_name,
                'projected_total': team_projections[team_name]['total_projection'],
                'actual_standing': team_result['regular_season_standing'],
                'wins': team_result['wins'],
                'losses': team_result['losses'],
                'win_pct': team_result['win_percentage'],
                'playoff_result': team_result['playoff_result'],
                'total_cost': team_projections[team_name]['total_cost'],
                'roster_size': team_projections[team_name]['player_count']
            })
    
    if len(matched_data) < 3:
        return None
    
    # Calculate correlations
    projections = [d['projected_total'] for d in matched_data]
    standings = [d['actual_standing'] for d in matched_data]
    win_pcts = [d['win_pct'] for d in matched_data]
    
    # Invert standings (lower standing = better performance)
    max_standing = max(standings)
    inverted_standings = [max_standing + 1 - s for s in standings]
    
    # Pearson correlations
    try:
        proj_standing_corr, p_val_standing = stats.pearsonr(projections, inverted_standings)
        proj_winpct_corr, p_val_winpct = stats.pearsonr(projections, win_pcts)
    except:
        return None
    
    return {
        'year': year,
        'teams_analyzed': len(matched_data),
        'projection_standing_correlation': proj_standing_corr,
        'projection_winpct_correlation': proj_winpct_corr,
        'p_value_standing': p_val_standing,
        'p_value_winpct': p_val_winpct,
        'team_data': matched_data,
        'avg_projection': np.mean(projections),
        'projection_std': np.std(projections),
        'avg_win_pct': np.mean(win_pcts)
    }

def run_correlation_analysis():
    """Run the full correlation analysis."""
    
    print("=== SIMPLIFIED PROJECTION CORRELATION ANALYSIS ===")
    
    # Load data
    standings_data = load_validated_standings()
    players_data = load_draft_data()
    
    correlation_results = {}
    
    # Analyze years 2015-2024 (need some historical data for projections)
    analysis_years = list(range(2015, 2025))
    
    for year in analysis_years:
        print(f"\nAnalyzing {year}...")
        
        # Get standings for this year
        year_standings = standings_data['standings_by_year'].get(str(year), [])
        if not year_standings:
            print(f"  No standings data for {year}")
            continue
        
        # Calculate team projections
        team_projections = calculate_team_projections_for_year(year, players_data)
        
        if not team_projections:
            print(f"  No projection data for {year}")
            continue
        
        # Analyze correlation
        year_result = analyze_yearly_correlation(year, team_projections, year_standings)
        
        if year_result:
            correlation_results[year] = year_result
            
            print(f"  Teams analyzed: {year_result['teams_analyzed']}")
            print(f"  Projection vs Standing correlation: {year_result['projection_standing_correlation']:.3f}")
            print(f"  Projection vs Win% correlation: {year_result['projection_winpct_correlation']:.3f}")
            print(f"  Statistical significance: {year_result['p_value_standing']:.3f}")
        else:
            print(f"  Unable to analyze correlations for {year}")
    
    return correlation_results

def create_simple_visualization(correlation_results):
    """Create simple visualization of results."""
    
    if not correlation_results:
        return
    
    years = sorted(correlation_results.keys())
    standing_corrs = [correlation_results[y]['projection_standing_correlation'] for y in years]
    winpct_corrs = [correlation_results[y]['projection_winpct_correlation'] for y in years]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Draft Projection Correlation Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Standing correlations
    ax1.plot(years, standing_corrs, marker='o', linewidth=2, markersize=8, color='#667eea')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax1.axhline(y=0.5, color='green', linestyle=':', alpha=0.5, label='Strong correlation')
    ax1.set_title('Projection vs Regular Season Standing')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Correlation Coefficient')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-1, 1)
    ax1.legend()
    
    # Plot 2: Win percentage correlations
    ax2.plot(years, winpct_corrs, marker='s', linewidth=2, markersize=8, color='#28a745')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.axhline(y=0.5, color='green', linestyle=':', alpha=0.5, label='Strong correlation')
    ax2.set_title('Projection vs Win Percentage')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Correlation Coefficient')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-1, 1)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('simple_projection_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved: simple_projection_correlation.png")

def create_summary_report(correlation_results):
    """Create summary report of findings."""
    
    if not correlation_results:
        print("No results to summarize!")
        return
    
    # Calculate summary statistics
    standing_corrs = [r['projection_standing_correlation'] for r in correlation_results.values()]
    winpct_corrs = [r['projection_winpct_correlation'] for r in correlation_results.values()]
    p_values = [r['p_value_standing'] for r in correlation_results.values()]
    
    avg_standing_corr = np.mean(standing_corrs)
    avg_winpct_corr = np.mean(winpct_corrs)
    significant_years = sum(1 for p in p_values if p < 0.05)
    
    # Best and worst years
    best_year = max(correlation_results.keys(), key=lambda y: correlation_results[y]['projection_standing_correlation'])
    worst_year = min(correlation_results.keys(), key=lambda y: correlation_results[y]['projection_standing_correlation'])
    
    print(f"\n=== CORRELATION ANALYSIS SUMMARY ===")
    print(f"Years analyzed: {len(correlation_results)}")
    print(f"Average projection vs standing correlation: {avg_standing_corr:.3f}")
    print(f"Average projection vs win% correlation: {avg_winpct_corr:.3f}")
    print(f"Statistically significant years (p<0.05): {significant_years}/{len(correlation_results)}")
    print(f"Correlation range: {min(standing_corrs):.3f} to {max(standing_corrs):.3f}")
    print(f"Best correlation year: {best_year} ({correlation_results[best_year]['projection_standing_correlation']:.3f})")
    print(f"Worst correlation year: {worst_year} ({correlation_results[worst_year]['projection_standing_correlation']:.3f})")
    
    # Interpretation
    print(f"\n=== INTERPRETATION ===")
    if avg_standing_corr > 0.5:
        print("✓ Strong predictive power: Draft projections show strong correlation with actual results")
    elif avg_standing_corr > 0.3:
        print("~ Moderate predictive power: Draft projections show meaningful correlation with results")
    else:
        print("✗ Weak predictive power: Draft projections show limited correlation with results")
    
    if significant_years > len(correlation_results) // 2:
        print("✓ Results are statistically reliable across multiple years")
    else:
        print("~ Statistical significance varies by year")
    
    # Save detailed results
    with open('projection_correlation_results.json', 'w', encoding='utf-8') as f:
        json.dump(correlation_results, f, indent=2)
    
    print(f"\nDetailed results saved: projection_correlation_results.json")

def main():
    """Main execution."""
    
    # Run correlation analysis
    correlation_results = run_correlation_analysis()
    
    if correlation_results:
        # Create visualization
        create_simple_visualization(correlation_results)
        
        # Create summary report
        create_summary_report(correlation_results)
    else:
        print("No correlation analysis results generated!")

if __name__ == "__main__":
    main()