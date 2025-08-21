#!/usr/bin/env python3
"""
Create minimal test HTML to isolate the issue.
"""

import json
import os

def create_minimal_test():
    """Create minimal test to see what's going wrong."""
    
    print("=== CREATING MINIMAL TEST ===\n")
    
    # Load just a few players for testing
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    
    # Get first 3 players only
    all_players = players_data['players']
    test_players = {}
    
    count = 0
    for player_id, player in all_players.items():
        if count < 3:
            test_players[player_id] = player
            print(f"Test player {count+1}: {player.get('player_name', 'NO NAME')}")
            count += 1
        else:
            break
    
    # Create minimal HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Minimal Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .debug {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Minimal Player Data Test</h1>
    
    <div class="debug">
        <strong>Debug Info:</strong>
        <div id="debug-info">Initializing...</div>
    </div>
    
    <div id="player-count">Loading...</div>
    <div id="player-list">Loading players...</div>
    
    <script>
        // Step 1: Log that script is starting
        console.log('=== SCRIPT STARTING ===');
        
        // Step 2: Embed test data
        window.TEST_DATA = {json.dumps(test_players, separators=(',', ':'))};
        console.log('Test data embedded:', Object.keys(window.TEST_DATA).length, 'players');
        
        // Step 3: Update debug info
        function updateDebug(message) {{
            const debugEl = document.getElementById('debug-info');
            if (debugEl) {{
                debugEl.innerHTML += '<br>' + message;
            }}
            console.log('DEBUG:', message);
        }}
        
        // Step 4: Try to access and display data
        function loadTestData() {{
            updateDebug('loadTestData() called');
            
            try {{
                if (!window.TEST_DATA) {{
                    throw new Error('No TEST_DATA found');
                }}
                
                const players = window.TEST_DATA;
                const playerCount = Object.keys(players).length;
                
                updateDebug(`Found ${{playerCount}} players in TEST_DATA`);
                
                // Update count
                const countEl = document.getElementById('player-count');
                if (countEl) {{
                    countEl.textContent = `Found ${{playerCount}} test players`;
                }}
                
                // Create player table
                let html = '<table><thead><tr><th>Player Name</th><th>Has Seasons</th><th>Has Drafts</th></tr></thead><tbody>';
                
                Object.entries(players).forEach(([id, player]) => {{
                    const name = player.player_name || 'NO NAME';
                    const hasSeasons = player.seasons && Object.keys(player.seasons).length > 0;
                    const hasDrafts = player.yahoo_draft_history && player.yahoo_draft_history.length > 0;
                    
                    html += `<tr>`;
                    html += `<td>${{name}}</td>`;
                    html += `<td>${{hasSeasons ? 'Yes' : 'No'}}</td>`;
                    html += `<td>${{hasDrafts ? 'Yes' : 'No'}}</td>`;
                    html += `</tr>`;
                    
                    updateDebug(`Player: ${{name}}, Seasons: ${{hasSeasons}}, Drafts: ${{hasDrafts}}`);
                }});
                
                html += '</tbody></table>';
                
                // Update player list
                const listEl = document.getElementById('player-list');
                if (listEl) {{
                    listEl.innerHTML = html;
                }}
                
                updateDebug('Table created successfully');
                
            }} catch (error) {{
                updateDebug('ERROR: ' + error.message);
                console.error('Error in loadTestData:', error);
                
                const listEl = document.getElementById('player-list');
                if (listEl) {{
                    listEl.innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }}
            }}
        }}
        
        // Step 5: Wait for DOM and run test
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', () => {{
                updateDebug('DOM loaded, calling loadTestData()');
                loadTestData();
            }});
        }} else {{
            updateDebug('DOM already loaded, calling loadTestData()');
            loadTestData();
        }}
        
        updateDebug('Script setup complete');
    </script>
</body>
</html>'''
    
    # Write test file
    with open('html_reports/minimal_test.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Minimal test created: html_reports/minimal_test.html")
    print("This will help us see exactly where the issue is occurring.")

if __name__ == "__main__":
    create_minimal_test()