#!/usr/bin/env python3
"""
Create advanced player analysis tool with regression models for auction years (2016-2024).
Analyzes player value, performance prediction, and identifies undervalued/overvalued players.
"""

import json
import os
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def load_auction_data():
    """Load all auction year data (2016-2024)."""
    
    print("=== LOADING AUCTION YEAR DATA (2016-2024) ===\n")
    
    all_picks = []
    auction_years = list(range(2016, 2025))
    
    for year in auction_years:
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            with open(draft_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            picks = data.get('picks', [])
            print(f"Loaded {year}: {len(picks)} picks")
            
            for pick in picks:
                pick['year'] = year
                all_picks.append(pick)
        else:
            print(f"Missing {year}: File not found")
    
    print(f"\nTotal auction picks loaded: {len(all_picks)}")
    return all_picks

def load_nba_performance_data():
    """Load NBA performance data for analysis years."""
    
    print("\n=== LOADING NBA PERFORMANCE DATA ===\n")
    
    all_stats = []
    auction_years = list(range(2016, 2025))
    
    for year in auction_years:
        stats_file = f'historical_nba_stats/{year}/fantasy_relevant_stats.csv'
        if os.path.exists(stats_file):
            df = pd.read_csv(stats_file)
            df['year'] = year
            all_stats.append(df)
            print(f"Loaded {year}: {len(df)} player seasons")
        else:
            print(f"Missing {year}: Stats file not found")
    
    if all_stats:
        combined_stats = pd.concat(all_stats, ignore_index=True)
        print(f"\nTotal NBA player seasons: {len(combined_stats)}")
        return combined_stats
    else:
        print("No NBA stats found!")
        return pd.DataFrame()

def merge_draft_and_performance():
    """Merge draft data with performance data."""
    
    print("\n=== MERGING DRAFT AND PERFORMANCE DATA ===\n")
    
    # Load data
    draft_picks = load_auction_data()
    nba_stats = load_nba_performance_data()
    
    if nba_stats.empty:
        print("No NBA stats available for analysis")
        return pd.DataFrame()
    
    # Convert draft picks to DataFrame
    draft_df = pd.DataFrame(draft_picks)
    
    # Load player mapping
    mapping_file = 'historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json'
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            yahoo_to_nba = json.load(f)
        print(f"Loaded player mapping: {len(yahoo_to_nba)} mappings")
    else:
        yahoo_to_nba = {}
        print("No player mapping found")
    
    # Merge datasets
    merged_data = []
    
    for _, pick in draft_df.iterrows():
        yahoo_id = str(pick['player_id'])
        year = pick['year']
        
        # Get NBA player ID
        nba_mapping = yahoo_to_nba.get(yahoo_id)
        if not nba_mapping or 'nba_id' not in nba_mapping:
            continue
        
        nba_id = nba_mapping['nba_id']
        
        # Find matching NBA stats
        player_stats = nba_stats[
            (nba_stats['personId'] == int(nba_id)) & 
            (nba_stats['year'] == year)
        ]
        
        if not player_stats.empty:
            stats = player_stats.iloc[0]
            
            # Create merged record
            merged_record = {
                'year': year,
                'player_name': pick['player_name'],
                'yahoo_id': yahoo_id,
                'nba_id': nba_id,
                'draft_cost': pick['draft_cost'],
                'pick_number': pick['pick_number'],
                'fantasy_team': pick['fantasy_team'],
                # NBA stats (using correct column names)
                'games_played': stats.get('games_played', 0),
                'ppg': stats.get('points_per_game', 0),
                'rpg': stats.get('rebounds_per_game', 0),
                'apg': stats.get('assists_per_game', 0),
                'fg_pct': stats.get('field_goal_percentage', 0),
                'ft_pct': stats.get('free_throw_percentage', 0),
                'threepm_pg': stats.get('threepointers_per_game', 0),
                'stl_pg': stats.get('steals_per_game', 0),
                'blk_pg': stats.get('blocks_per_game', 0),
                'to_pg': stats.get('turnovers_per_game', 0),
                # Fantasy points calculation
                'fantasy_points': (
                    stats.get('points_per_game', 0) + 
                    stats.get('rebounds_per_game', 0) + 
                    stats.get('assists_per_game', 0) + 
                    stats.get('steals_per_game', 0) + 
                    stats.get('blocks_per_game', 0) + 
                    stats.get('threepointers_per_game', 0) - 
                    stats.get('turnovers_per_game', 0)
                )
            }
            
            # Calculate value score
            if pick['draft_cost'] > 0:
                merged_record['value_score'] = merged_record['fantasy_points'] / pick['draft_cost'] * 10
            else:
                merged_record['value_score'] = 0
            
            merged_data.append(merged_record)
    
    merged_df = pd.DataFrame(merged_data)
    print(f"Successfully merged {len(merged_df)} player-seasons")
    print(f"Coverage: {len(merged_df)} / {len(draft_df)} = {len(merged_df)/len(draft_df)*100:.1f}%")
    
    return merged_df

def build_prediction_models(df):
    """Build regression models to predict player performance and value."""
    
    print("\n=== BUILDING PREDICTION MODELS ===\n")
    
    if df.empty:
        return {}
    
    # Prepare features for modeling
    feature_columns = ['draft_cost', 'pick_number', 'games_played', 'ppg', 'rpg', 'apg', 'fg_pct', 'ft_pct', 'threepm_pg', 'stl_pg', 'blk_pg', 'to_pg']
    target_columns = ['fantasy_points', 'value_score']
    
    # Remove rows with missing data
    model_df = df[feature_columns + target_columns].dropna()
    
    if len(model_df) < 20:
        print("Insufficient data for modeling")
        return {}
    
    print(f"Using {len(model_df)} complete records for modeling")
    
    models = {}
    
    for target in target_columns:
        print(f"\nBuilding model for {target}...")
        
        # Prepare data
        X = model_df[feature_columns]
        y = model_df[target]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train models
        linear_model = LinearRegression()
        ridge_model = Ridge(alpha=1.0)
        
        linear_model.fit(X_train_scaled, y_train)
        ridge_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        linear_pred = linear_model.predict(X_test_scaled)
        ridge_pred = ridge_model.predict(X_test_scaled)
        
        linear_r2 = r2_score(y_test, linear_pred)
        ridge_r2 = r2_score(y_test, ridge_pred)
        
        linear_mse = mean_squared_error(y_test, linear_pred)
        ridge_mse = mean_squared_error(y_test, ridge_pred)
        
        print(f"  Linear Regression - R²: {linear_r2:.3f}, MSE: {linear_mse:.3f}")
        print(f"  Ridge Regression - R²: {ridge_r2:.3f}, MSE: {ridge_mse:.3f}")
        
        # Choose best model
        best_model = ridge_model if ridge_r2 > linear_r2 else linear_model
        best_r2 = ridge_r2 if ridge_r2 > linear_r2 else linear_r2
        
        # Feature importance (coefficients)
        coefficients = best_model.coef_
        feature_importance = dict(zip(feature_columns, coefficients))
        
        models[target] = {
            'model': best_model,
            'scaler': scaler,
            'r2_score': best_r2,
            'feature_importance': feature_importance,
            'feature_columns': feature_columns
        }
    
    return models

def analyze_player_patterns(df):
    """Analyze patterns in player values and performance."""
    
    print("\n=== ANALYZING PLAYER PATTERNS ===\n")
    
    if df.empty:
        return {}
    
    # Group by player to track multi-year performance
    player_analysis = defaultdict(lambda: {
        'years': [],
        'draft_costs': [],
        'value_scores': [],
        'fantasy_points': [],
        'total_drafts': 0,
        'avg_cost': 0,
        'avg_value': 0,
        'consistency_score': 0
    })
    
    for _, row in df.iterrows():
        player_name = row['player_name']
        
        player_analysis[player_name]['years'].append(row['year'])
        player_analysis[player_name]['draft_costs'].append(row['draft_cost'])
        player_analysis[player_name]['value_scores'].append(row['value_score'])
        player_analysis[player_name]['fantasy_points'].append(row['fantasy_points'])
        player_analysis[player_name]['total_drafts'] += 1
    
    # Calculate aggregated metrics
    for player, data in player_analysis.items():
        data['avg_cost'] = np.mean(data['draft_costs'])
        data['avg_value'] = np.mean(data['value_scores'])
        data['avg_fantasy_points'] = np.mean(data['fantasy_points'])
        
        # Consistency score (inverse of coefficient of variation)
        if len(data['value_scores']) > 1 and np.std(data['value_scores']) > 0:
            cv = np.std(data['value_scores']) / np.mean(data['value_scores'])
            data['consistency_score'] = 1 / (1 + cv)  # Higher is more consistent
        else:
            data['consistency_score'] = 1.0
    
    # Identify patterns
    patterns = {
        'undervalued_players': [],
        'overvalued_players': [],
        'consistent_performers': [],
        'high_variance_players': [],
        'bargain_picks': [],
        'expensive_busts': []
    }
    
    for player, data in player_analysis.items():
        if data['total_drafts'] >= 2:  # Only consider players drafted multiple times
            
            # Undervalued: High average value score
            if data['avg_value'] > 1.5:
                patterns['undervalued_players'].append((player, data['avg_value'], data['avg_cost']))
            
            # Overvalued: Low average value score with high cost
            elif data['avg_value'] < 0.8 and data['avg_cost'] > 20:
                patterns['overvalued_players'].append((player, data['avg_value'], data['avg_cost']))
            
            # Consistent: High consistency score
            if data['consistency_score'] > 0.8:
                patterns['consistent_performers'].append((player, data['consistency_score'], data['avg_value']))
            
            # High variance: Low consistency score
            elif data['consistency_score'] < 0.5:
                patterns['high_variance_players'].append((player, data['consistency_score'], data['avg_value']))
    
    # Bargain picks: Low cost, high value
    for _, row in df.iterrows():
        if row['draft_cost'] <= 10 and row['value_score'] > 2.0:
            patterns['bargain_picks'].append((row['player_name'], row['value_score'], row['draft_cost'], row['year']))
    
    # Expensive busts: High cost, low value
    for _, row in df.iterrows():
        if row['draft_cost'] >= 40 and row['value_score'] < 0.5:
            patterns['expensive_busts'].append((row['player_name'], row['value_score'], row['draft_cost'], row['year']))
    
    # Sort patterns
    patterns['undervalued_players'].sort(key=lambda x: x[1], reverse=True)
    patterns['overvalued_players'].sort(key=lambda x: x[1])
    patterns['consistent_performers'].sort(key=lambda x: x[1], reverse=True)
    patterns['bargain_picks'].sort(key=lambda x: x[1], reverse=True)
    patterns['expensive_busts'].sort(key=lambda x: x[1])
    
    print(f"Found {len(patterns['undervalued_players'])} undervalued players")
    print(f"Found {len(patterns['overvalued_players'])} overvalued players")
    print(f"Found {len(patterns['consistent_performers'])} consistent performers")
    print(f"Found {len(patterns['bargain_picks'])} bargain picks")
    print(f"Found {len(patterns['expensive_busts'])} expensive busts")
    
    return patterns

def create_player_analysis_page():
    """Create the comprehensive player analysis HTML page."""
    
    print("\n=== CREATING PLAYER ANALYSIS PAGE ===\n")
    
    # Load and process data
    merged_df = merge_draft_and_performance()
    
    if merged_df.empty:
        print("No data available for analysis")
        return False
    
    # Build prediction models
    models = build_prediction_models(merged_df)
    
    # Analyze patterns
    patterns = analyze_player_patterns(merged_df)
    
    # Load CSS
    try:
        with open('html_reports/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
    except:
        css_content = "/* CSS file not found */"
    
    # Create HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Analysis - Auction Years (2016-2024)</title>
    <style>
{css_content}

/* Additional player analysis styles */
.analysis-section {{
    background: white;
    border-radius: 10px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.model-metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}}

.metric-card {{
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}}

.metric-value {{
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 5px;
}}

.metric-label {{
    font-size: 0.9em;
    opacity: 0.9;
}}

.player-list {{
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e9ecef;
    border-radius: 5px;
}}

.player-item {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
}}

.player-item:hover {{
    background-color: #f8f9fa;
}}

.player-item:last-child {{
    border-bottom: none;
}}

.player-name {{
    font-weight: bold;
    color: #333;
}}

.player-stats {{
    display: flex;
    gap: 15px;
    font-size: 0.9em;
    color: #666;
}}

.value-high {{
    color: #28a745;
    font-weight: bold;
}}

.value-low {{
    color: #dc3545;
    font-weight: bold;
}}

.value-medium {{
    color: #ffc107;
    font-weight: bold;
}}

.insights-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}}

