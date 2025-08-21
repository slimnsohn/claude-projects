#!/usr/bin/env python3
"""
Create simple working version with just drafted players to reduce size.
"""

import json
import os

def create_simple_working():
    """Create working version with smaller dataset."""
    
    print("=== CREATING SIMPLE WORKING VERSION ===\n")
    
    try:
        # Load all data
        with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        
        with open('html_reports/data/insights.json', 'r', encoding='utf-8') as f:
            insights_data = json.load(f)
        
        with open('html_reports/data/metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Filter to only players with draft history (much smaller dataset)
        all_players = players_data['players']
        drafted_players = {}
        
        for player_id, player in all_players.items():
            if player.get('yahoo_draft_history') and len(player['yahoo_draft_history']) > 0:
                drafted_players[player_id] = player
        
        print(f"Filtered from {len(all_players)} to {len(drafted_players)} drafted players")
        
        # Load CSS
        with open('html_reports/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Create simple working HTML
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fantasy Basketball Analysis - Drafted Players</title>
    <style>
{css_content}

/* Additional styles */
.player-row {{
    cursor: pointer;
    transition: background-color 0.2s ease;
}}

.player-row:hover {{
    background-color: #f8f9fa;
}}

.player-row.expanded {{
    background-color: #e3f2fd;
}}

.player-details-row {{
    display: none;
    background: #f8f9fa;
}}

.player-row.expanded + .player-details-row {{
    display: table-row;
}}

.player-details-cell {{
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
}}

.expand-btn {{
    color: #667eea;
    font-size: 0.8em;
    transition: transform 0.3s ease;
}}

.player-row.expanded .expand-btn {{
    transform: rotate(180deg);
}}

.table-container {{
    overflow-x: auto;
    margin-top: 20px;
}}

.player-table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.player-table th,
.player-table td {{
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}}

.player-table th {{
    background: #f5f5f5;
    font-weight: 600;
    color: #333;
}}

.draft-history-table,
.season-stats-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 0.9em;
}}

.draft-history-table th,
.draft-history-table td,
.season-stats-table th,
.season-stats-table td {{
    padding: 8px 10px;
    text-align: center;
    border-bottom: 1px solid #e9ecef;
}}

.draft-history-table th,
.season-stats-table th {{
    background: #667eea;
    color: white;
    font-weight: 500;
}}

