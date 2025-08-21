#!/usr/bin/env python3
"""
Fix both the standalone.html loading issue and draft names for all years.
"""

import json
import os

def add_player_names_to_all_drafts():
    """Add player names to all draft files for all years."""
    
    print("=== ADDING PLAYER NAMES TO ALL DRAFT FILES ===\n")
    
    # Load comprehensive player name mapping
    player_names = {}
    
    # Load from web data
    web_file = 'html_reports/data/players.json'
    if os.path.exists(web_file):
        with open(web_file, 'r', encoding='utf-8') as f:
            web_data = json.load(f)
        
        players = web_data.get('players', {})
        
        for player_id, player_data in players.items():
            player_name = player_data.get('player_name', f'Player {player_id}')
            player_names[player_id] = player_name
            
            # Also map Yahoo IDs from draft history
            if 'yahoo_draft_history' in player_data:
                for draft_entry in player_data['yahoo_draft_history']:
                    yahoo_id = str(draft_entry.get('yahoo_id', ''))
                    if yahoo_id:
                        player_names[yahoo_id] = player_name
        
        print(f"Loaded {len(player_names)} player name mappings")
    
    # Also load NBA mapping as backup
    nba_file = 'historical_nba_stats/player_mappings/nba_player_mapping.json'
    if os.path.exists(nba_file):
        with open(nba_file, 'r', encoding='utf-8') as f:
            nba_data = json.load(f)
        
        for player_id, player_info in nba_data.items():
            if player_id not in player_names:
                player_names[player_id] = player_info.get('name', f'Player {player_id}')
        
        print(f"Added NBA names, total: {len(player_names)} mappings")
    
    # Process all years
    fixed_years = []
    total_picks_updated = 0
    
    for year in range(2010, 2025):
        draft_file = f'league_data/{year}/processed_data/draft_analysis.json'
        if os.path.exists(draft_file):
            print(f"Processing {year}...")
            
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft_data = json.load(f)
                
                picks_updated = 0
                total_picks = len(draft_data.get('picks', []))
                
                for pick in draft_data.get('picks', []):
                    player_id = str(pick['player_id'])
                    
                    # Try to find player name
                    if player_id in player_names:
                        pick['player_name'] = player_names[player_id]
                        picks_updated += 1
                    else:
                        # Try without the string conversion
                        if pick['player_id'] in player_names:
                            pick['player_name'] = player_names[pick['player_id']]
                            picks_updated += 1
                        else:
                            # Fallback name
                            pick['player_name'] = f"Player {player_id}"
                
                # Save updated data
                with open(draft_file, 'w', encoding='utf-8') as f:
                    json.dump(draft_data, f, indent=2, ensure_ascii=False)
                
                print(f"  Updated {picks_updated}/{total_picks} player names")
                fixed_years.append(year)
                total_picks_updated += picks_updated
                
            except Exception as e:
                print(f"  Error processing {year}: {e}")
    
    print(f"\\nFixed {len(fixed_years)} years with {total_picks_updated} total picks updated")
    return fixed_years

