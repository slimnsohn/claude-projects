#!/usr/bin/env python3
"""
Debug the standalone HTML expandable issue.
"""

import json
import os

def debug_player_data():
    """Debug player data to find the issue."""
    
    print("=== DEBUGGING PLAYER DATA ===\n")
    
    # Load player data
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    players = players_data['players']
    print(f"Total players: {len(players)}")
    
    # Check a few players for completeness
    test_players = list(players.items())[:5]
    
    for player_id, player in test_players:
        print(f"\nPlayer: {player.get('player_name', 'NO NAME')} (ID: {player_id})")
        print(f"  Has seasons: {'seasons' in player and len(player.get('seasons', {})) > 0}")
        print(f"  Has draft history: {'yahoo_draft_history' in player and len(player.get('yahoo_draft_history', [])) > 0}")
        print(f"  Has career summary: {'career_summary' in player}")
        print(f"  Has value analysis: {'value_analysis' in player}")
        
        if 'seasons' in player:
            seasons = player['seasons']
            print(f"  Season count: {len(seasons)}")
            if seasons:
                first_season = list(seasons.values())[0]
                print(f"  Sample season keys: {list(first_season.keys())[:5]}")
        
        if 'yahoo_draft_history' in player:
            drafts = player['yahoo_draft_history']
            print(f"  Draft count: {len(drafts)}")
            if drafts:
                first_draft = drafts[0]
                print(f"  Sample draft keys: {list(first_draft.keys())}")
    
    # Find players with both data
    players_with_both = []
    players_with_seasons_only = []
    players_with_drafts_only = []
    players_with_neither = []
    
    for player_id, player in players.items():
        has_seasons = 'seasons' in player and len(player.get('seasons', {})) > 0
        has_drafts = 'yahoo_draft_history' in player and len(player.get('yahoo_draft_history', [])) > 0
        
        if has_seasons and has_drafts:
            players_with_both.append(player['player_name'])
        elif has_seasons:
            players_with_seasons_only.append(player['player_name'])
        elif has_drafts:
            players_with_drafts_only.append(player['player_name'])
        else:
            players_with_neither.append(player['player_name'])
    
    print(f"\n=== DATA SUMMARY ===")
    print(f"Players with both seasons & drafts: {len(players_with_both)}")
    print(f"Players with seasons only: {len(players_with_seasons_only)}")
    print(f"Players with drafts only: {len(players_with_drafts_only)}")
    print(f"Players with neither: {len(players_with_neither)}")
    
    if players_with_both:
        print(f"\nFirst 3 players with both: {players_with_both[:3]}")
    
    return players_with_both[0] if players_with_both else None

def create_simple_test_html(test_player_name):
    """Create a simple test HTML to debug the issue."""
    
    print(f"\n=== CREATING TEST HTML ===")
    
    # Load minimal data
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    # Find the test player
    test_player = None
    test_id = None
    for player_id, player in players_data['players'].items():
        if player.get('player_name') == test_player_name:
            test_player = player
            test_id = player_id
            break
    
    if not test_player:
        print("Test player not found!")
        return
    
    print(f"Found test player: {test_player_name}")
    
    # Create minimal HTML with just one player
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Debug Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .player-row {{ 
            background: #f0f0f0; 
            padding: 10px; 
            margin: 5px 0; 
            cursor: pointer; 
            border-radius: 5px;
        }}
        .player-row.expanded {{ background: #e3f2fd; }}
        .player-details-row {{ 
            display: none; 
            background: #f8f9fa; 
            padding: 20px; 
            margin: 5px 0;
            border-radius: 5px;
        }}
        .player-row.expanded + .player-details-row {{ display: block; }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 10px 0;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 8px; 
            text-align: left;
        }}
        th {{ background: #667eea; color: white; }}
    </style>
</head>
<body>
    <h1>Debug Test - Expandable Player</h1>
    
    <div class="player-row" onclick="togglePlayer(this)">
        <strong>{test_player_name}</strong> - Click to expand
    </div>
    
    <div class="player-details-row">
        <div id="player-details">Loading details...</div>
    </div>
    
    <script>
        const playerData = {json.dumps(test_player, indent=2)};
        
        function togglePlayer(row) {{
            console.log('Toggle clicked');
            row.classList.toggle('expanded');
            
            if (row.classList.contains('expanded')) {{
                renderPlayerDetails();
            }}
        }}
        
        function renderPlayerDetails() {{
            console.log('Rendering details for:', playerData.player_name);
            console.log('Player data:', playerData);
            
            const container = document.getElementById('player-details');
            let html = '<h3>Player Details</h3>';
            
            // Draft History
            if (playerData.yahoo_draft_history && playerData.yahoo_draft_history.length > 0) {{
                html += '<h4>Draft History (' + playerData.yahoo_draft_history.length + ' drafts)</h4>';
                html += '<table><thead><tr><th>Year</th><th>Team</th><th>Cost</th><th>Pick</th></tr></thead><tbody>';
                
                playerData.yahoo_draft_history.forEach(draft => {{
                    html += '<tr>';
                    html += '<td>' + draft.year + '</td>';
                    html += '<td>' + draft.fantasy_team + '</td>';
                    html += '<td>$' + draft.draft_cost + '</td>';
                    html += '<td>#' + draft.pick_number + '</td>';
                    html += '</tr>';
                }});
                
                html += '</tbody></table>';
            }} else {{
                html += '<p>No draft history available</p>';
            }}
            
            // Season Stats
            if (playerData.seasons && Object.keys(playerData.seasons).length > 0) {{
                const seasons = Object.entries(playerData.seasons).sort(([a], [b]) => parseInt(b) - parseInt(a));
                html += '<h4>Season Stats (' + seasons.length + ' seasons)</h4>';
                html += '<table><thead><tr><th>Year</th><th>Team</th><th>GP</th><th>PPG</th><th>RPG</th><th>APG</th></tr></thead><tbody>';
                
                seasons.forEach(([year, season]) => {{
                    html += '<tr>';
                    html += '<td>' + year + '</td>';
                    html += '<td>' + (season.team || '-') + '</td>';
                    html += '<td>' + (season.games_played || 0) + '</td>';
                    html += '<td>' + (season.pts_pg ? season.pts_pg.toFixed(1) : '-') + '</td>';
                    html += '<td>' + (season.reb_pg ? season.reb_pg.toFixed(1) : '-') + '</td>';
                    html += '<td>' + (season.ast_pg ? season.ast_pg.toFixed(1) : '-') + '</td>';
                    html += '</tr>';
                }});
                
                html += '</tbody></table>';
            }} else {{
                html += '<p>No season stats available</p>';
            }}
            
            container.innerHTML = html;
        }}
        
        console.log('Test page loaded');
        console.log('Player data loaded:', playerData.player_name);
    </script>
</body>
</html>'''
    
    # Write test file
    with open('html_reports/debug_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Debug test created: html_reports/debug_test.html")

def main():
    """Main debug function."""
    
    test_player = debug_player_data()
    if test_player:
        create_simple_test_html(test_player)
    else:
        print("No suitable test player found!")

if __name__ == "__main__":
    main()