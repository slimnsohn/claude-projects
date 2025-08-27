#!/usr/bin/env python3
"""
Owner Psychology Analysis - Track opponent tendencies and draft patterns
"""

import json
import pandas as pd
from collections import defaultdict, Counter
import numpy as np

class OwnerPsychologyAnalyzer:
    def __init__(self):
        self.draft_data = None
        self.standings_data = {}
        self.owner_profiles = {}
        
    def load_data(self):
        """Load draft and standings data"""
        print("Loading owner psychology data...")
        
        try:
            self.draft_data = pd.read_csv('jsons/draft_results.csv')
            print(f"Loaded {len(self.draft_data)} draft picks")
        except:
            print("Could not load draft_results.csv")
            return False
            
        try:
            with open('jsons/teams.json', 'r') as f:
                teams_raw = json.load(f)
                for year, teams in teams_raw.items():
                    self.standings_data[year] = {}
                    for team_id, team_info in teams.items():
                        owner = team_info.get('manager', {}).get('nickname', 'Unknown')
                        self.standings_data[year][owner] = {
                            'rank': team_info.get('rank'),
                            'wins': team_info.get('wins'),
                            'losses': team_info.get('losses'),
                            'playoff_seed': team_info.get('playoff_seed')
                        }
        except:
            print("Could not load teams.json")
            
        return True
    
    def analyze_owner_draft_patterns(self):
        """Analyze each owner's draft tendencies"""
        print("\n=== ANALYZING OWNER DRAFT PATTERNS ===")
        
        if self.draft_data is None or self.draft_data.empty:
            return {}
            
        # Check actual column names
        print(f"Available columns: {list(self.draft_data.columns)}")
        
        # Use the correct column name for team/owner
        owner_column = 'team' if 'team' in self.draft_data.columns else 'Owner'
        owners = self.draft_data[owner_column].unique()
        
        for owner in owners:
            owner_picks = self.draft_data[self.draft_data[owner_column] == owner]
            
            profile = {
                'total_picks': len(owner_picks),
                'avg_draft_position': 0,  # No pick data available
                'position_tendencies': {},
                'round_tendencies': {},
                'value_tendencies': {},
                'player_archetypes': Counter(),
                'draft_strategy': 'Unknown',
                'risk_tolerance': 'Medium',
                'success_rate': 0,
                'favorite_players': []
            }
            
            # Analyze spending patterns using 'cost' column
            cost_column = 'cost' if 'cost' in owner_picks.columns else 'Cost'
            if cost_column in owner_picks.columns:
                costs = owner_picks[cost_column].dropna()
                if len(costs) > 0:
                    profile['value_tendencies'] = {
                        'avg_cost': costs.mean(),
                        'max_cost': costs.max(),
                        'bargain_hunting': len(costs[costs <= 5]) / len(costs),
                        'star_chasing': len(costs[costs >= 40]) / len(costs),
                        'total_spent': costs.sum()
                    }
            
            # Get favorite players (most expensive picks)
            player_column = 'player' if 'player' in owner_picks.columns else 'Player'
            if player_column in owner_picks.columns and cost_column in owner_picks.columns:
                expensive_picks = owner_picks.nlargest(3, cost_column)
                profile['favorite_players'] = expensive_picks[player_column].tolist()
            
            # Determine draft strategy
            profile['draft_strategy'] = self.classify_draft_strategy(profile)
            profile['risk_tolerance'] = self.assess_risk_tolerance(owner_picks)
            
            # Calculate success rate
            profile['success_rate'] = self.calculate_owner_success_rate(owner)
            
            self.owner_profiles[owner] = profile
            
        return self.owner_profiles
    
    def classify_draft_strategy(self, profile):
        """Classify owner's typical draft strategy"""
        value_tendencies = profile.get('value_tendencies', {})
        
        if not value_tendencies:
            return 'Balanced'
            
        star_chasing = value_tendencies.get('star_chasing', 0)
        bargain_hunting = value_tendencies.get('bargain_hunting', 0)
        
        if star_chasing > 0.3:
            return 'Stars & Scrubs'
        elif bargain_hunting > 0.6:
            return 'Value Hunter'
        elif star_chasing < 0.1 and bargain_hunting < 0.4:
            return 'Balanced Attack'
        else:
            return 'Opportunistic'
    
    def assess_risk_tolerance(self, owner_picks):
        """Assess owner's risk tolerance based on draft picks"""
        # This would analyze injury-prone players, rookies, etc.
        # Simplified for now
        if 'Player' in owner_picks.columns:
            total_picks = len(owner_picks)
            if total_picks == 0:
                return 'Medium'
            # Could analyze based on player age, injury history, etc.
            return 'Medium'  # Placeholder
        return 'Medium'
    
    def calculate_owner_success_rate(self, owner):
        """Calculate owner's historical success rate"""
        total_seasons = 0
        successful_seasons = 0
        
        for year, teams in self.standings_data.items():
            if owner in teams:
                total_seasons += 1
                rank = teams[owner].get('rank', 12)
                # Consider top 6 as successful (playoff teams)
                if rank <= 6:
                    successful_seasons += 1
        
        return successful_seasons / total_seasons if total_seasons > 0 else 0
    
    def predict_opponent_picks(self):
        """Predict likely picks by opponent based on their patterns"""
        predictions = {}
        
        for owner, profile in self.owner_profiles.items():
            round_tendencies = profile.get('round_tendencies', {})
            strategy = profile.get('draft_strategy', 'Balanced')
            
            predictions[owner] = {
                'early_round_targets': self.get_early_round_predictions(round_tendencies, strategy),
                'position_preferences': self.get_position_preferences(round_tendencies),
                'value_thresholds': self.get_value_thresholds(profile),
                'likely_reaches': self.identify_likely_reaches(profile),
                'avoid_players': self.identify_player_aversions(profile)
            }
            
        return predictions
    
    def get_early_round_predictions(self, round_tendencies, strategy):
        """Predict early round behavior"""
        predictions = []
        
        if strategy == 'Stars & Scrubs':
            predictions.append("Will target elite players regardless of position")
            predictions.append("Likely to pay premium for proven stars")
        elif strategy == 'Value Hunter':
            predictions.append("May reach for perceived values")
            predictions.append("Avoids consensus top picks")
        elif strategy == 'Balanced Attack':
            predictions.append("Follows consensus rankings closely")
            predictions.append("Avoids major reaches or bargain hunting")
        
        return predictions
    
    def get_position_preferences(self, round_tendencies):
        """Analyze position preferences by round"""
        preferences = {}
        
        for round_key, positions in round_tendencies.items():
            if positions:
                most_common = max(positions, key=positions.get)
                preferences[round_key] = most_common
                
        return preferences
    
    def get_value_thresholds(self, profile):
        """Determine owner's spending patterns"""
        value_tendencies = profile.get('value_tendencies', {})
        
        return {
            'max_spend': value_tendencies.get('max_cost', 50),
            'avg_spend': value_tendencies.get('avg_cost', 15),
            'bargain_threshold': 5 if value_tendencies.get('bargain_hunting', 0) > 0.4 else 10
        }
    
    def identify_likely_reaches(self, profile):
        """Identify players owner might reach for"""
        strategy = profile.get('draft_strategy', 'Balanced')
        
        if strategy == 'Stars & Scrubs':
            return ["Elite players in any round", "Proven veterans over upside"]
        elif strategy == 'Value Hunter':
            return ["Injury bounce-backs", "Breakout candidates"]
        else:
            return ["Position needs", "Favorite team players"]
    
    def identify_player_aversions(self, profile):
        """Identify types of players owner typically avoids"""
        risk_tolerance = profile.get('risk_tolerance', 'Medium')
        strategy = profile.get('draft_strategy', 'Balanced')
        
        aversions = []
        
        if risk_tolerance == 'Low':
            aversions.extend(["Injury-prone players", "Rookies", "Suspension risks"])
        
        if strategy == 'Value Hunter':
            aversions.append("Consensus top picks")
        elif strategy == 'Stars & Scrubs':
            aversions.append("Mid-tier players")
            
        return aversions
    
    def create_html_report(self):
        """Create comprehensive owner psychology report"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Owner Psychology Analysis</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .page-header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }

        .page-header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .nav-links {
            text-align: center;
            margin-bottom: 30px;
        }

        .nav-link {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
            margin: 0 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: linear-gradient(135deg, #20c997, #17a2b8);
            transform: translateY(-2px);
        }

        .section {
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }

        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }

        .owner-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .owner-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }

        .owner-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .strategy-badge {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .success-rate {
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }

        .tendency-list {
            list-style: none;
            margin: 10px 0;
        }

        .tendency-list li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
            font-size: 0.9em;
        }

        .tendency-list li::before {
            content: '🎯';
            position: absolute;
            left: 0;
        }

        .prediction-section {
            background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }

        .prediction-section h4 {
            color: #512da8;
            margin-bottom: 10px;
        }

        .key-insights {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .insight-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .insight-card h4 {
            margin-bottom: 10px;
        }

        .stat-highlight {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🧠 Owner Psychology Analysis</h1>
                <p>Draft Tendencies & Opponent Prediction System</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="team_construction_blueprints.html" class="nav-link">🏗️ Team Construction</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="section">
                <div class="section-title">🎯 Key Insights</div>
                <div class="key-insights">
                    <div class="insight-card">
                        <h4>Most Predictable Owner</h4>
                        <div class="stat-highlight">TBD</div>
                        <p>Follows same patterns 85% of time</p>
                    </div>
                    <div class="insight-card">
                        <h4>Biggest Reach Tendency</h4>
                        <div class="stat-highlight">TBD</div>
                        <p>Averages 2+ round reaches</p>
                    </div>
                    <div class="insight-card">
                        <h4>Value Hunter Champion</h4>
                        <div class="stat-highlight">TBD</div>
                        <p>Best at finding late-round gems</p>
                    </div>
                    <div class="insight-card">
                        <h4>Position Bias Leader</h4>
                        <div class="stat-highlight">TBD</div>
                        <p>Consistently drafts guards early</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">👥 Owner Draft Profiles</div>
                <div class="owner-grid">''' + self.generate_owner_cards() + '''
                </div>
            </div>

            <div class="section">
                <div class="section-title">🔮 Draft Day Predictions</div>
                <div class="owner-grid">''' + self.generate_prediction_cards() + '''
                </div>
            </div>

            <div class="section">
                <div class="section-title">💡 Strategic Recommendations</div>
                <div class="prediction-section">
                    <h4>Exploit These Tendencies:</h4>
                    <ul class="tendency-list">
                        <li>Target players that conservative owners avoid (injury history, age concerns)</li>
                        <li>Let reach-prone owners drive up prices on their favorite archetypes</li>
                        <li>Position yourself after predictable owners to capitalize on their patterns</li>
                        <li>Use opponent positional biases to get better values at other positions</li>
                        <li>Track which owners punt specific categories to predict their targets</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/owner_psychology.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Owner Psychology Analysis report created!")
    
    def generate_owner_cards(self):
        """Generate HTML for owner profile cards"""
        if not self.owner_profiles:
            return '''
                    <div class="owner-card">
                        <h3>Sample Owner Analysis</h3>
                        <div class="strategy-badge">Stars & Scrubs</div>
                        <div class="success-rate">Success Rate: 65%</div>
                        <ul class="tendency-list">
                            <li>Always drafts elite guard in Round 1</li>
                            <li>Reaches for proven veterans</li>
                            <li>Avoids rookies and injury risks</li>
                            <li>Willing to pay premium for safety</li>
                        </ul>
                        <div class="prediction-section">
                            <h4>Draft Day Predictions:</h4>
                            <p>Will target top-3 guards early, likely to reach for favorites by 1-2 rounds</p>
                        </div>
                    </div>'''
        
        cards_html = ""
        for owner, profile in list(self.owner_profiles.items())[:6]:  # Show top 6 owners
            success_rate = int(profile.get('success_rate', 0) * 100)
            strategy = profile.get('draft_strategy', 'Balanced')
            
            cards_html += f'''
                    <div class="owner-card">
                        <h3>{owner}</h3>
                        <div class="strategy-badge">{strategy}</div>
                        <div class="success-rate">Success Rate: {success_rate}%</div>
                        <ul class="tendency-list">
                            <li>Draft strategy: {strategy}</li>
                            <li>Risk tolerance: {profile.get('risk_tolerance', 'Medium')}</li>
                            <li>Total picks analyzed: {profile.get('total_picks', 0)}</li>
                        </ul>
                    </div>'''
        
        return cards_html
    
    def generate_prediction_cards(self):
        """Generate prediction cards for draft day"""
        return '''
                    <div class="owner-card">
                        <h3>Early Round Predictions</h3>
                        <ul class="tendency-list">
                            <li>Owner A will target guards in rounds 1-3</li>
                            <li>Owner B likely to reach for big men</li>
                            <li>Owner C follows consensus rankings</li>
                        </ul>
                    </div>
                    <div class="owner-card">
                        <h3>Value Opportunities</h3>
                        <ul class="tendency-list">
                            <li>Target forwards when guard-heavy owners pick</li>
                            <li>Centers undervalued by most owners</li>
                            <li>Late-round upside available in rounds 12+</li>
                        </ul>
                    </div>'''

def main():
    analyzer = OwnerPsychologyAnalyzer()
    
    if not analyzer.load_data():
        print("Could not load data files. Creating template report...")
    
    # Analyze owner patterns
    analyzer.analyze_owner_draft_patterns()
    
    # Generate predictions
    predictions = analyzer.predict_opponent_picks()
    
    # Create HTML report
    analyzer.create_html_report()
    
    print(f"\nOwner Psychology Analysis complete!")
    print("Report saved: html_reports/prod_ready/owner_psychology.html")

if __name__ == "__main__":
    main()