def debug_standalone_html():
    """Debug the standalone HTML issue."""
    
    print("\\n=== DEBUGGING STANDALONE HTML ===\\n")
    
    # Check if the data files are correct
    files_to_check = [
        'html_reports/data/players.json',
        'html_reports/data/insights.json',
        'html_reports/data/metadata.json',
        'html_reports/data/player_index.json'
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'players.json' in file_path:
                    if 'players' in data:
                        print(f"✓ {file_path}: {len(data['players'])} players")
                    else:
                        print(f"✗ {file_path}: Missing 'players' key")
                        all_good = False
                else:
                    print(f"✓ {file_path}: OK")
                    
            except Exception as e:
                print(f"✗ {file_path}: Error - {e}")
                all_good = False
        else:
            print(f"✗ {file_path}: Not found")
            all_good = False
    
    # Create a simple test HTML to verify the issue
    test_html = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<div id="result">Loading...</div>
<script>
window.TEST_DATA = {"test": "value"};
document.getElementById('result').textContent = 'Data loaded: ' + JSON.stringify(window.TEST_DATA);
</script>
</body>
</html>'''
    
    with open('html_reports/test.html', 'w') as f:
        f.write(test_html)
    
    print(f"\\nTest HTML created: html_reports/test.html")
    print(f"Data files status: {'All OK' if all_good else 'Issues found'}")
    
    return all_good

def regenerate_standalone_html_fixed():
    """Regenerate standalone HTML with better error handling."""
    
    print("\\n=== REGENERATING STANDALONE HTML ===\\n")
    
    try:
        # Load all data files with error checking
        print("Loading data files...")
        
        with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        print(f"  Players: {len(players_data.get('players', {}))} loaded")
        
        with open('html_reports/data/insights.json', 'r', encoding='utf-8') as f:
            insights_data = json.load(f)
        print(f"  Insights: {len(insights_data)} categories")
        
        with open('html_reports/data/metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"  Metadata: {metadata.get('total_players', 'unknown')} players")
        
        with open('html_reports/data/player_index.json', 'r', encoding='utf-8') as f:
            player_index = json.load(f)
        print(f"  Index: {len(player_index)} entries")
        
        # Load the CSS and JS files
        with open('html_reports/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        with open('html_reports/js/app.js', 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Create a simplified HTML with better data embedding
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fantasy Basketball Analysis - Player Database</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <!-- Page Header -->
            <div class="page-header">
                <h1>🏀 Fantasy Basketball Analysis</h1>
                <p>15-Year Player Database & Insights (2010-2024)</p>
            </div>
            
            <!-- Navigation Tabs -->
            <div class="nav-tabs">
                <button class="nav-tab active" data-tab="players-tab">Player Database</button>
                <button class="nav-tab" data-tab="insights-tab">Analysis & Insights</button>
                <a href="draft_results_standalone.html" class="nav-tab nav-link">📋 Draft Results by Year</a>
            </div>
            
            <!-- Players Tab Content -->
            <div id="players-tab" class="tab-content active">
                <!-- Search Section -->
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
                    
                    <div class="search-filters">
                        <span class="filter-chip active" data-filter="all">All Players</span>
                        <span class="filter-chip" data-filter="drafted">Drafted in League</span>
                        <span class="filter-chip" data-filter="high-value">High Value (>1.5)</span>
                        <span class="filter-chip" data-filter="consistent">Long Career (5+ seasons)</span>
                        <span class="filter-chip" data-filter="recent">Recent Players (2022+)</span>
                    </div>
                    
                    <div style="text-align: center; margin-top: 15px;">
                        <span id="result-count" style="color: #666; font-size: 0.9em;">Loading players...</span>
                    </div>
                </div>
                
                <!-- Player Table -->
                <div id="player-grid">
                    <div class="loading">Loading player data...</div>
                </div>
            </div>
            
            <!-- Insights Tab Content -->
            <div id="insights-tab" class="tab-content">
                <!-- Summary Cards -->
                <div id="summary-cards" class="summary-cards">
                    <div class="loading">Loading summary...</div>
                </div>
                
                <!-- Insights Grid -->
                <div class="insights-grid">
                    <!-- Top Values -->
                    <div class="insight-card">
                        <h3>🎯 Best Values</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Players who provided the most production relative to their draft cost
                        </p>
                        <ul id="top-values-list" class="insight-list">
                            <li class="loading">Loading top values...</li>
                        </ul>
                    </div>
                    
                    <!-- Consistent Performers -->
                    <div class="insight-card">
                        <h3>📊 Most Consistent</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Players with low variance in scoring, providing reliable production
                        </p>
                        <ul id="consistent-list" class="insight-list">
                            <li class="loading">Loading consistent performers...</li>
                        </ul>
                    </div>
                    
                    <!-- Biggest Disappointments -->
                    <div class="insight-card">
                        <h3>📉 Biggest Busts</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 0.9em;">
                            Expensive players who underperformed relative to their draft cost
                        </p>
                        <ul id="busts-list" class="insight-list">
                            <li class="loading">Loading bust analysis...</li>
                        </ul>
                    </div>
                    
                    <!-- Draft Strategy Insights -->
                    <div class="insight-card">
                        <h3>💡 Key Insights</h3>
                        <div style="color: #666; font-size: 0.9em; line-height: 1.6;">
                            <h4 style="color: #333; margin: 15px 0 10px 0;">Player Value Patterns:</h4>
                            <ul style="padding-left: 20px;">
                                <li><strong>Value Score Formula:</strong> (Points + Rebounds + Assists - Turnovers) / Average Cost × 10</li>
                                <li><strong>High Value:</strong> Score > 1.5 indicates excellent value</li>
                                <li><strong>Poor Value:</strong> Score < 0.8 suggests overpaying</li>
                                <li><strong>Consistent Players:</strong> Low scoring variance over 3+ seasons</li>
                            </ul>
                            
                            <h4 style="color: #333; margin: 15px 0 10px 0;">Draft Strategy Recommendations:</h4>
                            <ul style="padding-left: 20px;">
                                <li>Target players with consistently high value scores across multiple seasons</li>
                                <li>Avoid paying premium prices for players with high variance</li>
                                <li>Look for players coming off "down" years who may be undervalued</li>
                                <li>Consider games played - availability is crucial for fantasy success</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Data Coverage Info -->
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px; text-align: center;">
                    <h4 style="color: #333; margin-bottom: 10px;">📈 Data Coverage</h4>
                    <p style="color: #666; font-size: 0.9em;">
                        Analysis based on 15 consecutive seasons (2010-2024) • 
                        2,376+ draft picks • 233 mapped players • 96.3% mapping accuracy
                    </p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Embed all data directly in the HTML
        console.log('Setting up embedded data...');
        
        window.EMBEDDED_DATA = {{
            players: {json.dumps(players_data['players'], separators=(',', ':'))},
            insights: {json.dumps(insights_data, separators=(',', ':'))},
            metadata: {json.dumps(metadata, separators=(',', ':'))},
            playerIndex: {json.dumps(player_index, separators=(',', ':'))}
        }};
        
        console.log('Embedded data set, players:', Object.keys(window.EMBEDDED_DATA.players).length);
        
        // Modified app JavaScript
        {js_content}
    </script>
</body>
</html>'''

        # Write the file
        output_file = 'html_reports/standalone_fixed.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Fixed standalone HTML created: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"Error creating standalone HTML: {e}")
        return False

def main():
    """Main function to fix both issues."""
    
    print("=== FIXING BOTH ISSUES ===\\n")
    
    # Fix 1: Add player names to all draft files
    fixed_years = add_player_names_to_all_drafts()
    
    # Fix 2: Debug and regenerate standalone HTML
    debug_ok = debug_standalone_html()
    standalone_ok = regenerate_standalone_html_fixed()
    
    # Regenerate draft results with all names
    if fixed_years:
        print("\\n=== REGENERATING DRAFT RESULTS PAGE ===")
        try:
            import create_draft_results_page
            create_draft_results_page.create_draft_results_page()
            print("Draft results page regenerated with all player names")
        except Exception as e:
            print(f"Error regenerating draft results: {e}")
    
    print(f"\\n=== SUMMARY ===")
    print(f"Draft names fixed for {len(fixed_years)} years")
    print(f"Debug status: {'OK' if debug_ok else 'Issues found'}")
    print(f"Standalone HTML: {'Fixed' if standalone_ok else 'Failed'}")
    print(f"\\nFiles created:")
    print(f"  - html_reports/standalone_fixed.html (test this one)")
    print(f"  - html_reports/test.html (simple test)")

if __name__ == "__main__":
    main()