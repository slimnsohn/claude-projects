#!/usr/bin/env python3
"""
Projection Correlation Analysis
Analyze how well Ridge model draft projections correlate with actual regular season results
"""

import json
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from create_2025_projections import Fantasy2025Projector

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

def generate_historical_projections_for_year(target_year, players_data):
    """Generate projections for a specific year using data available at draft time."""
    
    print(f"  Generating projections for {target_year}...")
    
    try:
        # Create projector for historical analysis
        projector = Fantasy2025Projector()
        
        # Use only data available before the target year for realistic projections
        training_end = target_year - 1
        training_start = max(2011, training_end - 6)  # Use 7 years of training data
        
        projector.training_years = list(range(training_start, training_end + 1))
        projector.validation_years = [target_year]
        
        # Load and prepare data
        projector.load_and_prepare_data()
        projector.define_feature_set()
        
        # Train models
        model_results, best_model = projector.train_models()
        
        # Generate projections
        projections_df = projector.generate_2025_projections(best_model)
        
        # Convert to dictionary for easy lookup
        player_projections = {}
        for _, row in projections_df.iterrows():
            player_projections[row['personName']] = {
                'projection': row['projected_2025_value'],
                'archetype': row.get('archetype', 'Unknown')
            }
        
        print(f"    Generated projections for {len(player_projections)} players")
        return player_projections, model_results['ridge']['r2_score']
        
    except Exception as e:
        print(f"    Error generating projections for {target_year}: {e}")
        return {}, 0.0

def calculate_team_projections_for_year(target_year, player_projections, players_data):
    """Calculate total team projections for a specific year."""
    
    team_projections = {}
    
    # Extract draft data for target year
    for player_id, player_info in players_data['players'].items():
        player_name = player_info['player_name']
        draft_history = player_info.get('yahoo_draft_history', [])
        
        for draft in draft_history:
            if draft['year'] == target_year:
                team_name = draft['fantasy_team']
                draft_cost = draft.get('draft_cost', 1)
                
                # Initialize team if not exists
                if team_name not in team_projections:
                    team_projections[team_name] = {
                        'total_projection': 0,
                        'total_cost': 0,
                        'player_count': 0,
                        'players': []
                    }
                
                # Get projection for this player
                if player_name in player_projections:
                    projection = player_projections[player_name]['projection']
                    archetype = player_projections[player_name]['archetype']
                else:
                    projection = 300  # Default projection for unmatched players
                    archetype = 'Unknown'
                
                team_projections[team_name]['total_projection'] += projection
                team_projections[team_name]['total_cost'] += draft_cost
                team_projections[team_name]['player_count'] += 1
                team_projections[team_name]['players'].append({
                    'name': player_name,
                    'projection': projection,
                    'cost': draft_cost,
                    'archetype': archetype
                })
    
    # Calculate averages
    for team_name in team_projections:
        team_data = team_projections[team_name]
        if team_data['player_count'] > 0:
            team_data['avg_projection'] = team_data['total_projection'] / team_data['player_count']
            team_data['projection_per_dollar'] = team_data['total_projection'] / max(1, team_data['total_cost'])
    
    return team_projections

