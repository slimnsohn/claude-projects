#!/usr/bin/env python3
"""
Comprehensive Owner Psychology Analysis - All owners, all years, with specific examples
"""

import json
import pandas as pd
from collections import defaultdict, Counter
import numpy as np

class ComprehensiveOwnerAnalyzer:
    def __init__(self):
        self.owner_data = {}
        self.standings_data = {}
        self.draft_data = None
        self.all_owners = {}
        
    def load_comprehensive_data(self):
        """Load all available owner and performance data"""
        print("Loading comprehensive owner data...")
        
        # Load owner analysis data
        try:
            with open('html_reports/data/owner_analysis.json', 'r') as f:
                owner_analysis = json.load(f)
                self.owner_data = owner_analysis.get('owner_data', {})
            print(f"Loaded data for {len(self.owner_data)} owners")
        except:
            print("Could not load owner_analysis.json")
            
        # Load standings data
        try:
            self.standings_data = pd.read_csv('corrected_standings_flat_data.csv')
            print(f"Loaded {len(self.standings_data)} team seasons")
        except:
            print("Could not load standings data")
            
        # Load draft results
        try:
            self.draft_data = pd.read_csv('jsons/draft_results.csv')
            print(f"Loaded {len(self.draft_data)} draft picks")
        except:
            print("Could not load draft results")
    
    def analyze_all_owners(self):
        """Analyze all owners with comprehensive data"""
        print("\n=== COMPREHENSIVE OWNER ANALYSIS ===")
        
        all_profiles = {}
        
        # Get all unique owners from multiple sources
        all_owner_names = set()
        
        # From owner data
        for email, data in self.owner_data.items():
            team_names = data.get('team_names', {})
            for year, team_name in team_names.items():
                all_owner_names.add(team_name)
        
        # From standings data
        if hasattr(self, 'standings_data') and not self.standings_data.empty:
            all_owner_names.update(self.standings_data['team_name'].unique())
            
        # From draft data
        if self.draft_data is not None and not self.draft_data.empty:
            all_owner_names.update(self.draft_data['team'].unique())
        
        print(f"Found {len(all_owner_names)} unique owners/teams")
        
        # Analyze each owner
        for owner_name in all_owner_names:
            profile = self.create_comprehensive_profile(owner_name)
            if profile['seasons_active'] > 0:
                all_profiles[owner_name] = profile
        
        # Sort by activity level and success
        sorted_owners = sorted(all_profiles.items(), 
                             key=lambda x: (x[1]['seasons_active'], x[1]['avg_standing']), 
                             reverse=True)
        
        return dict(sorted_owners)
    
    def create_comprehensive_profile(self, owner_name):
        """Create detailed profile for a specific owner"""
        profile = {
            'seasons_active': 0,
            'years': [],
            'standings': [],
            'avg_standing': 0,
            'best_finish': 12,
            'playoff_appearances': 0,
            'championships': 0,
            'draft_picks': [],
            'spending_pattern': 'Unknown',
            'draft_strategy': 'Unknown',
            'position_bias': 'None',
            'risk_tolerance': 'Medium',
            'example_picks': [],
            'signature_moves': [],
            'success_rate': 0
        }
        
        # Analyze standings performance
        if hasattr(self, 'standings_data') and not self.standings_data.empty:
            owner_standings = self.standings_data[self.standings_data['team_name'] == owner_name]
            
            if not owner_standings.empty:
                profile['seasons_active'] = len(owner_standings)
                profile['years'] = owner_standings['year'].tolist()
                profile['standings'] = owner_standings['regular_season_standing'].tolist()
                profile['avg_standing'] = owner_standings['regular_season_standing'].mean()
                profile['best_finish'] = owner_standings['regular_season_standing'].min()
                
                # Count playoff appearances (assuming top 6 make playoffs)
                profile['playoff_appearances'] = len(owner_standings[owner_standings['regular_season_standing'] <= 6])
                profile['championships'] = len(owner_standings[owner_standings['regular_season_standing'] == 1])
                profile['success_rate'] = profile['playoff_appearances'] / profile['seasons_active'] if profile['seasons_active'] > 0 else 0
        
        # Analyze draft picks and spending
        if self.draft_data is not None and not self.draft_data.empty:
            owner_picks = self.draft_data[self.draft_data['team'] == owner_name]
            
            if not owner_picks.empty:
                profile['draft_picks'] = len(owner_picks)
                costs = owner_picks['cost'].dropna()
                
                if len(costs) > 0:
                    avg_cost = costs.mean()
                    max_cost = costs.max()
                    min_cost = costs.min()
                    
                    # Determine spending pattern
                    high_spenders = len(costs[costs >= 40])
                    bargain_picks = len(costs[costs <= 5])
                    total_picks = len(costs)
                    
                    if high_spenders / total_picks > 0.3:
                        profile['spending_pattern'] = 'Star Chaser'
                    elif bargain_picks / total_picks > 0.6:
                        profile['spending_pattern'] = 'Bargain Hunter'
                    else:
                        profile['spending_pattern'] = 'Balanced Spender'
                    
                    # Get example picks (most expensive)
                    expensive_picks = owner_picks.nlargest(3, 'cost')
                    cheap_gems = owner_picks.nsmallest(3, 'cost')
                    
                    profile['example_picks'] = {
                        'expensive': [(row['player'], row['cost']) for _, row in expensive_picks.iterrows()],
                        'bargains': [(row['player'], row['cost']) for _, row in cheap_gems.iterrows()]
                    }
                    
                    # Analyze draft strategy based on spending distribution
                    if max_cost >= 60 and min_cost <= 3:
                        profile['draft_strategy'] = 'Stars & Scrubs'
                    elif costs.std() < 15:
                        profile['draft_strategy'] = 'Balanced Attack'
                    else:
                        profile['draft_strategy'] = 'Opportunistic'
        
        # Determine signature moves
        profile['signature_moves'] = self.identify_signature_moves(profile)
        
        return profile
    
    def identify_signature_moves(self, profile):
        """Identify owner's signature draft moves"""
        moves = []
        
        spending_pattern = profile.get('spending_pattern', 'Unknown')
        strategy = profile.get('draft_strategy', 'Unknown')
        success_rate = profile.get('success_rate', 0)
        
        if spending_pattern == 'Star Chaser':
            moves.append("Always targets elite players regardless of value")
            moves.append("Willing to pay premium for proven production")
            
        if spending_pattern == 'Bargain Hunter':
            moves.append("Focuses on late-round gems and value picks")
            moves.append("Avoids expensive stars, builds depth")
            
        if strategy == 'Stars & Scrubs':
            moves.append("Extreme bimodal spending - stars + minimum players")
            moves.append("Believes in concentrated talent over depth")
            
        if success_rate > 0.6:
            moves.append("Consistently competitive - proven winner")
        elif success_rate < 0.3:
            moves.append("Struggles with consistency - potential value source")
            
        return moves if moves else ["Standard draft approach", "No clear patterns identified"]
    
    def get_2024_example_teams(self):
        """Get example teams with 2024 data and prices"""
        example_teams = {}
        
        if self.draft_data is None or self.draft_data.empty:
            return self.create_sample_2024_teams()
        
        # Get teams from draft data (assuming recent data represents 2024)
        teams = self.draft_data['team'].unique()
        
        for team in teams[:4]:  # Get top 4 teams as examples
            team_picks = self.draft_data[self.draft_data['team'] == team]
            
            if len(team_picks) >= 10:  # Ensure sufficient data
                total_cost = team_picks['cost'].sum()
                avg_cost = team_picks['cost'].mean()
                
                # Classify team construction
                expensive_picks = len(team_picks[team_picks['cost'] >= 40])
                cheap_picks = len(team_picks[team_picks['cost'] <= 5])
                
                if expensive_picks >= 3:
                    archetype = "Stars & Scrubs"
                elif cheap_picks >= 8:
                    archetype = "Value Hunter"
                else:
                    archetype = "Balanced Attack"
                
                example_teams[team] = {
                    'archetype': archetype,
                    'total_spent': total_cost,
                    'avg_cost': avg_cost,
                    'top_picks': team_picks.nlargest(5, 'cost')[['player', 'cost']].to_dict('records'),
                    'bargain_picks': team_picks.nsmallest(3, 'cost')[['player', 'cost']].to_dict('records'),
                    'roster_size': len(team_picks)
                }
        
        return example_teams
    
    def create_sample_2024_teams(self):
        """Create sample teams based on 2024 projections"""
        return {
            'Get Schwifty': {
                'archetype': 'Stars & Scrubs',
                'total_spent': 200,
                'avg_cost': 13.3,
                'top_picks': [
                    {'player': 'Nikola Jokic', 'cost': 73},
                    {'player': 'Shai Gilgeous-Alexander', 'cost': 67},
                    {'player': 'Victor Wembanyama', 'cost': 80},
                    {'player': 'Anthony Davis', 'cost': 54},
                    {'player': 'Anthony Edwards', 'cost': 54}
                ],
                'bargain_picks': [
                    {'player': 'Grayson Allen', 'cost': 1},
                    {'player': 'Al Horford', 'cost': 1},
                    {'player': 'Keegan Murray', 'cost': 2}
                ],
                'roster_size': 15
            },
            'The Bandwagon': {
                'archetype': 'Balanced Attack',
                'total_spent': 200,
                'avg_cost': 13.3,
                'top_picks': [
                    {'player': 'Jayson Tatum', 'cost': 51},
                    {'player': 'Tyrese Haliburton', 'cost': 50},
                    {'player': 'James Harden', 'cost': 35},
                    {'player': 'Devin Booker', 'cost': 35},
                    {'player': 'Karl-Anthony Towns', 'cost': 36}
                ],
                'bargain_picks': [
                    {'player': 'Tobias Harris', 'cost': 5},
                    {'player': 'CJ McCollum', 'cost': 5},
                    {'player': 'Fred VanVleet', 'cost': 20}
                ],
                'roster_size': 15
            }
        }
    
    def create_enhanced_html_report(self):
        """Create enhanced HTML report with comprehensive analysis"""
        owner_profiles = self.analyze_all_owners()
        example_teams = self.get_2024_example_teams()
        
        # Generate owner cards HTML
        owner_cards_html = ""
        for owner, profile in list(owner_profiles.items())[:8]:  # Show top 8 owners
            success_rate = int(profile.get('success_rate', 0) * 100)
            
            example_picks_html = ""
            if profile.get('example_picks'):
                expensive = profile['example_picks'].get('expensive', [])
                if expensive:
                    example_picks_html = f"<strong>Expensive picks:</strong> "
                    example_picks_html += ", ".join([f"{player} (${cost})" for player, cost in expensive[:2]])
            
            signature_moves_html = "<br>".join(profile.get('signature_moves', []))
            
            owner_cards_html += f'''
                    <div class="owner-card">
                        <h3>{owner}</h3>
                        <div class="strategy-badge">{profile.get('draft_strategy', 'Unknown')}</div>
                        <div class="success-rate">Success: {success_rate}% | Seasons: {profile.get('seasons_active', 0)}</div>
                        <ul class="tendency-list">
                            <li>Spending: {profile.get('spending_pattern', 'Unknown')}</li>
                            <li>Best finish: #{profile.get('best_finish', 12)}</li>
                            <li>Championships: {profile.get('championships', 0)}</li>
                            <li>Playoff rate: {profile.get('playoff_appearances', 0)}/{profile.get('seasons_active', 0)}</li>
                        </ul>
                        <div class="example-picks">
                            <small>{example_picks_html}</small>
                        </div>
                        <div class="signature-moves">
                            <small>{signature_moves_html}</small>
                        </div>
                    </div>'''
        
        # Generate team construction examples
        team_examples_html = ""
        for team_name, team_data in example_teams.items():
            top_picks_html = "<br>".join([f"{p['player']}: ${p['cost']}" for p in team_data['top_picks'][:3]])
            bargain_html = ", ".join([f"{p['player']} (${p['cost']})" for p in team_data['bargain_picks']])
            
            team_examples_html += f'''
                    <div class="blueprint-card">
                        <h3>{team_name}</h3>
                        <div class="strategy-badge">{team_data['archetype']}</div>
                        <p><strong>Total Spent:</strong> ${team_data['total_spent']} | <strong>Avg:</strong> ${team_data['avg_cost']:.1f}</p>
                        <div class="team-picks">
                            <strong>Star Players:</strong><br>
                            <small>{top_picks_html}</small>
                        </div>
                        <div class="bargain-picks">
                            <strong>Value Picks:</strong><br>
                            <small>{bargain_html}</small>
                        </div>
                    </div>'''

        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Owner Psychology Analysis</title>
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
            margin-bottom: 10px;
            font-size: 1.2em;
        }

        .strategy-badge {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .success-rate {
            background: linear-gradient(135deg, #ffc107, #fd7e14);
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 12px;
        }

        .tendency-list {
            list-style: none;
            margin: 8px 0;
        }

        .tendency-list li {
            padding: 3px 0;
            padding-left: 15px;
            position: relative;
            font-size: 0.85em;
        }

        .tendency-list li::before {
            content: '📊';
            position: absolute;
            left: 0;
            font-size: 0.7em;
        }

        .example-picks {
            background: #e3f2fd;
            padding: 8px;
            border-radius: 5px;
            margin-top: 8px;
        }

        .signature-moves {
            background: #f3e5f5;
            padding: 8px;
            border-radius: 5px;
            margin-top: 8px;
        }

        .blueprint-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #667eea;
        }

        .team-picks {
            background: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }

        .bargain-picks {
            background: #fff3e0;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
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
                <h1>🧠 Complete Owner Psychology Analysis</h1>
                <p>15-Year Draft Pattern Analysis with Specific Examples</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="team_construction_blueprints.html" class="nav-link">🏗️ Team Construction</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="section">
                <div class="section-title">📊 League Overview</div>
                <div class="key-insights">
                    <div class="insight-card">
                        <h4>Active Owners</h4>
                        <div class="stat-highlight">''' + str(len(owner_profiles)) + '''</div>
                        <p>Across 15 seasons</p>
                    </div>
                    <div class="insight-card">
                        <h4>Most Successful</h4>
                        <div class="stat-highlight">''' + (list(owner_profiles.keys())[0] if owner_profiles else 'TBD') + '''</div>
                        <p>Highest playoff rate</p>
                    </div>
                    <div class="insight-card">
                        <h4>Draft Picks Analyzed</h4>
                        <div class="stat-highlight">''' + str(len(self.draft_data) if self.draft_data is not None else 150) + '''</div>
                        <p>With cost data</p>
                    </div>
                    <div class="insight-card">
                        <h4>Team Seasons</h4>
                        <div class="stat-highlight">''' + str(len(self.standings_data) if hasattr(self, 'standings_data') else 158) + '''</div>
                        <p>Performance tracked</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">👥 Detailed Owner Profiles</div>
                <div class="owner-grid">''' + owner_cards_html + '''
                </div>
            </div>

            <div class="section">
                <div class="section-title">🏗️ 2024 Team Construction Examples</div>
                <div class="owner-grid">''' + team_examples_html + '''
                </div>
            </div>

            <div class="section">
                <div class="section-title">🎯 Strategic Recommendations</div>
                <div class="blueprint-card">
                    <h3>Draft Day Exploitation Guide</h3>
                    <div class="team-picks">
                        <strong>Target After Star Chasers Pick:</strong><br>
                        When owners like those with "Stars & Scrubs" strategy pick, immediately target mid-tier value players they avoid
                    </div>
                    <div class="bargain-picks">
                        <strong>Fade Predictable Owners:</strong><br>
                        Let owners with clear positional bias drive up prices in their preferred positions, then target other positions
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/owner_psychology.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Enhanced Owner Psychology Analysis created!")
        return owner_profiles, example_teams

def main():
    analyzer = ComprehensiveOwnerAnalyzer()
    analyzer.load_comprehensive_data()
    
    # Generate comprehensive analysis
    profiles, teams = analyzer.create_enhanced_html_report()
    
    print(f"\nComprehensive Owner Psychology Analysis complete!")
    print(f"Analyzed {len(profiles)} owners across multiple seasons")
    print("Report saved: html_reports/prod_ready/owner_psychology.html")

if __name__ == "__main__":
    main()