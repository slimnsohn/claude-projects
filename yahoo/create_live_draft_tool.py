#!/usr/bin/env python3
"""
Create Live Draft Tool

Interactive draft assistant that provides real-time recommendations
based on your team construction, remaining budget, and category needs.
"""

import json
import pandas as pd
from create_2025_projections import Fantasy2025Projector

def create_draft_tool_data():
    """Generate the data needed for the live draft tool."""
    print("Creating live draft tool data...")
    
    # Load projections
    projector = Fantasy2025Projector()
    projector.load_and_prepare_data()
    projector.define_feature_set()
    
    # Train model
    model_results, best_model = projector.train_models()
    
    # Generate projections
    projections = projector.generate_2025_projections(best_model)
    projections = projector.analyze_projection_categories(projections)
    
    # Filter for viable draft targets (have draft costs or high projections)
    draft_pool = projections[
        (projections['draft_cost_2024'] > 0) | 
        (projections['projected_2025_value'] > 400)
    ].copy()
    
    # Fill in missing draft costs with estimated values based on projections
    missing_cost_mask = draft_pool['draft_cost_2024'] == 0
    if missing_cost_mask.any():
        # Estimate costs based on projection tiers
        def estimate_cost(projection):
            if projection >= 700: return 60
            elif projection >= 650: return 45
            elif projection >= 600: return 35
            elif projection >= 550: return 25
            elif projection >= 500: return 15
            elif projection >= 450: return 8
            elif projection >= 400: return 4
            else: return 2
        
        draft_pool.loc[missing_cost_mask, 'draft_cost_2024'] = draft_pool.loc[missing_cost_mask, 'projected_2025_value'].apply(estimate_cost)
    
    # Sort by projection
    draft_pool = draft_pool.sort_values('projected_2025_value', ascending=False)
    
    print(f"Created draft pool with {len(draft_pool)} players")
    
    return draft_pool