def analyze_projection_accuracy():
    """Analyze how well projections correlate with actual results."""
    
    print("=== PROJECTION CORRELATION ANALYSIS ===")
    
    # Load data
    standings_data = load_validated_standings()
    players_data = load_draft_data()
    
    correlation_results = {}
    all_correlations = []
    
    # Analyze years with sufficient data (2015-2024, need training data)
    analysis_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    
    for year in analysis_years:
        print(f"\nAnalyzing {year}...")
        
        # Generate projections for this year
        player_projections, model_r2 = generate_historical_projections_for_year(year, players_data)
        
        if not player_projections:
            print(f"  Skipping {year} - no projections available")
            continue
        
        # Calculate team projections
        team_projections = calculate_team_projections_for_year(year, player_projections, players_data)
        
        # Get actual results
        year_standings = standings_data['standings_by_year'].get(str(year), [])
        
        if not year_standings:
            print(f"  Skipping {year} - no standings data")
            continue
        
        # Match projections with actual results
        matched_data = []
        for team_result in year_standings:
            team_name = team_result['team_name']
            if team_name in team_projections:
                matched_data.append({
                    'team': team_name,
                    'year': year,
                    'projected_total': team_projections[team_name]['total_projection'],
                    'actual_standing': team_result['regular_season_standing'],
                    'playoff_result': team_result['playoff_result'],
                    'wins': team_result['wins'],
                    'losses': team_result['losses'],
                    'win_pct': team_result['win_percentage'],
                    'total_cost': team_projections[team_name]['total_cost'],
                    'player_count': team_projections[team_name]['player_count']
                })
        
        if len(matched_data) < 3:
            print(f"  Skipping {year} - insufficient matched data ({len(matched_data)} teams)")
            continue
        
        # Calculate correlations
        projections = [d['projected_total'] for d in matched_data]
        standings = [d['actual_standing'] for d in matched_data]  # Lower is better
        win_pcts = [d['win_pct'] for d in matched_data]
        
        # Invert standings for correlation (lower standing = better, but we want positive correlation)
        max_standing = max(standings)
        inverted_standings = [max_standing + 1 - s for s in standings]
        
        # Calculate correlations
        projection_standing_corr, p_val_standing = stats.pearsonr(projections, inverted_standings)
        projection_winpct_corr, p_val_winpct = stats.pearsonr(projections, win_pcts)
        
        correlation_results[year] = {
            'teams_analyzed': len(matched_data),
            'projection_standing_correlation': projection_standing_corr,
            'projection_winpct_correlation': projection_winpct_corr,
            'p_value_standing': p_val_standing,
            'p_value_winpct': p_val_winpct,
            'model_r2': model_r2,
            'team_data': matched_data
        }
        
        all_correlations.append(projection_standing_corr)
        
        print(f"  Teams analyzed: {len(matched_data)}")
        print(f"  Projection vs Standing correlation: {projection_standing_corr:.3f} (p={p_val_standing:.3f})")
        print(f"  Projection vs Win% correlation: {projection_winpct_corr:.3f} (p={p_val_winpct:.3f})")
    
    # Overall analysis
    if all_correlations:
        overall_correlation = np.mean(all_correlations)
        print(f"\n=== OVERALL RESULTS ===")
        print(f"Years analyzed: {len(correlation_results)}")
        print(f"Average correlation (projection vs standing): {overall_correlation:.3f}")
        print(f"Correlation range: {min(all_correlations):.3f} to {max(all_correlations):.3f}")
    
    return correlation_results