.value-high {{ color: #2e7d32; font-weight: bold; }}
.value-medium {{ color: #f57c00; }}
.value-low {{ color: #d32f2f; }}

    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🏀 Fantasy Basketball Analysis</h1>
                <p>Drafted Players Database ({len(drafted_players)} players)</p>
            </div>
            
            <div class="search-section">
                <div class="search-box">
                    <input 
                        type="text" 
                        id="player-search" 
                        class="search-input" 
                        placeholder="Search players by name..."
                    >
                    <span class="search-icon">🔍</span>
                </div>
                
                <div style="text-align: center; margin-top: 15px;">
                    <span id="result-count" style="color: #666; font-size: 0.9em;">Loading players...</span>
                </div>
            </div>
            
            <div id="player-grid">
                <div class="loading">Loading player data...</div>
            </div>
        </div>
    </div>
    
    <script>
        console.log('=== STARTING SIMPLE VERSION ===');
        
        // Embed drafted players data
        window.PLAYER_DATA = {json.dumps(drafted_players, separators=(',', ':'))};
        
        console.log('Data embedded:', Object.keys(window.PLAYER_DATA).length, 'players');
        
        // Simple app class
        class SimpleApp {{
            constructor() {{
                this.players = window.PLAYER_DATA || {{}};
                this.filteredPlayers = Object.entries(this.players);
                this.currentSearch = '';
                this.init();
            }}
            
            init() {{
                console.log('Initializing app with', Object.keys(this.players).length, 'players');
                this.setupSearch();
                this.renderPlayers();
            }}
            
            setupSearch() {{
                const searchInput = document.getElementById('player-search');
                if (searchInput) {{
                    searchInput.addEventListener('input', (e) => {{
                        this.currentSearch = e.target.value.toLowerCase();
                        this.filterPlayers();
                    }});
                }}
            }}
            
            filterPlayers() {{
                const allPlayers = Object.entries(this.players);
                
                if (this.currentSearch) {{
                    this.filteredPlayers = allPlayers.filter(([id, player]) => 
                        player.player_name && 
                        player.player_name.toLowerCase().includes(this.currentSearch)
                    );
                }} else {{
                    this.filteredPlayers = allPlayers;
                }}
                
                this.renderPlayers();
            }}
            
            renderPlayers() {{
                const container = document.getElementById('player-grid');
                const countElement = document.getElementById('result-count');
                
                if (!container) return;
                
                if (this.filteredPlayers.length === 0) {{
                    container.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>No players found.</p></div>';
                    if (countElement) countElement.textContent = 'No players found';
                    return;
                }}
                
                // Update count
                if (countElement) {{
                    countElement.textContent = `${{this.filteredPlayers.length}} players found`;
                }}
                
                // Sort by name
                const sortedPlayers = this.filteredPlayers.sort(([aId, a], [bId, b]) => {{
                    const aName = a.player_name || '';
                    const bName = b.player_name || '';
                    return aName.localeCompare(bName);
                }});
                
                // Create table
                let html = `
                    <div class="table-container">
                        <table class="player-table">
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Times Drafted</th>
                                    <th>Avg Cost</th>
                                    <th>Value Score</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                sortedPlayers.forEach(([playerId, player]) => {{
                    const playerName = player.player_name || `Player ${{playerId}}`;
                    const draftCount = player.yahoo_draft_history ? player.yahoo_draft_history.length : 0;
                    const avgCost = player.value_analysis && player.value_analysis.avg_cost ? 
                        '$' + player.value_analysis.avg_cost.toFixed(0) : '-';
                    const valueScore = player.value_analysis && player.value_analysis.value_score ? 
                        player.value_analysis.value_score.toFixed(2) : '-';
                    
                    let valueClass = '';
                    if (player.value_analysis && player.value_analysis.value_score) {{
                        if (player.value_analysis.value_score > 1.5) valueClass = 'value-high';
                        else if (player.value_analysis.value_score < 0.8) valueClass = 'value-low';
                        else valueClass = 'value-medium';
                    }}
                    
                    html += `
                        <tr class="player-row" data-player-id="${{playerId}}">
                            <td><strong>${{playerName}}</strong></td>
                            <td>${{draftCount}}</td>
                            <td>${{avgCost}}</td>
                            <td class="${{valueClass}}">${{valueScore}}</td>
                            <td><span class="expand-btn">▼</span></td>
                        </tr>
                        <tr class="player-details-row">
                            <td colspan="5" class="player-details-cell">
                                <div id="details-${{playerId}}">Click to load details...</div>
                            </td>
                        </tr>
                    `;
                }});
                
                html += '</tbody></table></div>';
                
                container.innerHTML = html;
                
                // Add click listeners
                container.querySelectorAll('.player-row').forEach(row => {{
                    row.addEventListener('click', () => {{
                        this.togglePlayer(row);
                    }});
                }});
            }}
            
            togglePlayer(row) {{
                const isExpanded = row.classList.contains('expanded');
                
                // Close all others
                document.querySelectorAll('.player-row.expanded').forEach(r => {{
                    r.classList.remove('expanded');
                }});
                
                if (!isExpanded) {{
                    row.classList.add('expanded');
                    
                    // Load details
                    const playerId = row.dataset.playerId;
                    const player = this.players[playerId];
                    const detailsEl = document.getElementById(`details-${{playerId}}`);
                    
                    if (detailsEl && player) {{
                        detailsEl.innerHTML = this.generateDetails(player);
                    }}
                }}
            }}
            
            generateDetails(player) {{
                let html = '<h4>📋 Draft History</h4>';
                
                if (player.yahoo_draft_history && player.yahoo_draft_history.length > 0) {{
                    html += '<table class="draft-history-table"><thead><tr><th>Year</th><th>Team</th><th>Cost</th><th>Pick</th></tr></thead><tbody>';
                    
                    player.yahoo_draft_history.forEach(draft => {{
                        html += `<tr>`;
                        html += `<td>${{draft.year}}</td>`;
                        html += `<td>${{draft.fantasy_team}}</td>`;
                        html += `<td>$${{draft.draft_cost}}</td>`;
                        html += `<td>#${{draft.pick_number}}</td>`;
                        html += `</tr>`;
                    }});
                    
                    html += '</tbody></table>';
                }} else {{
                    html += '<p>No draft history available</p>';
                }}
                
                // Season stats if available
                if (player.seasons && Object.keys(player.seasons).length > 0) {{
                    html += '<h4>📊 Recent Season Stats</h4>';
                    html += '<table class="season-stats-table"><thead><tr><th>Year</th><th>Team</th><th>GP</th><th>PPG</th><th>RPG</th><th>APG</th></tr></thead><tbody>';
                    
                    const seasons = Object.entries(player.seasons).sort(([a], [b]) => parseInt(b) - parseInt(a)).slice(0, 3);
                    
                    seasons.forEach(([year, season]) => {{
                        html += `<tr>`;
                        html += `<td>${{year}}</td>`;
                        html += `<td>${{season.team || '-'}}</td>`;
                        html += `<td>${{season.games_played || 0}}</td>`;
                        html += `<td>${{season.pts_pg ? season.pts_pg.toFixed(1) : '-'}}</td>`;
                        html += `<td>${{season.reb_pg ? season.reb_pg.toFixed(1) : '-'}}</td>`;
                        html += `<td>${{season.ast_pg ? season.ast_pg.toFixed(1) : '-'}}</td>`;
                        html += `</tr>`;
                    }});
                    
                    html += '</tbody></table>';
                }}
                
                return html;
            }}
        }}
        
        // Initialize when DOM loads
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('DOM loaded, starting simple app');
            new SimpleApp();
        }});
        
        console.log('Script setup complete');
    </script>
</body>
</html>'''

        # Write the file
        output_file = 'html_reports/simple_working.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Simple working version created: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
        print(f"Contains {len(drafted_players)} drafted players")
        
        # Also save the filtered data for debugging
        filtered_data = {'players': drafted_players}
        with open('html_reports/data/drafted_players.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=2)
        
        print("Also saved filtered data to: html_reports/data/drafted_players.json")
        
        return True
        
    except Exception as e:
        print(f"Error creating simple version: {e}")
        return False

if __name__ == "__main__":
    create_simple_working()