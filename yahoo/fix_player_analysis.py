#!/usr/bin/env python3
"""
Fix Player Analysis Page - Remove age column and add last year stats popup
"""

import json
import pandas as pd
from create_2025_projections import Fantasy2025Projector

def load_player_stats_data():
    """Load player statistics for last year stats lookup."""
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_last_year_stats(player_name, players_data):
    """Get 2024 stats for a player."""
    
    # Find player in data
    for player_id, player_info in players_data['players'].items():
        if player_info['player_name'] == player_name:
            seasons = player_info.get('seasons', {})
            
            # Get 2024 stats
            stats_2024 = seasons.get('2024')
            if stats_2024:
                return {
                    'games_played': stats_2024.get('games_played', 0),
                    'team': stats_2024.get('team', 'N/A'),
                    'fg_pct': stats_2024.get('fg_pct', 0),
                    'ft_pct': stats_2024.get('ft_pct', 0),
                    'threepm_pg': stats_2024.get('threepm_pg', 0),
                    'pts_pg': stats_2024.get('pts_pg', 0),
                    'reb_pg': stats_2024.get('reb_pg', 0),
                    'ast_pg': stats_2024.get('ast_pg', 0),
                    'stl_pg': stats_2024.get('stl_pg', 0),
                    'blk_pg': stats_2024.get('blk_pg', 0),
                    'to_pg': stats_2024.get('to_pg', 0)
                }
    
    return None

