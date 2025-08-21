#!/usr/bin/env python3
"""
2025 Fantasy Basketball Projections

Uses machine learning on historical data to project 2025 fantasy values.
Training: 2011-2017 (7 years)
Validation: 2018-2024 (7 years)
Prediction: Apply to 2024 data for 2025 projections
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
import json
import warnings
from fantasy_basketball_analyzer import FantasyBasketballAnalyzer

warnings.filterwarnings('ignore')

class Fantasy2025Projector:
    def __init__(self):
        """Initialize the 2025 projection system."""
        self.analyzer = FantasyBasketballAnalyzer()
        self.training_years = list(range(2011, 2018))  # 2011-2017
        self.validation_years = list(range(2018, 2025))  # 2018-2024
        self.models = {}
        self.scalers = {}
        self.features = []
        self.training_data = None
        self.validation_data = None
        
    def load_and_prepare_data(self):
        """Load data and prepare features for modeling."""
        print("Loading historical data for projection modeling...")
        
        # Load analyzer data
        self.analyzer.load_data(min_games=30)
        self.analyzer.normalize_stats()
        
        data = self.analyzer.normalized_data.copy()
        
        # Add additional features for prediction
        data = self.engineer_features(data)
        
        # Split into training and validation
        self.training_data = data[data['season'].isin(self.training_years)].copy()
        self.validation_data = data[data['season'].isin(self.validation_years)].copy()
        
        print(f"Training data: {len(self.training_data)} player-seasons ({min(self.training_years)}-{max(self.training_years)})")
        print(f"Validation data: {len(self.validation_data)} player-seasons ({min(self.validation_years)}-{max(self.validation_years)})")
        
        return data
    
    def engineer_features(self, data):
        """Create predictive features for the model."""
        print("Engineering predictive features...")
        
        # Age estimation (rough)
        data['estimated_age'] = data['season'] - 1995  # Rough average birth year
        data['estimated_age'] = np.clip(data['estimated_age'], 18, 45)
        
        # Experience proxy (years since first season for each player)
        player_first_seasons = data.groupby('personName')['season'].min()
        data['experience'] = data.apply(lambda row: row['season'] - player_first_seasons[row['personName']], axis=1)
        
        # Games played efficiency
        data['games_efficiency'] = data['games_played'] / 82  # Percentage of season played
        
        # Performance trends (if player has multiple seasons)
        data = self.add_trend_features(data)
        
        # Advanced ratios
        data['usage_efficiency'] = data['points_per_game'] / (data['turnovers_per_game'] + 1)
        data['defensive_impact'] = data['steals_per_game'] + data['blocks_per_game']
        data['shooting_volume'] = data['threepointers_per_game'] + (data['points_per_game'] / 2)
        data['big_man_score'] = data['rebounds_per_game'] + data['blocks_per_game'] * 2
        data['guard_score'] = data['assists_per_game'] + data['steals_per_game'] + data['threepointers_per_game']
        
        # Consistency metrics (fantasy value relative to percentiles)
        data['consistency_score'] = data['fantasy_value'] / (data[['points_per_game_norm', 'rebounds_per_game_norm', 'assists_per_game_norm']].mean(axis=1) + 1)
        
        # Injury risk proxy (games played vs. expected)
        data['injury_risk'] = 82 - data['games_played']
        
        return data
    
    def add_trend_features(self, data):
        """Add year-over-year trend features."""
        print("Adding player trend features...")
        
        # Sort by player and season
        data = data.sort_values(['personName', 'season'])
        
        # Initialize trend columns
        trend_features = ['fantasy_value_trend', 'games_trend', 'efficiency_trend']
        for feature in trend_features:
            data[feature] = 0.0
        
        # Calculate trends for each player
        for player in data['personName'].unique():
            player_data = data[data['personName'] == player].sort_values('season')
            
            if len(player_data) > 1:
                # Fantasy value trend
                fantasy_diff = player_data['fantasy_value'].diff().fillna(0)
                games_diff = player_data['games_played'].diff().fillna(0)
                
                # Set trends
                data.loc[data['personName'] == player, 'fantasy_value_trend'] = fantasy_diff
                data.loc[data['personName'] == player, 'games_trend'] = games_diff
                
                # Efficiency trend (fantasy value per game)
                player_data['value_per_game'] = player_data['fantasy_value'] / (player_data['games_played'] + 1)
                efficiency_diff = player_data['value_per_game'].diff().fillna(0)
                data.loc[data['personName'] == player, 'efficiency_trend'] = efficiency_diff
        
        return data
    
    def define_feature_set(self):
        """Define the features to use for prediction."""
        self.features = [
            # Basic stats (normalized)
            'points_per_game_norm', 'rebounds_per_game_norm', 'assists_per_game_norm',
            'steals_per_game_norm', 'blocks_per_game_norm', 'threepointers_per_game_norm',
            'field_goal_percentage_norm', 'free_throw_percentage_norm', 'turnovers_per_game_norm',
            
            # Player characteristics
            'estimated_age', 'experience', 'games_efficiency',
            
            # Advanced metrics
            'usage_efficiency', 'defensive_impact', 'shooting_volume',
            'big_man_score', 'guard_score', 'consistency_score', 'injury_risk',
            
            # Trends
            'fantasy_value_trend', 'games_trend', 'efficiency_trend'
        ]
        
        print(f"Using {len(self.features)} features for prediction")
        return self.features
    
    def train_models(self):
        """Train multiple models and select the best performing."""
        print("Training prediction models...")
        
        X_train = self.training_data[self.features].fillna(0)
        y_train = self.training_data['fantasy_value']
        
        X_val = self.validation_data[self.features].fillna(0)
        y_val = self.validation_data['fantasy_value']
        
        # Scale features
        self.scalers['standard'] = StandardScaler()
        X_train_scaled = self.scalers['standard'].fit_transform(X_train)
        X_val_scaled = self.scalers['standard'].transform(X_val)
        
        # Define models to test
        model_configs = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=6),
            'ridge': Ridge(alpha=1.0)
        }
        
        # Train and evaluate models
        best_model = None
        best_score = -float('inf')
        model_results = {}
        
        for name, model in model_configs.items():
            print(f"\\nTraining {name}...")
            
            if name == 'ridge':
                # Ridge needs scaled features
                model.fit(X_train_scaled, y_train)
                val_pred = model.predict(X_val_scaled)
                train_pred = model.predict(X_train_scaled)
            else:
                # Tree models can use original features
                model.fit(X_train, y_train)
                val_pred = model.predict(X_val)
                train_pred = model.predict(X_train)
            
            # Calculate metrics
            train_r2 = r2_score(y_train, train_pred)
            val_r2 = r2_score(y_val, val_pred)
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            
            # Cross-validation score
            if name == 'ridge':
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            
            model_results[name] = {
                'model': model,
                'train_r2': train_r2,
                'val_r2': val_r2,
                'val_rmse': val_rmse,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
            
            print(f"  Train R²: {train_r2:.3f}")
            print(f"  Validation R²: {val_r2:.3f}")
            print(f"  Validation RMSE: {val_rmse:.3f}")
            print(f"  CV Score: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            
            # Select best model based on validation R²
            if val_r2 > best_score:
                best_score = val_r2
                best_model = name
        
        self.models = model_results
        print(f"\\nBest model: {best_model} (Validation R²: {best_score:.3f})")
        
        return model_results, best_model
    
    def analyze_feature_importance(self, model_name='random_forest'):
        """Analyze which features are most predictive."""
        print(f"\\nFeature importance analysis ({model_name}):")
        
        model = self.models[model_name]['model']
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models
            importances = model.feature_importances_
            feature_importance = list(zip(self.features, importances))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            print("\\nTop 10 most important features:")
            for i, (feature, importance) in enumerate(feature_importance[:10], 1):
                print(f"{i:2d}. {feature:25}: {importance:.4f}")
        
        elif hasattr(model, 'coef_'):
            # Linear models
            coefs = np.abs(model.coef_)
            feature_importance = list(zip(self.features, coefs))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            print("\\nTop 10 most important features (by coefficient magnitude):")
            for i, (feature, coef) in enumerate(feature_importance[:10], 1):
                print(f"{i:2d}. {feature:25}: {coef:.4f}")
        
        return feature_importance
    
    def generate_2025_projections(self, model_name='random_forest'):
        """Generate 2025 projections using 2024 data."""
        print(f"\\nGenerating 2025 projections using {model_name} model...")
        
        # Get 2024 data
        data_2024 = self.analyzer.normalized_data[
            self.analyzer.normalized_data['season'] == 2024
        ].copy()
        
        # Engineer features for 2024
        data_2024 = self.engineer_features(data_2024)
        
        # Prepare features
        X_2024 = data_2024[self.features].fillna(0)
        
        # Get model
        model = self.models[model_name]['model']
        
        # Make predictions
        if model_name == 'ridge':
            X_2024_scaled = self.scalers['standard'].transform(X_2024)
            predictions = model.predict(X_2024_scaled)
        else:
            predictions = model.predict(X_2024)
        
        # Add predictions to dataframe
        data_2024['projected_2025_value'] = predictions
        
        # Calculate projection confidence based on validation performance
        val_r2 = self.models[model_name]['val_r2']
        data_2024['projection_confidence'] = val_r2  # Same confidence for all players
        
        # Filter for players with meaningful projections
        projections = data_2024[
            (data_2024['games_played'] >= 30) &  # Played meaningful minutes
            (data_2024['projected_2025_value'] > 200)  # Projected fantasy relevance
        ].copy()
        
        # Sort by projected value
        projections = projections.sort_values('projected_2025_value', ascending=False)
        
        print(f"Generated projections for {len(projections)} players")
        
        return projections
    
    def analyze_projection_categories(self, projections):
        """Analyze projections by player categories."""
        print("\\nAnalyzing projection categories...")
        
        # Define player archetypes based on 2024 performance
        projections['archetype'] = 'Balanced'
        
        # Big men (high rebounds and blocks)
        big_men_mask = (
            (projections['rebounds_per_game_norm'] > 70) &
            (projections['blocks_per_game_norm'] > 60)
        )
        projections.loc[big_men_mask, 'archetype'] = 'Big Man'
        
        # Guards (high assists and steals)
        guard_mask = (
            (projections['assists_per_game_norm'] > 70) |
            (projections['steals_per_game_norm'] > 70)
        )
        projections.loc[guard_mask, 'archetype'] = 'Guard'
        
        # Shooters (high 3PM and good percentages)
        shooter_mask = (
            (projections['threepointers_per_game_norm'] > 75) &
            (projections['field_goal_percentage_norm'] > 50)
        )
        projections.loc[shooter_mask, 'archetype'] = 'Shooter'
        
        # Analyze by archetype
        print("\\nProjected 2025 value by player archetype:")
        for archetype in projections['archetype'].unique():
            archetype_data = projections[projections['archetype'] == archetype]
            avg_projection = archetype_data['projected_2025_value'].mean()
            count = len(archetype_data)
            print(f"  {archetype:10}: {count:3d} players, Avg projection: {avg_projection:.1f}")
        
        return projections
    
    def identify_breakout_candidates(self, projections):
        """Identify potential breakout candidates for 2025."""
        print("\\nIdentifying 2025 breakout candidates...")
        
        # Criteria for breakout candidates (more relaxed)
        breakout_criteria = (
            (projections['estimated_age'] < 30) &  # Young enough for improvement
            (projections['experience'] < 10) &      # Not veteran
            (projections['projected_2025_value'] > projections['fantasy_value'] * 1.05) &  # 5%+ projection increase
            (projections['games_efficiency'] > 0.4) &  # Decent availability
            (projections['projected_2025_value'] > 300)  # Meaningful fantasy relevance
        )
        
        breakouts = projections[breakout_criteria].copy()
        breakouts['projected_improvement'] = breakouts['projected_2025_value'] - breakouts['fantasy_value']
        breakouts = breakouts.sort_values('projected_improvement', ascending=False)
        
        print(f"Found {len(breakouts)} potential breakout candidates")
        
        return breakouts
    
    def create_projection_tiers(self, projections):
        """Create draft tiers based on projections."""
        print("\\nCreating 2025 draft tiers...")
        
        # Define tiers
        tiers = []
        
        # Tier 1: Elite (top 12)
        tier1 = projections.head(12).copy()
        tier1['tier'] = 'Tier 1 - Elite'
        tier1['tier_description'] = 'First round picks, league winners'
        tiers.append(tier1)
        
        # Tier 2: Very Good (next 24)
        tier2 = projections.iloc[12:36].copy()
        tier2['tier'] = 'Tier 2 - Very Good'
        tier2['tier_description'] = 'Second-third round, solid contributors'
        tiers.append(tier2)
        
        # Tier 3: Good (next 36)
        tier3 = projections.iloc[36:72].copy()
        tier3['tier'] = 'Tier 3 - Good'
        tier3['tier_description'] = 'Mid-round picks, reliable players'
        tiers.append(tier3)
        
        # Tier 4: Sleepers (next 48)
        tier4 = projections.iloc[72:120].copy()
        tier4['tier'] = 'Tier 4 - Sleepers'
        tier4['tier_description'] = 'Late round targets, upside plays'
        tiers.append(tier4)
        
        return tiers

def create_html_report(projector, projections, breakouts, tiers, model_results, best_model):
    """Create the HTML report for 2025 projections."""
    
    print("Creating HTML report...")
    
    # Calculate model performance summary
    best_model_info = model_results[best_model]
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Fantasy Basketball Projections</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

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
        }}

        .main-content {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
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
            background-clip: text;
            margin-bottom: 10px;
        }}

        .methodology {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }}

        .model-performance {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .projection-section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}

        .tier-container {{
            margin-bottom: 30px;
        }}

        .tier-header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 20px;
            border-radius: 10px 10px 0 0;
            font-weight: bold;
        }}

        .tier-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 0 0 10px 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .tier-table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}

        .tier-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f1f3f4;
        }}

        .tier-table tbody tr:hover {{
            background-color: #f8f9fa;
        }}

        .player-name {{
            font-weight: 600;
            color: #333;
        }}

        .projection-value {{
            font-weight: bold;
            color: #28a745;
        }}

        .improvement {{
            color: #17a2b8;
            font-weight: 500;
        }}

        .breakout-card {{
            background: linear-gradient(135deg, #fd7e14, #e83e8c);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .confidence-high {{ color: #28a745; font-weight: bold; }}
        .confidence-medium {{ color: #ffc107; font-weight: bold; }}
        .confidence-low {{ color: #dc3545; font-weight: bold; }}

        .archetype-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .archetype-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}

        .nav-links {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .nav-link {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
            margin: 0 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .nav-link:hover {{
            background: linear-gradient(135deg, #20c997, #17a2b8);
            transform: translateY(-2px);
        }}

        @media (max-width: 768px) {{
            .model-performance {{
                grid-template-columns: 1fr;
            }}
            
            .tier-table {{
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🔮 2025 Fantasy Basketball Projections</h1>
                <p>Machine Learning-Powered Draft Analysis</p>
            </div>

            <div class="nav-links">
                <a href="index.html" class="nav-link">🏠 Dashboard</a>
                <a href="simple_working.html" class="nav-link">👥 Player Database</a>
                <a href="owner_analysis.html" class="nav-link">📊 Owner Analysis</a>
            </div>

            <div class="methodology">
                <h3>📊 Methodology</h3>
                <p><strong>Training Data:</strong> 2011-2017 seasons (7 years) - {len(projector.training_data):,} player-seasons</p>
                <p><strong>Validation:</strong> 2018-2024 seasons (7 years) - {len(projector.validation_data):,} player-seasons</p>
                <p><strong>Best Model:</strong> {best_model.replace('_', ' ').title()} - Validated on unseen data</p>
                <p><strong>Features:</strong> {len(projector.features)} predictive variables including player stats, trends, age, and advanced metrics</p>
                <p><strong>Projections:</strong> Applied to 2024 performance to predict 2025 fantasy value</p>
            </div>

            <div class="model-performance">
                <div class="metric-card">
                    <div class="metric-value">{best_model_info['val_r2']:.3f}</div>
                    <div class="metric-label">Validation R²</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{best_model_info['val_rmse']:.1f}</div>
                    <div class="metric-label">Prediction RMSE</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(projections)}</div>
                    <div class="metric-label">Players Projected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(breakouts)}</div>
                    <div class="metric-label">Breakout Candidates</div>
                </div>
            </div>'''

    # Add breakout candidates section
    html_content += f'''
            <div class="projection-section">
                <div class="section-title">🚀 Top 2025 Breakout Candidates</div>
                <div class="breakout-card">
                    <h4>High-Upside Players Projected for Significant Improvement</h4>
                    <p>Based on age, experience, recent trends, and statistical projections</p>
                </div>
                
                <table class="tier-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>2024 Value</th>
                            <th>2025 Projection</th>
                            <th>Improvement</th>
                            <th>Age</th>
                            <th>Experience</th>
                            <th>Key Strengths</th>
                        </tr>
                    </thead>
                    <tbody>'''

    # Add top 15 breakout candidates
    for i, (_, player) in enumerate(breakouts.head(15).iterrows(), 1):
        improvement = player['projected_improvement']
        age = int(player['estimated_age'])
        exp = int(player['experience'])
        
        # Identify key strengths
        strengths = []
        if player['points_per_game_norm'] > 70:
            strengths.append('Scoring')
        if player['rebounds_per_game_norm'] > 70:
            strengths.append('Rebounds')
        if player['assists_per_game_norm'] > 70:
            strengths.append('Assists')
        if player['defensive_impact'] > 1.5:
            strengths.append('Defense')
        if player['shooting_volume'] > 15:
            strengths.append('Shooting')
        
        key_strengths = ', '.join(strengths[:3]) if strengths else 'Balanced'
        
        html_content += f'''
                        <tr>
                            <td><strong>{i}</strong></td>
                            <td class="player-name">{player['personName']}</td>
                            <td>{player['fantasy_value']:.0f}</td>
                            <td class="projection-value">{player['projected_2025_value']:.0f}</td>
                            <td class="improvement">+{improvement:.0f}</td>
                            <td>{age}</td>
                            <td>{exp}</td>
                            <td>{key_strengths}</td>
                        </tr>'''

    html_content += '''
                    </tbody>
                </table>
            </div>'''

    # Add tier sections
    for tier_data in tiers:
        tier_name = tier_data['tier'].iloc[0]
        tier_desc = tier_data['tier_description'].iloc[0]
        
        html_content += f'''
            <div class="projection-section">
                <div class="tier-container">
                    <div class="tier-header">
                        {tier_name} - {tier_desc}
                    </div>
                    <table class="tier-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Team</th>
                                <th>2025 Projection</th>
                                <th>2024 Actual</th>
                                <th>Archetype</th>
                                <th>Age</th>
                                <th>Games</th>
                            </tr>
                        </thead>
                        <tbody>'''
        
        start_rank = 1 if tier_name.startswith('Tier 1') else (13 if tier_name.startswith('Tier 2') else (37 if tier_name.startswith('Tier 3') else 73))
        
        for i, (_, player) in enumerate(tier_data.iterrows()):
            rank = start_rank + i
            age = int(player['estimated_age'])
            
            html_content += f'''
                            <tr>
                                <td><strong>{rank}</strong></td>
                                <td class="player-name">{player['personName']}</td>
                                <td>{player['teamTricode']}</td>
                                <td class="projection-value">{player['projected_2025_value']:.0f}</td>
                                <td>{player['fantasy_value']:.0f}</td>
                                <td>{player['archetype']}</td>
                                <td>{age}</td>
                                <td>{player['games_played']:.0f}</td>
                            </tr>'''
        
        html_content += '''
                        </tbody>
                    </table>
                </div>
            </div>'''

    # Add archetype analysis
    archetype_analysis = projections.groupby('archetype').agg({
        'projected_2025_value': ['mean', 'count'],
        'estimated_age': 'mean',
        'experience': 'mean'
    }).round(1)

    html_content += f'''
            <div class="projection-section">
                <div class="section-title">🎯 Player Archetype Analysis</div>
                <div class="archetype-grid">'''

    for archetype in projections['archetype'].unique():
        archetype_data = projections[projections['archetype'] == archetype]
        avg_proj = archetype_data['projected_2025_value'].mean()
        count = len(archetype_data)
        avg_age = archetype_data['estimated_age'].mean()
        
        html_content += f'''
                    <div class="archetype-card">
                        <h4>{archetype}</h4>
                        <p><strong>{count}</strong> players projected</p>
                        <p><strong>Avg Projection:</strong> {avg_proj:.0f}</p>
                        <p><strong>Avg Age:</strong> {avg_age:.1f}</p>
                    </div>'''

    html_content += '''
                </div>
            </div>

            <div class="projection-section">
                <div class="section-title">📈 Model Insights</div>
                <div class="methodology">
                    <h4>Key Predictive Factors</h4>
                    <p><strong>Most Important:</strong> Recent performance trends, age/experience curve, games played consistency</p>
                    <p><strong>Breakout Indicators:</strong> Young age (under 28), improving efficiency, increased usage trends</p>
                    <p><strong>Risk Factors:</strong> Injury history, age-related decline (30+), inconsistent playing time</p>
                    
                    <h4>Usage Guidelines</h4>
                    <p><strong>High Confidence:</strong> Players with stable trends and clear role definition</p>
                    <p><strong>Monitor:</strong> Breakout candidates depend on opportunity and health</p>
                    <p><strong>Team Context:</strong> Projections assume similar role/usage as 2024</p>
                </div>
            </div>

        </div>
    </div>
</body>
</html>'''

    return html_content

def main():
    """Generate 2025 fantasy basketball projections."""
    print("=== 2025 FANTASY BASKETBALL PROJECTION SYSTEM ===")
    
    # Initialize projector
    projector = Fantasy2025Projector()
    
    # Load and prepare data
    projector.load_and_prepare_data()
    projector.define_feature_set()
    
    # Train models
    model_results, best_model = projector.train_models()
    
    # Analyze feature importance
    projector.analyze_feature_importance(best_model)
    
    # Generate projections
    projections = projector.generate_2025_projections(best_model)
    projections = projector.analyze_projection_categories(projections)
    
    # Identify breakouts and create tiers
    breakouts = projector.identify_breakout_candidates(projections)
    tiers = projector.create_projection_tiers(projections)
    
    # Create HTML report
    html_content = create_html_report(projector, projections, breakouts, tiers, model_results, best_model)
    
    # Save the HTML file
    with open('html_reports/prod_ready/player_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\\n2025 projections complete!")
    print(f"Players projected: {len(projections)}")
    print(f"Breakout candidates identified: {len(breakouts)}")
    print(f"Report saved to: html_reports/prod_ready/player_analysis.html")
    
    # Display summary
    print(f"\\nTOP 10 2025 PROJECTIONS:")
    top_10 = projections.head(10)
    for i, (_, player) in enumerate(top_10.iterrows(), 1):
        proj = player['projected_2025_value']
        actual = player['fantasy_value']
        name = player['personName']
        print(f"{i:2d}. {name:25} | 2025: {proj:5.0f} | 2024: {actual:5.0f}")
    
    if len(breakouts) > 0:
        print(f"\\nTOP 5 BREAKOUT CANDIDATES:")
        top_breakouts = breakouts.head(5)
        for i, (_, player) in enumerate(top_breakouts.iterrows(), 1):
            improvement = player['projected_improvement']
            name = player['personName']
            age = int(player['estimated_age'])
            print(f"{i}. {name:25} | Age: {age} | Improvement: +{improvement:3.0f}")
    else:
        print(f"\\nNo breakout candidates found with current criteria")

if __name__ == "__main__":
    main()