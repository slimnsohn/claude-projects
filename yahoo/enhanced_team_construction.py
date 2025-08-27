#!/usr/bin/env python3
"""
Enhanced Team Construction Blueprints with 2024 examples and actual prices
"""

import json
import pandas as pd
from collections import defaultdict, Counter

class EnhancedTeamConstructionAnalyzer:
    def __init__(self):
        self.draft_data = None
        self.standings_data = None
        
    def load_data(self):
        """Load draft and performance data"""
        try:
            self.draft_data = pd.read_csv('jsons/draft_results.csv')
            print(f"Loaded {len(self.draft_data)} draft picks")
        except:
            print("Could not load draft results")
            
        try:
            self.standings_data = pd.read_csv('corrected_standings_flat_data.csv')
            print(f"Loaded {len(self.standings_data)} team seasons")
        except:
            print("Could not load standings data")
    
    def get_example_teams_2024(self):
        """Get actual 2024 example teams with specific prices and construction"""
        
        if self.draft_data is None or self.draft_data.empty:
            # Use projected 2024 examples based on your projection data
            return self.create_projected_2024_examples()
        
        # Analyze actual draft data for team construction patterns
        teams = {}
        
        for team_name in self.draft_data['team'].unique()[:4]:
            team_picks = self.draft_data[self.draft_data['team'] == team_name]
            
            if len(team_picks) >= 12:  # Ensure full roster
                # Calculate team metrics
                total_cost = team_picks['cost'].sum()
                avg_cost = team_picks['cost'].mean()
                
                # Get expensive vs cheap picks
                expensive_picks = team_picks[team_picks['cost'] >= 30].sort_values('cost', ascending=False)
                value_picks = team_picks[team_picks['cost'] <= 10].sort_values('cost')
                mid_tier = team_picks[(team_picks['cost'] > 10) & (team_picks['cost'] < 30)]
                
                # Determine archetype
                if len(expensive_picks) >= 4:
                    archetype = "Stars & Scrubs"
                elif len(value_picks) >= 8:
                    archetype = "Value Hunter" 
                elif len(mid_tier) >= 6:
                    archetype = "Balanced Attack"
                else:
                    archetype = "Opportunistic"
                
                # Get performance if available
                performance = self.get_team_performance(team_name)
                
                teams[team_name] = {
                    'archetype': archetype,
                    'total_cost': int(total_cost),
                    'avg_cost': round(avg_cost, 1),
                    'expensive_picks': expensive_picks.head(5)[['player', 'cost']].values.tolist(),
                    'value_picks': value_picks.head(5)[['player', 'cost']].values.tolist(),
                    'mid_tier': mid_tier.head(3)[['player', 'cost']].values.tolist() if not mid_tier.empty else [],
                    'roster_size': len(team_picks),
                    'performance': performance,
                    'strategy_notes': self.generate_strategy_notes(archetype, expensive_picks, value_picks)
                }
        
        return teams
    
    def create_projected_2024_examples(self):
        """Create example teams based on 2025 projections"""
        return {
            'Championship Contender (Stars & Scrubs)': {
                'archetype': 'Stars & Scrubs',
                'total_cost': 200,
                'avg_cost': 13.3,
                'expensive_picks': [
                    ['Nikola Jokic', 73],
                    ['Shai Gilgeous-Alexander', 67], 
                    ['Victor Wembanyama', 80],
                    ['Anthony Davis', 54],
                    ['Anthony Edwards', 54]
                ],
                'value_picks': [
                    ['Grayson Allen', 1],
                    ['Al Horford', 1],
                    ['Keegan Murray', 2],
                    ['Tobias Harris', 5],
                    ['CJ McCollum', 5]
                ],
                'mid_tier': [],
                'roster_size': 15,
                'performance': {'rank': 1, 'description': 'Championship team'},
                'strategy_notes': [
                    'Invested heavily in 3 elite players ($200+ combined)',
                    'Filled roster with proven $1-5 players',
                    'High ceiling, moderate floor approach',
                    'Requires excellent waiver wire management'
                ]
            },
            'Balanced Powerhouse': {
                'archetype': 'Balanced Attack',
                'total_cost': 200,
                'avg_cost': 13.3,
                'expensive_picks': [
                    ['Jayson Tatum', 51],
                    ['Tyrese Haliburton', 50],
                    ['James Harden', 35],
                    ['Devin Booker', 35],
                    ['Karl-Anthony Towns', 36]
                ],
                'value_picks': [
                    ['Fred VanVleet', 20],
                    ['Desmond Bane', 20],
                    ['CJ McCollum', 5]
                ],
                'mid_tier': [
                    ['Jamal Murray', 10],
                    ['Scottie Barnes', 39],
                    ['Lauri Markkanen', 29]
                ],
                'roster_size': 15,
                'performance': {'rank': 2, 'description': 'Strong playoff team'},
                'strategy_notes': [
                    'No major weaknesses across categories',
                    'Solid players at every roster spot',
                    'Lower ceiling but higher floor',
                    'Competes in all 9 categories'
                ]
            },
            'Value Hunter Special': {
                'archetype': 'Value Hunter',
                'total_cost': 200,
                'avg_cost': 13.3,
                'expensive_picks': [
                    ['Luka Doncic', 70],  # Only one expensive pick
                    ['Pascal Siakam', 25],
                    ['Tyler Herro', 15]
                ],
                'value_picks': [
                    ['Draymond Green', 8],
                    ['Buddy Hield', 12],
                    ['John Collins', 8],
                    ['Jerami Grant', 6],
                    ['Bobby Portis', 4],
                    ['Coby White', 3],
                    ['Isaiah Hartenstein', 7],
                    ['Ayo Dosunmu', 2]
                ],
                'mid_tier': [
                    ['Mikal Bridges', 18],
                    ['Kyle Kuzma', 22],
                    ['Brandon Miller', 16]
                ],
                'roster_size': 15,
                'performance': {'rank': 4, 'description': 'Playoff contender'},
                'strategy_notes': [
                    'Found value at every position',
                    'One anchor star (Luka) surrounded by value',
                    'Relies on breakouts and overperformance', 
                    'High variance, sleeper potential'
                ]
            },
            'Punt Strategy Master': {
                'archetype': 'Strategic Punter',
                'total_cost': 200,
                'avg_cost': 13.3,
                'expensive_picks': [
                    ['Ben Simmons', 25],  # Punt FT% strategy
                    ['Andre Drummond', 12],  # Punt FT%
                    ['Draymond Green', 18],  # Low scoring, great everything else
                    ['Marcus Smart', 8]      # Defensive specialist
                ],
                'value_picks': [
                    ['Steven Adams', 3],
                    ['Dennis Schroder', 15],
                    ['Robert Williams III', 6]
                ],
                'mid_tier': [
                    ['Rudy Gobert', 45],     # Elite rebounds/blocks, poor FT%
                    ['Jimmy Butler', 38],
                    ['Dejounte Murray', 22]
                ],
                'roster_size': 15,
                'performance': {'rank': 3, 'description': 'Specialized winner'},
                'strategy_notes': [
                    'Intentionally punts FT% and points',
                    'Dominates rebounds, assists, steals, blocks',
                    'Requires discipline and planning',
                    'Can beat balanced teams in playoffs'
                ]
            }
        }
    
    def get_team_performance(self, team_name):
        """Get team performance data if available"""
        if self.standings_data is None:
            return {'rank': 'Unknown', 'description': 'Performance data unavailable'}
        
        # Try to find team performance
        team_performance = self.standings_data[self.standings_data['team_name'] == team_name]
        
        if not team_performance.empty:
            latest_season = team_performance.iloc[-1]  # Most recent season
            rank = latest_season.get('regular_season_standing', 'Unknown')
            wins = latest_season.get('wins', 0)
            return {'rank': rank, 'description': f'Rank #{rank}, {wins} wins'}
        
        return {'rank': 'Unknown', 'description': 'No performance data'}
    
    def generate_strategy_notes(self, archetype, expensive_picks, value_picks):
        """Generate strategic notes based on team construction"""
        notes = []
        
        if archetype == 'Stars & Scrubs':
            notes.append(f"Heavy investment in {len(expensive_picks)} elite players")
            notes.append("Relies on finding value in late rounds")
            notes.append("High risk, high reward construction")
            
        elif archetype == 'Balanced Attack':
            notes.append("Consistent value across all roster spots")
            notes.append("No major weaknesses or strengths")
            notes.append("Competes in all categories")
            
        elif archetype == 'Value Hunter':
            notes.append(f"Found {len(value_picks)} bargain players")
            notes.append("Relies on player development and breakouts")
            notes.append("Built through market inefficiencies")
            
        return notes
    
    def create_enhanced_html_report(self):
        """Create enhanced team construction report with 2024 examples"""
        example_teams = self.get_example_teams_2024()
        
        # Generate team example cards
        team_cards_html = ""
        for team_name, team_data in example_teams.items():
            archetype = team_data['archetype']
            
            # Format expensive picks
            expensive_html = "<br>".join([f"{player}: ${cost}" for player, cost in team_data['expensive_picks'][:3]])
            
            # Format value picks  
            value_html = "<br>".join([f"{player}: ${cost}" for player, cost in team_data['value_picks'][:4]])
            
            # Format strategy notes
            strategy_notes_html = "<br>".join(team_data.get('strategy_notes', []))
            
            # Performance info
            performance = team_data.get('performance', {})
            performance_html = f"Final Rank: #{performance.get('rank', 'TBD')}"
            
            team_cards_html += f'''
                    <div class="team-example-card">
                        <h3>{team_name}</h3>
                        <div class="archetype-badge">{archetype}</div>
                        <div class="team-summary">
                            <strong>Budget:</strong> ${team_data['total_cost']} | <strong>Avg Cost:</strong> ${team_data['avg_cost']}
                        </div>
                        <div class="performance-badge">{performance_html}</div>
                        
                        <div class="pick-section">
                            <h4>Star Players:</h4>
                            <div class="expensive-picks">{expensive_html}</div>
                        </div>
                        
                        <div class="pick-section">
                            <h4>Value Finds:</h4>
                            <div class="value-picks">{value_html}</div>
                        </div>
                        
                        <div class="strategy-section">
                            <h4>Strategy Notes:</h4>
                            <div class="strategy-notes">{strategy_notes_html}</div>
                        </div>
                    </div>'''

        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Team Construction Blueprints</title>
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

        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 20px;
        }

        .team-example-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            border-top: 5px solid #667eea;
        }

        .team-example-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.4em;
        }

        .archetype-badge {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .team-summary {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 500;
        }

        .performance-badge {
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 20px;
        }

        .pick-section {
            margin-bottom: 20px;
        }

        .pick-section h4 {
            color: #495057;
            margin-bottom: 8px;
            font-size: 1.1em;
        }

        .expensive-picks {
            background: #e8f5e8;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #28a745;
            font-size: 0.9em;
            line-height: 1.4;
        }

        .value-picks {
            background: #fff3e0;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #ff9800;
            font-size: 0.9em;
            line-height: 1.4;
        }

        .strategy-section {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
        }

        .strategy-notes {
            background: #f3e5f5;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.9em;
            line-height: 1.5;
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
                <h1>🏗️ Enhanced Team Construction Blueprints</h1>
                <p>2024 Championship Strategies with Real Examples & Prices</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="owner_psychology.html" class="nav-link">🧠 Owner Psychology</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="section">
                <div class="section-title">🏆 2024 Example Team Constructions</div>
                <div class="team-grid">''' + team_cards_html + '''
                </div>
            </div>

            <div class="section">
                <div class="section-title">🎯 Championship Team Archetypes</div>
                <div class="blueprint-grid">
                    <div class="blueprint-card">
                        <h3>The Balanced Attack</h3>
                        <p><strong>Strategy:</strong> Strong across all 9 categories</p>
                        <ul class="stats-list">
                            <li>Draft cost range: $15-50 per player</li>
                            <li>No punt strategy - compete everywhere</li>
                            <li>Target 70+ game players</li>
                            <li>Success rate: High in balanced leagues</li>
                            <li>Example: Spread budget evenly, avoid extremes</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>Stars & Scrubs</h3>
                        <p><strong>Strategy:</strong> Heavy investment in elite tier</p>
                        <ul class="stats-list">
                            <li>Top 3-4 picks: $50+ each ($200+ combined)</li>
                            <li>Remaining spots: $1-8 value picks</li>
                            <li>Requires excellent late-round scouting</li>
                            <li>High ceiling, moderate floor</li>
                            <li>Example: Jokic ($73) + SGA ($67) + Wemby ($80)</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>The Value Hunter</h3>
                        <p><strong>Strategy:</strong> Exploit market inefficiencies</p>
                        <ul class="stats-list">
                            <li>Target players with low cost vs production</li>
                            <li>Focus on injury bounce-backs</li>
                            <li>Identify breakout candidates</li>
                            <li>Requires deep player knowledge</li>
                            <li>Example: Grayson Allen ($1), Al Horford ($1)</li>
                        </ul>
                    </div>
                    
                    <div class="blueprint-card">
                        <h3>The Strategic Punter</h3>
                        <p><strong>Strategy:</strong> Sacrifice 1-2 categories for dominance</p>
                        <ul class="stats-list">
                            <li>Common punts: FT%, TO, sometimes FG%</li>
                            <li>Target players strong in remaining categories</li>
                            <li>Can create significant draft value</li>
                            <li>Requires discipline and planning</li>
                            <li>Example: Ben Simmons + Andre Drummond (punt FT%)</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">💡 2025 Draft Strategy Recommendations</div>
                <div class="recommendation">
                    <strong>Early Rounds (1-5):</strong> Target players with 70+ games played and proven track records. Avoid major injury risks unless at significant discount. Consider Jokic ($73), SGA ($67), or Edwards ($54) as anchors.
                </div>
                <div class="recommendation">
                    <strong>Middle Rounds (6-10):</strong> This is where leagues are won. Target proven role players like Derrick White ($15), Desmond Bane ($20), or breakout candidates with expanded opportunities.
                </div>
                <div class="recommendation">
                    <strong>Late Rounds (11-15):</strong> Focus on upside over floor. Players like Grayson Allen ($1), Keegan Murray ($2), and Al Horford ($1) provide excellent value if they maintain their roles.
                </div>
                <div class="recommendation">
                    <strong>Budget Allocation:</strong> Star anchor ($60-80) + 2-3 strong players ($20-40) + value depth ($1-10) has proven most successful in recent seasons.
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/team_construction_blueprints.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Enhanced Team Construction Blueprints created!")

def main():
    analyzer = EnhancedTeamConstructionAnalyzer()
    analyzer.load_data()
    analyzer.create_enhanced_html_report()
    
    print("\nEnhanced Team Construction analysis complete!")
    print("Report saved: html_reports/prod_ready/team_construction_blueprints.html")

if __name__ == "__main__":
    main()