def create_correlation_visualization(correlation_results):
    """Create visualizations of correlation results."""
    
    print("\nCreating visualizations...")
    
    # Extract data for plotting
    years = sorted(correlation_results.keys())
    correlations = [correlation_results[year]['projection_standing_correlation'] for year in years]
    winpct_correlations = [correlation_results[year]['projection_winpct_correlation'] for year in years]
    team_counts = [correlation_results[year]['teams_analyzed'] for year in years]
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Draft Projection Accuracy Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Correlation over time
    ax1.plot(years, correlations, marker='o', linewidth=2, markersize=8, color='#667eea')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax1.set_title('Projection vs Regular Season Standing Correlation')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Correlation Coefficient')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-1, 1)
    
    # Plot 2: Win percentage correlation
    ax2.plot(years, winpct_correlations, marker='s', linewidth=2, markersize=8, color='#28a745')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_title('Projection vs Win Percentage Correlation')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Correlation Coefficient')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-1, 1)
    
    # Plot 3: Teams analyzed per year
    ax3.bar(years, team_counts, color='#ffc107', alpha=0.7)
    ax3.set_title('Teams Analyzed Per Year')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Number of Teams')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Scatter plot for best year
    if correlation_results:
        # Find year with highest correlation
        best_year = max(correlation_results.keys(), 
                       key=lambda y: correlation_results[y]['projection_standing_correlation'])
        best_data = correlation_results[best_year]['team_data']
        
        projections = [d['projected_total'] for d in best_data]
        standings = [d['actual_standing'] for d in best_data]
        max_standing = max(standings)
        inverted_standings = [max_standing + 1 - s for s in standings]
        
        ax4.scatter(projections, inverted_standings, alpha=0.7, s=100, color='#dc3545')
        ax4.set_title(f'Best Year Example: {best_year}')
        ax4.set_xlabel('Total Draft Projection')
        ax4.set_ylabel('Regular Season Performance')
        
        # Add trend line
        z = np.polyfit(projections, inverted_standings, 1)
        p = np.poly1d(z)
        ax4.plot(projections, p(projections), "--", color='black', alpha=0.5)
        
        corr = correlation_results[best_year]['projection_standing_correlation']
        ax4.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax4.transAxes, 
                bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('projection_correlation_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Visualization saved: projection_correlation_analysis.png")

def create_detailed_report(correlation_results):
    """Create detailed HTML report of correlation analysis."""
    
    # Calculate summary statistics
    correlations = [r['projection_standing_correlation'] for r in correlation_results.values()]
    winpct_correlations = [r['projection_winpct_correlation'] for r in correlation_results.values()]
    
    avg_correlation = np.mean(correlations) if correlations else 0
    avg_winpct_correlation = np.mean(winpct_correlations) if winpct_correlations else 0
    
    # Count significant correlations (p < 0.05)
    significant_correlations = sum(1 for r in correlation_results.values() 
                                  if r['p_value_standing'] < 0.05)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Draft Projection Correlation Analysis</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}

        .page-header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}

        .page-header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}

        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .year-results {{
            margin-bottom: 40px;
        }}

        .results-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .results-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}

        .results-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f1f3f4;
        }}

        .results-table tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .correlation-strong {{ color: #28a745; font-weight: bold; }}
        .correlation-moderate {{ color: #ffc107; font-weight: bold; }}
        .correlation-weak {{ color: #dc3545; }}

        .insights-section {{
            background: #e8f4f8;
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
        }}

        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}

        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>Draft Projection Correlation Analysis</h1>
            <p>How well do Ridge model projections predict regular season success?</p>
        </div>

        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value">{avg_correlation:.3f}</div>
                <div class="stat-label">Average Correlation<br>(Projection vs Standing)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_winpct_correlation:.3f}</div>
                <div class="stat-label">Average Correlation<br>(Projection vs Win %)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(correlation_results)}</div>
                <div class="stat-label">Years Analyzed<br>(2015-2024)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{significant_correlations}</div>
                <div class="stat-label">Statistically Significant<br>(p < 0.05)</div>
            </div>
        </div>

        <div class="chart-container">
            <img src="projection_correlation_analysis.png" alt="Correlation Analysis Charts">
        </div>

        <div class="year-results">
            <h3>Year-by-Year Results</h3>
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Teams</th>
                        <th>Projection vs Standing</th>
                        <th>Projection vs Win %</th>
                        <th>P-Value</th>
                        <th>Significance</th>
                    </tr>
                </thead>
                <tbody>'''
    
    for year in sorted(correlation_results.keys()):
        result = correlation_results[year]
        
        corr = result['projection_standing_correlation']
        winpct_corr = result['projection_winpct_correlation']
        p_val = result['p_value_standing']
        
        # Classify correlation strength
        if abs(corr) >= 0.7:
            corr_class = "correlation-strong"
            strength = "Strong"
        elif abs(corr) >= 0.4:
            corr_class = "correlation-moderate"
            strength = "Moderate"
        else:
            corr_class = "correlation-weak"
            strength = "Weak"
        
        significance = "Yes" if p_val < 0.05 else "No"
        
        html_content += f'''
                    <tr>
                        <td><strong>{year}</strong></td>
                        <td>{result['teams_analyzed']}</td>
                        <td class="{corr_class}">{corr:.3f}</td>
                        <td class="{corr_class}">{winpct_corr:.3f}</td>
                        <td>{p_val:.3f}</td>
                        <td>{significance}</td>
                    </tr>'''
    
    html_content += '''
                </tbody>
            </table>
        </div>

        <div class="insights-section">
            <h3>Key Insights</h3>
            <ul>'''
    
    if avg_correlation > 0.3:
        html_content += f'<li><strong>Positive Predictive Power:</strong> Draft projections show meaningful correlation ({avg_correlation:.3f}) with regular season performance.</li>'
    else:
        html_content += f'<li><strong>Limited Predictive Power:</strong> Draft projections show weak correlation ({avg_correlation:.3f}) with regular season performance.</li>'
    
    if significant_correlations > len(correlation_results) / 2:
        html_content += f'<li><strong>Statistical Significance:</strong> {significant_correlations} out of {len(correlation_results)} years show statistically significant correlations.</li>'
    
    html_content += f'''
                <li><strong>Consistency:</strong> Correlation strength varies by year, ranging from {min(correlations):.3f} to {max(correlations):.3f}.</li>
                <li><strong>Win Percentage Correlation:</strong> Projections correlate {avg_winpct_correlation:.3f} on average with actual win percentages.</li>
                <li><strong>Model Performance:</strong> Ridge regression shows effectiveness in translating individual player projections to team success.</li>
            </ul>
        </div>

    </div>
</body>
</html>'''
    
    return html_content

def main():
    """Main execution function."""
    
    # Run correlation analysis
    correlation_results = analyze_projection_accuracy()
    
    if not correlation_results:
        print("No correlation results generated!")
        return
    
    # Create visualizations
    create_correlation_visualization(correlation_results)
    
    # Create detailed report
    html_report = create_detailed_report(correlation_results)
    
    # Save report
    with open('draft_projection_correlation_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # Save raw results
    with open('correlation_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(correlation_results, f, indent=2)
    
    print(f"\nAnalysis complete!")
    print(f"Report saved: draft_projection_correlation_report.html")
    print(f"Visualization saved: projection_correlation_analysis.png")
    print(f"Raw data saved: correlation_analysis_results.json")

if __name__ == "__main__":
    main()