def create_live_draft_html(draft_pool):
    """Create the interactive live draft tool HTML."""
    
    # Convert draft pool to JSON for JavaScript
    draft_data = []
    for _, player in draft_pool.iterrows():
        draft_data.append({
            'name': player['personName'],
            'team': player.get('teamTricode', 'N/A'),
            'projection': round(player['projected_2025_value']),
            'estimatedCost': round(player['draft_cost_2024']),
            'archetype': player.get('archetype', 'Balanced'),
            'games': int(player['games_played']),
            'pts': round(player.get('points_per_game_norm', 50)),
            'reb': round(player.get('rebounds_per_game_norm', 50)),
            'ast': round(player.get('assists_per_game_norm', 50)),
            'stl': round(player.get('steals_per_game_norm', 50)),
            'blk': round(player.get('blocks_per_game_norm', 50)),
            'threes': round(player.get('threepointers_per_game_norm', 50)),
            'fg_pct': round(player.get('field_goal_percentage_norm', 50)),
            'ft_pct': round(player.get('free_throw_percentage_norm', 50)),
            'to': round(player.get('turnovers_per_game_norm', 50))
        })
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Draft Assistant - 2025 Fantasy Basketball</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.4;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            height: calc(100vh - 20px);
        }}

        .main-panel {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            overflow-y: auto;
        }}

        .sidebar {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}

        .header h1 {{
            font-size: 2em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 5px;
        }}

        .nav-links {{
            text-align: center;
            margin-bottom: 20px;
        }}

        .nav-link {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 20px;
            margin: 0 5px;
            font-size: 0.9em;
            font-weight: 500;
        }}

        .draft-form {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #28a745;
        }}

        .form-row {{
            display: grid;
            grid-template-columns: 2fr 1fr auto;
            gap: 10px;
            align-items: end;
            margin-bottom: 15px;
        }}

        .form-group {{
            display: flex;
            flex-direction: column;
        }}

        .form-group label {{
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }}

        .form-group input {{
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
        }}

        .form-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .add-btn {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            height: fit-content;
        }}

        .add-btn:hover {{
            background: linear-gradient(135deg, #20c997, #17a2b8);
        }}

        .team-overview {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .budget-info {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}

        .budget-item {{
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }}

        .budget-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #28a745;
        }}

        .budget-label {{
            font-size: 0.9em;
            color: #666;
        }}

        .roster-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }}

        .roster-slot {{
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .roster-slot.filled {{
            background: #d4edda;
            border: 2px solid #28a745;
            border-style: solid;
        }}

        .player-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .player-info {{
            font-size: 0.9em;
            color: #666;
        }}

        .recommendations {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
            margin-bottom: 20px;
        }}

        .recommendations h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}

        .player-list {{
            flex: 1;
            overflow-y: auto;
            margin-top: 10px;
        }}

        .player-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .player-item:hover {{
            background: #f8f9fa;
            border-color: #667eea;
        }}

        .player-header {{
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 5px;
        }}

        .player-header strong {{
            color: #333;
        }}

        .player-projection {{
            color: #28a745;
            font-weight: bold;
        }}

        .player-cost {{
            color: #dc3545;
            font-weight: bold;
        }}

        .player-details {{
            font-size: 0.9em;
            color: #666;
        }}

        .category-bars {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}

        .category-item {{
            text-align: center;
            padding: 8px;
            background: white;
            border-radius: 6px;
        }}

        .category-name {{
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 3px;
        }}

        .category-bar {{
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
        }}

        .category-fill {{
            height: 100%;
            background: linear-gradient(90deg, #dc3545, #ffc107, #28a745);
            transition: width 0.3s ease;
        }}

        .remove-btn {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            margin-left: 10px;
        }}

        .filters {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }}

        .filter-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 10px;
        }}

        .filter-select {{
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
        }}

        @media (max-width: 1200px) {{
            .container {{
                grid-template-columns: 1fr;
                grid-template-rows: auto 1fr;
            }}
            
            .sidebar {{
                order: -1;
            }}
        }}

        .archetype-high {{ color: #28a745; }}
        .archetype-medium {{ color: #ffc107; }}
        .archetype-low {{ color: #dc3545; }}

        .urgent {{ 
            background: #f8d7da !important; 
            border-color: #dc3545 !important; 
        }}

        .toggle-buttons {{
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
        }}

        .toggle-btn {{
            flex: 1;
            padding: 8px 12px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            text-align: center;
            transition: all 0.2s ease;
        }}

        .toggle-btn.active {{
            background: #667eea;
            color: white;
        }}

        .toggle-btn:hover {{
            background: #f8f9fa;
        }}

        .toggle-btn.active:hover {{
            background: #5a6fd8;
        }}

        .team-tier {{
            background: linear-gradient(135deg, #17a2b8, #20c997);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            text-align: center;
        }}

        .team-tier.tier-elite {{
            background: linear-gradient(135deg, #28a745, #20c997);
        }}

        .team-tier.tier-strong {{
            background: linear-gradient(135deg, #28a745, #20c997);
        }}

        .team-tier.tier-good {{
            background: linear-gradient(135deg, #ffc107, #fd7e14);
        }}

        .team-tier.tier-weak {{
            background: linear-gradient(135deg, #dc3545, #e83e8c);
        }}

        .tier-title {{
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .tier-description {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-panel">
            <div class="header">
                <h1>🔴 Live Draft Assistant</h1>
                <p>Real-time team construction with 2025 projections</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">📊 2025 Projections</a>
                <a href="projections_explanation.html" class="nav-link">🔬 Model Explanation</a>
                <a href="index.html" class="nav-link">🏠 Dashboard</a>
            </div>

            <div class="draft-form">
                <h3>Add Your Pick</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label for="playerName">Player Name</label>
                        <input type="text" id="playerName" placeholder="Start typing player name..." list="playerSuggestions">
                        <datalist id="playerSuggestions"></datalist>
                    </div>
                    <div class="form-group">
                        <label for="playerCost">Cost ($)</label>
                        <input type="number" id="playerCost" placeholder="0" min="1" max="200">
                    </div>
                    <button class="add-btn" onclick="addPlayer()">Add Pick</button>
                </div>
            </div>

            <div class="team-overview">
                <h3>Your Team Status</h3>
                <div class="budget-info">
                    <div class="budget-item">
                        <div class="budget-value" id="totalSpent">$0</div>
                        <div class="budget-label">Spent</div>
                    </div>
                    <div class="budget-item">
                        <div class="budget-value" id="remainingBudget">$200</div>
                        <div class="budget-label">Remaining</div>
                    </div>
                    <div class="budget-item">
                        <div class="budget-value" id="totalProjection">0</div>
                        <div class="budget-label">Total Projection</div>
                    </div>
                    <div class="budget-item">
                        <div class="budget-value" id="avgProjection">0</div>
                        <div class="budget-label">Avg Projection</div>
                    </div>
                </div>

                <div class="category-bars">
                    <div class="category-item">
                        <div class="category-name">Scoring</div>
                        <div class="category-bar"><div class="category-fill" id="scoringBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">Rebounds</div>
                        <div class="category-bar"><div class="category-fill" id="reboundsBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">Assists</div>
                        <div class="category-bar"><div class="category-fill" id="assistsBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">Steals</div>
                        <div class="category-bar"><div class="category-fill" id="stealsBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">Blocks</div>
                        <div class="category-bar"><div class="category-fill" id="blocksBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">3-Pointers</div>
                        <div class="category-bar"><div class="category-fill" id="threesBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">FG%</div>
                        <div class="category-bar"><div class="category-fill" id="fgBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">FT%</div>
                        <div class="category-bar"><div class="category-fill" id="ftBar" style="width: 0%"></div></div>
                    </div>
                    <div class="category-item">
                        <div class="category-name">Low TOs</div>
                        <div class="category-bar"><div class="category-fill" id="toBar" style="width: 0%"></div></div>
                    </div>
                </div>
            </div>

            <div class="roster-section">
                <h3>Your Roster (15 players)</h3>
                <div class="roster-grid" id="rosterGrid">
                    <!-- Roster slots will be generated by JavaScript -->
                </div>
            </div>
        </div>

        <div class="sidebar">
            <div class="team-tier" id="teamTier">
                <div class="tier-title">Team Projection Tier</div>
                <div class="tier-description">Add players to see your team strength</div>
            </div>

            <div class="recommendations">
                <h3>🎯 Draft Recommendations</h3>
                <p id="recommendationText">Add your first player to get started!</p>
            </div>

            <div class="toggle-buttons">
                <div class="toggle-btn active" id="smartBtn" onclick="toggleRecommendationMode('smart')">Smart Picks</div>
                <div class="toggle-btn" id="valueBtn" onclick="toggleRecommendationMode('value')">Value Picks</div>
            </div>

            <div class="filters">
                <h4>Filter Targets</h4>
                <div class="filter-row">
                    <select class="filter-select" id="positionFilter" onchange="updateRecommendations()">
                        <option value="">All Archetypes</option>
                        <option value="Guard">Guards</option>
                        <option value="Big Man">Big Men</option>
                        <option value="Shooter">Shooters</option>
                        <option value="Balanced">Balanced</option>
                    </select>
                    <select class="filter-select" id="priceFilter" onchange="updateRecommendations()">
                        <option value="">All Prices</option>
                        <option value="1-5">$1-5</option>
                        <option value="6-15">$6-15</option>
                        <option value="16-30">$16-30</option>
                        <option value="31-50">$31-50</option>
                        <option value="51-100">$51+</option>
                    </select>
                </div>
            </div>

            <div class="player-list" id="recommendationsList">
                <!-- Recommendations will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let draftData = {json.dumps(draft_data)};
        let myTeam = [];
        let remainingBudget = 200;
        let draftedPlayers = new Set(); // Track all drafted players (yours + others)
        let recommendationMode = 'smart'; // 'smart' or 'value'

        // Initialize the application
        function initializeApp() {{
            generateRosterSlots();
            populatePlayerSuggestions();
            updateRecommendations();
            updateTeamStats();
            updateTeamTier();
        }}

        // Toggle between recommendation modes
        function toggleRecommendationMode(mode) {{
            recommendationMode = mode;
            
            // Update button states
            document.getElementById('smartBtn').classList.remove('active');
            document.getElementById('valueBtn').classList.remove('active');
            document.getElementById(mode + 'Btn').classList.add('active');
            
            // Update recommendations
            updateRecommendations();
        }}

        // Generate roster slots
        function generateRosterSlots() {{
            const rosterGrid = document.getElementById('rosterGrid');
            rosterGrid.innerHTML = '';
            
            for (let i = 0; i < 15; i++) {{
                const slot = document.createElement('div');
                slot.className = 'roster-slot';
                slot.id = `slot-${{i}}`;
                slot.innerHTML = `<div>Slot ${{i + 1}}</div><div class="player-info">Empty</div>`;
                rosterGrid.appendChild(slot);
            }}
        }}

        // Populate player name suggestions
        function populatePlayerSuggestions() {{
            const datalist = document.getElementById('playerSuggestions');
            draftData.forEach(player => {{
                const option = document.createElement('option');
                option.value = player.name;
                option.textContent = `${{player.name}} - ${{player.team}} (Proj: ${{player.projection}})`;
                datalist.appendChild(option);
            }});
        }}

        // Add player to team
        function addPlayer() {{
            const playerName = document.getElementById('playerName').value.trim();
            const playerCost = parseInt(document.getElementById('playerCost').value) || 0;
            
            if (!playerName || playerCost <= 0) {{
                alert('Please enter both player name and cost');
                return;
            }}
            
            if (myTeam.length >= 15) {{
                alert('Your roster is full!');
                return;
            }}
            
            if (playerCost > remainingBudget) {{
                alert(`Not enough budget! Remaining: $${{remainingBudget}}`);
                return;
            }}
            
            // Find player in draft data
            const playerData = draftData.find(p => 
                p.name.toLowerCase() === playerName.toLowerCase()
            );
            
            if (!playerData) {{
                // Allow manual entry for players not in our data
                const manualPlayer = {{
                    name: playerName,
                    team: 'N/A',
                    projection: 300, // Default projection
                    estimatedCost: playerCost,
                    archetype: 'Unknown',
                    pts: 50, reb: 50, ast: 50, stl: 50, blk: 50,
                    threes: 50, fg_pct: 50, ft_pct: 50, to: 50
                }};
                myTeam.push({{ ...manualPlayer, actualCost: playerCost }});
            }} else {{
                myTeam.push({{ ...playerData, actualCost: playerCost }});
            }}
            
            remainingBudget -= playerCost;
            
            // Clear form
            document.getElementById('playerName').value = '';
            document.getElementById('playerCost').value = '';
            
            // Update UI
            updateRoster();
            updateTeamStats();
            updateTeamTier();
            updateRecommendations();
        }}

        // Update roster display
        function updateRoster() {{
            myTeam.forEach((player, index) => {{
                const slot = document.getElementById(`slot-${{index}}`);
                slot.className = 'roster-slot filled';
                slot.innerHTML = `
                    <div class="player-name">${{player.name}}</div>
                    <div class="player-info">
                        ${{player.team}} - $${{player.actualCost}} - Proj: ${{player.projection}}
                        <button class="remove-btn" onclick="removePlayer(${{index}})">Remove</button>
                    </div>
                `;
            }});
        }}

        // Remove player from team
        function removePlayer(index) {{
            const player = myTeam[index];
            remainingBudget += player.actualCost;
            myTeam.splice(index, 1);
            
            // Reset all slots and repopulate
            generateRosterSlots();
            updateRoster();
            updateTeamStats();
            updateTeamTier();
            updateRecommendations();
        }}

        // Update team statistics
        function updateTeamStats() {{
            const totalSpent = 200 - remainingBudget;
            const totalProjection = myTeam.reduce((sum, p) => sum + p.projection, 0);
            const avgProjection = myTeam.length > 0 ? totalProjection / myTeam.length : 0;
            
            document.getElementById('totalSpent').textContent = `$${{totalSpent}}`;
            document.getElementById('remainingBudget').textContent = `$${{remainingBudget}}`;
            document.getElementById('totalProjection').textContent = totalProjection.toFixed(0);
            document.getElementById('avgProjection').textContent = avgProjection.toFixed(0);
            
            // Update category bars
            updateCategoryBars();
        }}

        // Update category strength bars
        function updateCategoryBars() {{
            if (myTeam.length === 0) {{
                const categories = ['scoring', 'rebounds', 'assists', 'steals', 'blocks', 'threes', 'fg', 'ft', 'to'];
                categories.forEach(cat => {{
                    document.getElementById(`${{cat}}Bar`).style.width = '0%';
                }});
                return;
            }}
            
            // Calculate team averages in each category
            const teamStats = {{
                scoring: myTeam.reduce((sum, p) => sum + p.pts, 0) / myTeam.length,
                rebounds: myTeam.reduce((sum, p) => sum + p.reb, 0) / myTeam.length,
                assists: myTeam.reduce((sum, p) => sum + p.ast, 0) / myTeam.length,
                steals: myTeam.reduce((sum, p) => sum + p.stl, 0) / myTeam.length,
                blocks: myTeam.reduce((sum, p) => sum + p.blk, 0) / myTeam.length,
                threes: myTeam.reduce((sum, p) => sum + p.threes, 0) / myTeam.length,
                fg: myTeam.reduce((sum, p) => sum + p.fg_pct, 0) / myTeam.length,
                ft: myTeam.reduce((sum, p) => sum + p.ft_pct, 0) / myTeam.length,
                to: myTeam.reduce((sum, p) => sum + (100 - p.to), 0) / myTeam.length
            }};
            
            // Update bars (percentile based, 50 = average)
            Object.keys(teamStats).forEach(category => {{
                const percentage = Math.min(100, Math.max(0, teamStats[category]));
                document.getElementById(`${{category}}Bar`).style.width = `${{percentage}}%`;
            }});
        }}

        // Update team tier based on total projection
        function updateTeamTier() {{
            const totalProjection = myTeam.reduce((sum, p) => sum + p.projection, 0);
            const remainingSlots = 15 - myTeam.length;
            const projectedTotal = totalProjection + (remainingSlots * 400); // Assume 400 avg for remaining slots
            
            const tierElement = document.getElementById('teamTier');
            let tierClass = '';
            let tierTitle = '';
            let tierDescription = '';
            
            // Define tiers based on projected final total
            if (projectedTotal >= 7500) {{
                tierClass = 'tier-elite';
                tierTitle = 'Elite Championship Tier';
                tierDescription = `Total: ${{totalProjection}} | Projected Final: ${{projectedTotal}} | Top 2 finish expected`;
            }} else if (projectedTotal >= 7000) {{
                tierClass = 'tier-strong';
                tierTitle = 'Strong Playoff Tier';
                tierDescription = `Total: ${{totalProjection}} | Projected Final: ${{projectedTotal}} | Top 4 finish likely`;
            }} else if (projectedTotal >= 6500) {{
                tierClass = 'tier-good';
                tierTitle = 'Solid Team Tier';
                tierDescription = `Total: ${{totalProjection}} | Projected Final: ${{projectedTotal}} | Playoff contender`;
            }} else {{
                tierClass = 'tier-weak';
                tierTitle = 'Needs Improvement';
                tierDescription = `Total: ${{totalProjection}} | Projected Final: ${{projectedTotal}} | Focus on high-value picks`;
            }}
            
            tierElement.className = `team-tier ${{tierClass}}`;
            tierElement.innerHTML = `
                <div class="tier-title">${{tierTitle}}</div>
                <div class="tier-description">${{tierDescription}}</div>
            `;
        }}

        // Update recommendations based on team needs
        function updateRecommendations() {{
            const availablePlayers = draftData.filter(player => 
                !myTeam.some(teamPlayer => teamPlayer.name === player.name) &&
                player.estimatedCost <= remainingBudget
            );
            
            // Apply filters
            const positionFilter = document.getElementById('positionFilter').value;
            const priceFilter = document.getElementById('priceFilter').value;
            
            let filteredPlayers = availablePlayers;
            
            if (positionFilter) {{
                filteredPlayers = filteredPlayers.filter(p => p.archetype === positionFilter);
            }}
            
            if (priceFilter) {{
                const [min, max] = priceFilter.split('-').map(Number);
                filteredPlayers = filteredPlayers.filter(p => {{
                    if (max) return p.estimatedCost >= min && p.estimatedCost <= max;
                    return p.estimatedCost >= min;
                }});
            }}
            
            // Sort based on recommendation mode
            if (recommendationMode === 'value') {{
                // Value mode: Sort by value per dollar
                filteredPlayers.forEach(player => {{
                    player.valuePerDollar = player.projection / player.estimatedCost;
                }});
                filteredPlayers.sort((a, b) => b.valuePerDollar - a.valuePerDollar);
            }} else {{
                // Smart mode: Sort by team fit + projection
                filteredPlayers.forEach(player => {{
                    player.smartScore = calculateSmartScore(player);
                }});
                filteredPlayers.sort((a, b) => b.smartScore - a.smartScore);
            }}
            
            // Generate recommendation text
            const needsAnalysis = analyzeTeamNeeds();
            document.getElementById('recommendationText').textContent = needsAnalysis;
            
            // Display top recommendations
            displayRecommendations(filteredPlayers.slice(0, 20));
        }}

        // Calculate smart score based on team fit and projection
        function calculateSmartScore(player) {{
            let score = player.projection; // Base score
            
            if (myTeam.length === 0) {{
                // First pick: Prioritize high projection
                return score;
            }}
            
            // Calculate team category averages
            const teamStats = {{
                pts: myTeam.reduce((sum, p) => sum + p.pts, 0) / myTeam.length,
                reb: myTeam.reduce((sum, p) => sum + p.reb, 0) / myTeam.length,
                ast: myTeam.reduce((sum, p) => sum + p.ast, 0) / myTeam.length,
                stl: myTeam.reduce((sum, p) => sum + p.stl, 0) / myTeam.length,
                blk: myTeam.reduce((sum, p) => sum + p.blk, 0) / myTeam.length,
                threes: myTeam.reduce((sum, p) => sum + p.threes, 0) / myTeam.length,
                fg_pct: myTeam.reduce((sum, p) => sum + p.fg_pct, 0) / myTeam.length,
                ft_pct: myTeam.reduce((sum, p) => sum + p.ft_pct, 0) / myTeam.length
            }};
            
            // Identify weakest categories (below 45th percentile)
            const weakCategories = [];
            Object.keys(teamStats).forEach(cat => {{
                if (teamStats[cat] < 45) {{
                    weakCategories.push(cat);
                }}
            }});
            
            // Boost score if player helps weak categories
            weakCategories.forEach(cat => {{
                if (player[cat] > 60) {{ // Player is strong in this category
                    score += (player[cat] - 50) * 2; // Bonus for addressing weakness
                }}
            }});
            
            // Budget consideration
            const remainingSlots = 15 - myTeam.length;
            const avgBudgetPerSlot = remainingBudget / remainingSlots;
            
            if (player.estimatedCost > avgBudgetPerSlot * 1.5) {{
                // Expensive relative to remaining budget
                score *= 0.9;
            }} else if (player.estimatedCost < avgBudgetPerSlot * 0.5) {{
                // Cheap relative to budget - good value
                score *= 1.1;
            }}
            
            return score;
        }}

        // Analyze what the team needs most
        function analyzeTeamNeeds() {{
            if (myTeam.length === 0) {{
                return "Start with a high-projection player to anchor your team!";
            }}
            
            const remainingSlots = 15 - myTeam.length;
            const avgBudgetPerSlot = remainingBudget / remainingSlots;
            
            if (myTeam.length >= 13) {{
                return `Final picks! Focus on filling category weaknesses with $${{avgBudgetPerSlot.toFixed(0)}} average budget.`;
            }}
            
            if (remainingBudget < 20 && remainingSlots > 5) {{
                return "Budget is tight! Look for high-value players under $5.";
            }}
            
            if (avgBudgetPerSlot > 25) {{
                return `Good budget remaining! Can afford premium players (~$${{avgBudgetPerSlot.toFixed(0)}} per slot).`;
            }}
            
            // Analyze category needs
            if (myTeam.length >= 3) {{
                const teamStats = {{
                    rebounds: myTeam.reduce((sum, p) => sum + p.reb, 0) / myTeam.length,
                    assists: myTeam.reduce((sum, p) => sum + p.ast, 0) / myTeam.length,
                    blocks: myTeam.reduce((sum, p) => sum + p.blk, 0) / myTeam.length,
                    steals: myTeam.reduce((sum, p) => sum + p.stl, 0) / myTeam.length
                }};
                
                const weakest = Object.entries(teamStats).sort((a, b) => a[1] - b[1])[0];
                return `Consider strengthening ${{weakest[0]}} (current strength: ${{weakest[1].toFixed(0)}}/100).`;
            }}
            
            return `${{remainingSlots}} slots remaining. Budget: $${{avgBudgetPerSlot.toFixed(0)}} per player average.`;
        }}

        // Display recommendation list
        function displayRecommendations(players) {{
            const container = document.getElementById('recommendationsList');
            container.innerHTML = '';
            
            players.forEach(player => {{
                const playerDiv = document.createElement('div');
                playerDiv.className = 'player-item';
                playerDiv.onclick = () => {{
                    document.getElementById('playerName').value = player.name;
                    document.getElementById('playerCost').value = player.estimatedCost;
                }};
                
                const valueDisplay = recommendationMode === 'value' ? 
                    ` • Value: ${{(player.projection / player.estimatedCost).toFixed(1)}}` : '';
                
                playerDiv.innerHTML = `
                    <div class="player-header">
                        <strong>${{player.name}}</strong>
                        <span class="player-projection">${{player.projection}}</span>
                    </div>
                    <div class="player-details">
                        ${{player.team}} • ${{player.archetype}} • <span class="player-cost">$${{player.estimatedCost}}</span>${{valueDisplay}}
                    </div>
                `;
                
                container.appendChild(playerDiv);
            }});
        }}

        // Initialize app when page loads
        document.addEventListener('DOMContentLoaded', initializeApp);
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Create the live draft tool."""
    print("=== CREATING LIVE DRAFT TOOL ===")
    
    try:
        # Generate draft data
        draft_pool = create_draft_tool_data()
        
        # Create HTML
        html_content = create_live_draft_html(draft_pool)
        
        # Save file
        output_path = 'html_reports/prod_ready/live_draft_tool.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Live draft tool created: {output_path}")
        print(f"Draft pool includes {len(draft_pool)} players")
        print("\nFeatures:")
        print("- Real-time budget tracking")
        print("- Category strength analysis")
        print("- Smart recommendations based on team needs")
        print("- Player search with autocomplete")
        print("- 15-player roster management")
        
    except Exception as e:
        print(f"Error creating live draft tool: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()