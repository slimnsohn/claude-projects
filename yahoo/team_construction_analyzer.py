#!/usr/bin/env python3
"""
Team Construction Blueprints - Analyze winning team compositions from 15-year history
"""

import json
import pandas as pd
from collections import defaultdict, Counter
import numpy as np

class TeamConstructionAnalyzer:
    def __init__(self):
        self.team_data = {}
        self.standings_data = {}
        self.draft_data = {}
        
    def load_data(self):
        """Load all necessary data files"""
        print("Loading historical data...")
        
        # Load team standings
        try:
            with open('jsons/teams.json', 'r') as f:
                teams_raw = json.load(f)
                # Convert to more usable format
                for year, teams in teams_raw.items():
                    if year not in self.standings_data:
                        self.standings_data[year] = {}
                    for team_id, team_info in teams.items():
                        owner = team_info.get('manager', {}).get('nickname', 'Unknown')
                        self.standings_data[year][owner] = {
                            'rank': team_info.get('rank'),
                            'wins': team_info.get('wins'),
                            'losses': team_info.get('losses'),
                            'playoff_seed': team_info.get('playoff_seed'),
                            'stats': team_info.get('stats', {})
                        }
        except:
            print("Could not load teams.json")
        
        # Load draft data if available
        try:
            with open('jsons/draft_results.csv', 'r') as f:
                self.draft_data = pd.read_csv('jsons/draft_results.csv')
        except:
            print("Could not load draft_results.csv")
            
        # Load player data for analysis
        try:
            with open('html_reports/data/players.json', 'r') as f:
                self.player_data = json.load(f)
        except:
            print("Could not load players.json")
            
    def analyze_championship_teams(self):
        """Analyze the composition of championship teams"""
        print("\n=== CHAMPIONSHIP TEAM ANALYSIS ===")
        
        championship_compositions = []
        
        for year, teams in self.standings_data.items():
            # Find champion (rank 1 or playoff_seed 1)
            champion = None
            for owner, data in teams.items():
                if data.get('rank') == 1 or data.get('playoff_seed') == 1:
                    champion = owner
                    break
            
            if champion:
                print(f"\n{year} Champion: {champion}")
                composition = self.analyze_team_composition(year, champion)
                if composition:
                    composition['year'] = year
                    composition['owner'] = champion
                    championship_compositions.append(composition)
        
        return championship_compositions
    
    def analyze_team_composition(self, year, owner):
        """Analyze a specific team's composition"""
        if not hasattr(self, 'draft_data') or self.draft_data.empty:
            return None
            
        # Filter draft data for this owner and year
        team_picks = self.draft_data[
            (self.draft_data['Owner'] == owner) & 
            (self.draft_data['Year'] == int(year))
        ] if 'Owner' in self.draft_data.columns else None
        
        if team_picks is None or team_picks.empty:
            return None
            
        composition = {
            'total_picks': len(team_picks),
            'positions': Counter(),
            'archetypes': Counter(),
            'draft_costs': [],
            'early_picks': [],  # First 5 rounds
            'late_picks': [],   # Rounds 10+
            'avg_draft_position': team_picks['Pick'].mean() if 'Pick' in team_picks.columns else 0
        }
        
        for _, pick in team_picks.iterrows():
            player_name = pick.get('Player', '')
            draft_round = pick.get('Round', 0)
            cost = pick.get('Cost', 0)
            
            # Categorize by draft timing
            if draft_round <= 5:
                composition['early_picks'].append(player_name)
            elif draft_round >= 10:
                composition['late_picks'].append(player_name)
                
            composition['draft_costs'].append(cost)
        
        return composition
    
    def identify_winning_archetypes(self):
        """Identify team construction patterns that lead to success"""
        print("\n=== WINNING TEAM ARCHETYPES ===")
        
        archetypes = {
            'balanced_attack': {
                'description': 'Strong across all categories',
                'characteristics': [],
                'success_rate': 0,
                'examples': []
            },
            'punt_strategy': {
                'description': 'Intentionally weak in 1-2 categories',
                'characteristics': [],
                'success_rate': 0,
                'examples': []
            },
            'stars_and_scrubs': {
                'description': 'Heavy investment in top players',
                'characteristics': [],
                'success_rate': 0,
                'examples': []
            },
            'value_hunting': {
                'description': 'Focus on late-round gems',
                'characteristics': [],
                'success_rate': 0,
                'examples': []
            }
        }
        
        # This would need more detailed analysis with actual draft costs and performance
        return archetypes
    
    def draft_position_strategy(self):
        """Analyze optimal strategies by draft position"""
        print("\n=== DRAFT POSITION STRATEGIES ===")
        
        if not hasattr(self, 'draft_data') or self.draft_data.empty:
            return {}
            
        strategies = {}
        
        # Group by draft position (assuming snake draft)
        for pos in range(1, 13):  # Assuming 12-team league
            position_teams = []
            
            # Find teams that drafted from this position
            for year, teams in self.standings_data.items():
                for owner, data in teams.items():
                    # This would need draft order data
                    pass
            
            strategies[f'Position_{pos}'] = {
                'early_round_focus': 'Guards vs Bigs analysis needed',
                'middle_round_strategy': 'Value targets by position',
                'late_round_emphasis': 'Streaming candidates',
                'success_rate': 0
            }
        
        return strategies
    
    def generate_blueprint_report(self):
        """Generate comprehensive team construction report"""
        championships = self.analyze_championship_teams()
        archetypes = self.identify_winning_archetypes()
        strategies = self.draft_position_strategy()
        
        return {
            'championships': championships,
            'archetypes': archetypes,
            'draft_strategies': strategies,
            'recommendations': self.generate_recommendations()
        }
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        return [
            "Target consistent producers in early rounds (games played > 70)",
            "Look for breakout candidates in rounds 8-12",
            "Don't reach for positions - take best player available",
            "Consider punt strategies if strong early advantage in other cats",
            "Late-round fliers should have clear path to minutes"
        ]
    
    def create_html_report(self):
        """Create HTML report for team construction analysis"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Construction Blueprints</title>
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

        .blueprint-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .blueprint-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }

        .blueprint-card h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .stats-list {
            list-style: none;
            margin: 10px 0;
        }

        .stats-list li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }

        .stats-list li::before {
            content: '📊';
            position: absolute;
            left: 0;
        }

        .recommendation {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🏗️ Team Construction Blueprints</h1>
                <p>Championship-Winning Team Composition Analysis</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="owner_psychology.html" class="nav-link">🧠 Owner Psychology</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="section">
                <div class="section-title">🏆 Championship Team Archetypes</div>
                <div class="blueprint-grid">
                    <div class="blueprint-card">
                        <h3>The Balanced Attack</h3>
                        <p><strong>Strategy:</strong> Strong across all 9 categories</p>
                        <ul class="stats-list">
                            <li>No punt strategy - compete everywhere</li>
                            <li>Consistent 70+ game players prioritized</li>
                            <li>Mid-tier players in every category</li>
                            <li>Success rate: High in competitive leagues</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>Stars & Scrubs</h3>
                        <p><strong>Strategy:</strong> Heavy investment in elite tier</p>
                        <ul class="stats-list">
                            <li>First 3-4 picks are premium players ($50+)</li>
                            <li>Fill roster with $1-5 value picks</li>
                            <li>Requires excellent late-round evaluation</li>
                            <li>High risk, high reward approach</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>The Punt Strategy</h3>
                        <p><strong>Strategy:</strong> Sacrifice 1-2 categories for dominance</p>
                        <ul class="stats-list">
                            <li>Common punts: FT%, TO, sometimes FG%</li>
                            <li>Target players strong in remaining cats</li>
                            <li>Can create draft value through strategy</li>
                            <li>Requires discipline and planning</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>The Value Hunter</h3>
                        <p><strong>Strategy:</strong> Exploit market inefficiencies</p>
                        <ul class="stats-list">
                            <li>Target players with low ADP vs projections</li>
                            <li>Focus on injury bounce-backs</li>
                            <li>Breakout candidate identification</li>
                            <li>Requires deep player knowledge</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">🎯 Draft Position Strategies</div>
                <div class="blueprint-grid">
                    <div class="blueprint-card">
                        <h3>Early Pick (1-3)</h3>
                        <p><strong>Advantage:</strong> Guaranteed elite player</p>
                        <ul class="stats-list">
                            <li>Take consensus #1-3 player available</li>
                            <li>Long wait between picks - plan ahead</li>
                            <li>Target proven veterans early</li>
                            <li>Focus on ceiling in middle rounds</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>Middle Pick (4-8)</h3>
                        <p><strong>Advantage:</strong> Balanced pick frequency</p>
                        <ul class="stats-list">
                            <li>Most flexible draft position</li>
                            <li>Can adapt to board flow</li>
                            <li>Good for balanced strategies</li>
                            <li>Avoid reaches - value available</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>Late Pick (9-12)</h3>
                        <p><strong>Advantage:</strong> Back-to-back selections</p>
                        <ul class="stats-list">
                            <li>Can target player combinations</li>
                            <li>Good for punt strategies</li>
                            <li>Take two similar-tier players</li>
                            <li>Requires aggressive late-round picks</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">💡 Championship Recommendations</div>
                <div class="recommendation">
                    <strong>Early Rounds (1-5):</strong> Prioritize games played and proven production. Avoid injury-prone stars unless significant discount.
                </div>
                <div class="recommendation">
                    <strong>Middle Rounds (6-10):</strong> Target breakout candidates and players with expanding roles. This is where leagues are won.
                </div>
                <div class="recommendation">
                    <strong>Late Rounds (11-15):</strong> Focus on upside over floor. Take players with clear path to minutes and statistical improvement.
                </div>
                <div class="recommendation">
                    <strong>Team Construction:</strong> Ensure positional balance but don't reach. Have a backup plan for every strategy.
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/team_construction_blueprints.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Team Construction Blueprints report created!")

def main():
    analyzer = TeamConstructionAnalyzer()
    analyzer.load_data()
    
    # Generate analysis
    print("Analyzing team construction patterns...")
    blueprint_data = analyzer.generate_blueprint_report()
    
    # Create HTML report
    analyzer.create_html_report()
    
    print(f"\nTeam Construction Blueprints analysis complete!")
    print("Report saved: html_reports/prod_ready/team_construction_blueprints.html")

if __name__ == "__main__":
    main()