.insight-card {{
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    border-left: 4px solid #667eea;
}}

.insight-title {{
    font-size: 1.2em;
    font-weight: bold;
    color: #333;
    margin-bottom: 15px;
}}

.data-summary {{
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin: 20px 0;
}}

.summary-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
    margin-top: 15px;
}}

.summary-stat {{
    text-align: center;
}}

.summary-number {{
    font-size: 1.8em;
    font-weight: bold;
    display: block;
}}

.summary-label {{
    font-size: 0.9em;
    opacity: 0.9;
    margin-top: 5px;
}}

    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <!-- Page Header -->
            <div class="page-header">
                <h1>📈 Advanced Player Analysis</h1>
                <p>Auction Years Performance & Value Analysis (2016-2024)</p>
            </div>
            
            <!-- Data Summary -->
            <div class="data-summary">
                <h3 style="margin-bottom: 15px;">📊 Analysis Coverage</h3>
                <div class="summary-stats">
                    <div class="summary-stat">
                        <span class="summary-number">{len(merged_df)}</span>
                        <div class="summary-label">Player-Seasons</div>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-number">{len(merged_df['player_name'].unique())}</span>
                        <div class="summary-label">Unique Players</div>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-number">9</span>
                        <div class="summary-label">Auction Years</div>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-number">{merged_df['draft_cost'].sum():,}</span>
                        <div class="summary-label">Total $ Spent</div>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-number">{merged_df['draft_cost'].mean():.0f}</span>
                        <div class="summary-label">Avg Draft Cost</div>
                    </div>
                    <div class="summary-stat">
                        <span class="summary-number">{merged_df['value_score'].mean():.2f}</span>
                        <div class="summary-label">Avg Value Score</div>
                    </div>
                </div>
            </div>