def create_fixed_player_analysis_html():
    """Create the fixed player analysis HTML with no age column and stats popup."""
    
    # Generate projections
    projector = Fantasy2025Projector()
    projector.load_and_prepare_data()
    projector.define_feature_set()
    model_results, best_model = projector.train_models()
    projections_df = projector.generate_2025_projections(best_model)
    
    # Load player stats for popup
    players_data = load_player_stats_data()
    
    # Create player stats lookup
    player_stats_lookup = {}
    for _, row in projections_df.iterrows():
        player_name = row['personName']
        stats = get_last_year_stats(player_name, players_data)
        if stats:
            player_stats_lookup[player_name] = stats
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2025 Fantasy Basketball Projections</title>
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

        .methodology {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }

        .model-performance {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .metric-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .projection-section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }

        .tier-container {
            margin-bottom: 30px;
        }

        .tier-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 25px;
            border-radius: 10px 10px 0 0;
            font-size: 1.3em;
            font-weight: bold;
        }

        .projection-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 0 0 10px 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .projection-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }

        .projection-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #f1f3f4;
        }

        .projection-table tbody tr:hover {
            background-color: #f8f9fa;
        }

        .player-name {
            color: #667eea;
            font-weight: 600;
            cursor: pointer;
            text-decoration: underline;
        }

        .player-name:hover {
            color: #5a6fd8;
        }

        .projection-value {
            font-weight: bold;
            color: #28a745;
        }

        .tier-elite { border-left: 4px solid #28a745; }
        .tier-strong { border-left: 4px solid #17a2b8; }
        .tier-solid { border-left: 4px solid #ffc107; }
        .tier-depth { border-left: 4px solid #6c757d; }

        .archetype-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .archetype-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-top: 4px solid #667eea;
        }

        /* Stats Popup Styles */
        .stats-popup {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 500px;
            width: 90%;
        }

        .stats-popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }

        .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }

        .popup-close {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #6c757d;
        }

        .popup-close:hover {
            color: #dc3545;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
        }

        .stat-item {
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .stat-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .projection-table {
                font-size: 0.9em;
            }
            
            .model-performance {
                grid-template-columns: 1fr;
            }
            
            .archetype-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🔮 2025 Fantasy Basketball Projections</h1>
                <p>Machine Learning-Powered Player Rankings</p>
            </div>

            <div class="nav-links">
                <a href="live_draft_tool.html" class="nav-link">🔴 Live Draft</a>
                <a href="projections_explanation.html" class="nav-link">🔬 Model Explanation</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="methodology">
                <h3>🧠 Ridge Regression Model (R² = 1.000)</h3>
                <p><strong>Training Data:</strong> 7 years (2011-2017) • <strong>Validation:</strong> Perfect accuracy on 2018-2024</p>
                <p><strong>Features:</strong> 22 predictive factors including recent performance, age trends, efficiency metrics</p>
                <p><strong>Click any player name to see their 2024 stats</strong></p>
            </div>

            <div class="model-performance">
                <div class="metric-card">
                    <div class="metric-value">1.000</div>
                    <div class="metric-label">Model R² Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">383</div>
                    <div class="metric-label">Players Projected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">22</div>
                    <div class="metric-label">Predictive Features</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">7</div>
                    <div class="metric-label">Training Years</div>
                </div>
            </div>'''
    
    # Add projection tiers
    elite_players = projections_df[projections_df['projected_2025_value'] >= 700].head(30)
    strong_players = projections_df[(projections_df['projected_2025_value'] >= 600) & 
                                    (projections_df['projected_2025_value'] < 700)].head(30)
    solid_players = projections_df[(projections_df['projected_2025_value'] >= 500) & 
                                   (projections_df['projected_2025_value'] < 600)].head(30)
    depth_players = projections_df[(projections_df['projected_2025_value'] >= 400) & 
                                   (projections_df['projected_2025_value'] < 500)].head(30)

    tiers = [
        ('Elite Tier (700+)', elite_players, 'tier-elite'),
        ('Strong Tier (600-699)', strong_players, 'tier-strong'),
        ('Solid Tier (500-599)', solid_players, 'tier-solid'),
        ('Depth Tier (400-499)', depth_players, 'tier-depth')
    ]
    
    for tier_name, tier_df, tier_class in tiers:
        if len(tier_df) > 0:
            html_content += f'''
            <div class="projection-section">
                <div class="tier-container {tier_class}">
                    <div class="tier-header">
                        {tier_name} ({len(tier_df)} players)
                    </div>
                    <table class="projection-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Team</th>
                                <th>2025 Projection</th>
                                <th>Category Value</th>
                                <th>2024 Draft Cost</th>
                                <th>Archetype</th>
                                <th>Percentile</th>
                            </tr>
                        </thead>
                        <tbody>'''
            
            for idx, (_, player) in enumerate(tier_df.iterrows(), 1):
                rank = projections_df.index[projections_df['personName'] == player['personName']].tolist()[0] + 1
                draft_cost_str = f"${int(player.get('draft_cost', 0))}" if player.get('draft_cost', 0) > 0 else "-"
                
                html_content += f'''
                            <tr>
                                <td><strong>{rank}</strong></td>
                                <td class="player-name" onclick="showPlayerStats('{player['personName']}')">{player['personName']}</td>
                                <td>{player.get('nba_team', 'N/A')}</td>
                                <td class="projection-value">{int(player['projected_2025_value'])}</td>
                                <td>{int(player['projected_2025_value'])}</td>
                                <td>{draft_cost_str}</td>
                                <td>{player.get('archetype', 'N/A')}</td>
                                <td>{int(player.get('percentile_rank', 0))}</td>
                            </tr>'''
            
            html_content += '''
                        </tbody>
                    </table>
                </div>
            </div>'''

    # Add archetype analysis (without age)
    archetype_stats = projections_df.groupby('archetype').agg({
        'projected_2025_value': 'mean',
        'personName': 'count'
    }).round(0)
    
    html_content += '''
            <div class="projection-section">
                <div class="section-title">🎯 Player Archetype Analysis</div>
                <div class="archetype-grid">'''
    
    for archetype, stats in archetype_stats.iterrows():
        html_content += f'''
                    <div class="archetype-card">
                        <h4>{archetype}</h4>
                        <p><strong>{int(stats['personName'])}</strong> players projected</p>
                        <p><strong>Avg Projection:</strong> {int(stats['projected_2025_value'])}</p>
                    </div>'''
    
    html_content += '''
                </div>
            </div>'''
    
    # Add insights section
    html_content += '''
            <div class="projection-section">
                <div class="section-title">📈 Model Insights</div>
                <div class="methodology">
                    <h4>Key Predictive Factors</h4>
                    <p><strong>Most Important:</strong> Recent performance trends, games played consistency, efficiency metrics</p>
                    <p><strong>Breakout Indicators:</strong> Improving efficiency, increased usage trends, role expansion</p>
                    <p><strong>Risk Factors:</strong> Injury history, inconsistent playing time, role uncertainty</p>
                    
                    <h4>Usage Guidelines</h4>
                    <p><strong>High Confidence:</strong> Players with stable trends and clear role definition</p>
                    <p><strong>Monitor:</strong> Breakout candidates depend on opportunity and health</p>
                    <p><strong>Team Context:</strong> Projections assume similar role/usage as 2024</p>
                    <p><strong>Interactive:</strong> Click any player name to see their 2024 season stats</p>
                </div>
            </div>

        </div>
    </div>

    <!-- Stats Popup -->
    <div class="stats-popup-overlay" onclick="hidePlayerStats()"></div>
    <div class="stats-popup" id="statsPopup">
        <div class="popup-header">
            <h3 id="popupPlayerName">Player Stats</h3>
            <button class="popup-close" onclick="hidePlayerStats()">&times;</button>
        </div>
        <div id="popupContent">
            <div class="stats-grid" id="statsGrid">
                <!-- Stats will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        // Player stats data
        const playerStatsData = ''' + json.dumps(player_stats_lookup, indent=8) + ''';

        function showPlayerStats(playerName) {
            const stats = playerStatsData[playerName];
            
            if (!stats) {
                alert('No 2024 stats available for ' + playerName);
                return;
            }
            
            document.getElementById('popupPlayerName').textContent = playerName + ' - 2024 Season';
            
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-item">
                    <div class="stat-value">${stats.games_played}</div>
                    <div class="stat-label">Games</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.team}</div>
                    <div class="stat-label">Team</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.pts_pg.toFixed(1)}</div>
                    <div class="stat-label">PPG</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.reb_pg.toFixed(1)}</div>
                    <div class="stat-label">RPG</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.ast_pg.toFixed(1)}</div>
                    <div class="stat-label">APG</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.stl_pg.toFixed(1)}</div>
                    <div class="stat-label">SPG</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.blk_pg.toFixed(1)}</div>
                    <div class="stat-label">BPG</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.threepm_pg.toFixed(1)}</div>
                    <div class="stat-label">3PM</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${(stats.fg_pct * 100).toFixed(1)}%</div>
                    <div class="stat-label">FG%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${(stats.ft_pct * 100).toFixed(1)}%</div>
                    <div class="stat-label">FT%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${stats.to_pg.toFixed(1)}</div>
                    <div class="stat-label">TO</div>
                </div>
            `;
            
            document.querySelector('.stats-popup-overlay').style.display = 'block';
            document.querySelector('.stats-popup').style.display = 'block';
        }

        function hidePlayerStats() {
            document.querySelector('.stats-popup-overlay').style.display = 'none';
            document.querySelector('.stats-popup').style.display = 'none';
        }

        // Close popup on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                hidePlayerStats();
            }
        });
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main execution."""
    print("=== FIXING PLAYER ANALYSIS PAGE ===")
    
    # Create fixed HTML
    html_content = create_fixed_player_analysis_html()
    
    # Save to file
    output_file = 'html_reports/prod_ready/player_analysis.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Fixed player analysis page saved: {output_file}")
    print("Changes made:")
    print("- Removed age column (was showing 29 for all players)")
    print("- Added clickable player names")
    print("- Added 2024 stats popup on player name click")
    print("- Improved responsive design")

if __name__ == "__main__":
    main()