'''
    
    # Add prediction model results
    if models:
        html_content += '''
            <!-- Model Performance -->
            <div class="analysis-section">
                <h2>🤖 Prediction Model Performance</h2>
                <p>Machine learning models trained to predict player fantasy points and value scores based on historical data.</p>
                
                <div class="model-metrics">
        '''
        
        for target, model_data in models.items():
            r2_score = model_data['r2_score']
            html_content += f'''
                    <div class="metric-card">
                        <div class="metric-value">{r2_score:.3f}</div>
                        <div class="metric-label">{target.replace('_', ' ').title()} R² Score</div>
                    </div>
            '''
        
        html_content += '''
                </div>
                
                <h3>Key Model Insights:</h3>
                <ul>
                    <li><strong>R² Score</strong>: Measures how well the model explains the variance (1.0 = perfect prediction)</li>
                    <li><strong>Fantasy Points Model</strong>: Predicts total fantasy production based on stats and draft position</li>
                    <li><strong>Value Score Model</strong>: Predicts value relative to draft cost</li>
                    <li><strong>Features Used</strong>: Draft cost, pick number, games played, and all 9 fantasy stat categories</li>
                </ul>
            </div>
        '''
    
    # Add pattern analysis
    html_content += '''
            <!-- Pattern Analysis -->
            <div class="insights-grid">
    '''
    
    # Undervalued players
    if patterns.get('undervalued_players'):
        html_content += '''
                <div class="insight-card">
                    <div class="insight-title">💎 Most Undervalued Players</div>
                    <div class="player-list">
        '''
        
        for player, value, cost in patterns['undervalued_players'][:10]:
            html_content += f'''
                        <div class="player-item">
                            <div class="player-name">{player}</div>
                            <div class="player-stats">
                                <span class="value-high">{value:.2f}</span>
                                <span>${cost:.0f}</span>
                            </div>
                        </div>
            '''
        
        html_content += '''
                    </div>
                    <small>Players with consistently high value scores relative to their draft cost</small>
                </div>
        '''
    
    # Overvalued players
    if patterns.get('overvalued_players'):
        html_content += '''
                <div class="insight-card">
                    <div class="insight-title">💸 Most Overvalued Players</div>
                    <div class="player-list">
        '''
        
        for player, value, cost in patterns['overvalued_players'][:10]:
            html_content += f'''
                        <div class="player-item">
                            <div class="player-name">{player}</div>
                            <div class="player-stats">
                                <span class="value-low">{value:.2f}</span>
                                <span>${cost:.0f}</span>
                            </div>
                        </div>
            '''
        
        html_content += '''
                    </div>
                    <small>Expensive players who consistently underperform relative to cost</small>
                </div>
        '''
    
    # Consistent performers
    if patterns.get('consistent_performers'):
        html_content += '''
                <div class="insight-card">
                    <div class="insight-title">🎯 Most Consistent Performers</div>
                    <div class="player-list">
        '''
        
        for player, consistency, avg_value in patterns['consistent_performers'][:10]:
            html_content += f'''
                        <div class="player-item">
                            <div class="player-name">{player}</div>
                            <div class="player-stats">
                                <span>{consistency:.3f}</span>
                                <span class="value-medium">{avg_value:.2f}</span>
                            </div>
                        </div>
            '''
        
        html_content += '''
                    </div>
                    <small>Players with low variance in value scores year-over-year</small>
                </div>
        '''
    
    # Bargain picks
    if patterns.get('bargain_picks'):
        html_content += '''
                <div class="insight-card">
                    <div class="insight-title">🏆 Best Bargain Picks</div>
                    <div class="player-list">
        '''
        
        for player, value, cost, year in patterns['bargain_picks'][:10]:
            html_content += f'''
                        <div class="player-item">
                            <div class="player-name">{player} ({year})</div>
                            <div class="player-stats">
                                <span class="value-high">{value:.2f}</span>
                                <span>${cost:.0f}</span>
                            </div>
                        </div>
            '''
        
        html_content += '''
                    </div>
                    <small>Low-cost players (≤$10) who delivered exceptional value</small>
                </div>
        '''
    
    # Expensive busts
    if patterns.get('expensive_busts'):
        html_content += '''
                <div class="insight-card">
                    <div class="insight-title">💔 Biggest Expensive Busts</div>
                    <div class="player-list">
        '''
        
        for player, value, cost, year in patterns['expensive_busts'][:10]:
            html_content += f'''
                        <div class="player-item">
                            <div class="player-name">{player} ({year})</div>
                            <div class="player-stats">
                                <span class="value-low">{value:.2f}</span>
                                <span>${cost:.0f}</span>
                            </div>
                        </div>
            '''
        
        html_content += '''
                    </div>
                    <small>High-cost players (≥$40) who severely underperformed</small>
                </div>
        '''
    
    html_content += '''
            </div>
            
            <!-- Methodology -->
            <div class="analysis-section">
                <h2>📋 Analysis Methodology</h2>
                
                <h3>Value Score Calculation:</h3>
                <p><strong>Value Score = (Fantasy Points / Draft Cost) × 10</strong></p>
                <p>Where Fantasy Points = PPG + RPG + APG + STL + BLK + 3PM - TO</p>
                
                <h3>Classification Thresholds:</h3>
                <ul>
                    <li><strong>High Value:</strong> Score > 1.5 (green)</li>
                    <li><strong>Medium Value:</strong> Score 0.8-1.5 (yellow)</li>
                    <li><strong>Low Value:</strong> Score < 0.8 (red)</li>
                </ul>
                
                <h3>Machine Learning Models:</h3>
                <ul>
                    <li><strong>Algorithm:</strong> Ridge Regression with feature scaling</li>
                    <li><strong>Features:</strong> Draft cost, pick number, games played, and 9 fantasy categories</li>
                    <li><strong>Training Data:</strong> 80% of player-seasons for model training</li>
                    <li><strong>Validation:</strong> 20% held out for testing model accuracy</li>
                </ul>
                
                <h3>Pattern Analysis:</h3>
                <ul>
                    <li><strong>Undervalued/Overvalued:</strong> Based on multi-year average value scores</li>
                    <li><strong>Consistency:</strong> Inverse coefficient of variation (lower variance = higher consistency)</li>
                    <li><strong>Bargains:</strong> Cost ≤ $10 with value score > 2.0</li>
                    <li><strong>Busts:</strong> Cost ≥ $40 with value score < 0.5</li>
                </ul>
            </div>
            
            <!-- Data Coverage -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px; text-align: center;">
                <h4 style="color: #333; margin-bottom: 10px;">📈 Data Coverage</h4>
                <p style="color: #666; font-size: 0.9em;">
                    Analysis based on {len(merged_df)} player-seasons from auction years (2016-2024) • 
                    {len(merged_df['player_name'].unique())} unique players • 
                    Machine learning models with {models.get('fantasy_points', {}).get('r2_score', 0):.1%} accuracy
                </p>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Write the file
    output_file = 'html_reports/prod_ready/player_analysis.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Player analysis page created: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    # Save analysis data
    analysis_data = {
        'merged_data': merged_df.to_dict('records'),
        'patterns': patterns,
        'model_performance': {k: {'r2_score': v['r2_score']} for k, v in models.items()},
        'summary_stats': {
            'total_player_seasons': len(merged_df),
            'unique_players': len(merged_df['player_name'].unique()),
            'total_spending': int(merged_df['draft_cost'].sum()),
            'avg_draft_cost': float(merged_df['draft_cost'].mean()),
            'avg_value_score': float(merged_df['value_score'].mean())
        }
    }
    
    with open('html_reports/data/player_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print("Analysis data saved to: html_reports/data/player_analysis.json")
    
    return True

if __name__ == "__main__":
    try:
        create_player_analysis_page()
    except ImportError as e:
        print(f"Missing required library: {e}")
        print("Please install: pip install scikit-learn pandas numpy")
    except Exception as e:
        print(f"Error creating player analysis: {e}")
        import traceback
        traceback.print_exc()