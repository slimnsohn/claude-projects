#!/usr/bin/env python3
"""
Complete fix for standalone.html without Unicode characters.
"""

import json
import os

def regenerate_standalone_html_fixed():
    """Regenerate standalone HTML with better error handling."""
    
    print("=== REGENERATING STANDALONE HTML ===\n")
    
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

def regenerate_draft_results():
    """Regenerate draft results with all player names."""
    
    print("\n=== REGENERATING DRAFT RESULTS PAGE ===")
    
    try:
        import create_draft_results_page
        create_draft_results_page.create_draft_results_page()
        print("Draft results page regenerated with all player names")
        return True
    except Exception as e:
        print(f"Error regenerating draft results: {e}")
        return False

def main():
    """Main function to complete the fix."""
    
    print("=== COMPLETING THE FIX ===\n")
    
    # Fix standalone HTML
    standalone_ok = regenerate_standalone_html_fixed()
    
    # Regenerate draft results with all names
    draft_ok = regenerate_draft_results()
    
    print(f"\n=== SUMMARY ===")
    print(f"Standalone HTML: {'Fixed' if standalone_ok else 'Failed'}")
    print(f"Draft results: {'Updated' if draft_ok else 'Failed'}")
    print(f"\nFiles to test:")
    print(f"  - html_reports/standalone_fixed.html (should load player data)")
    print(f"  - html_reports/draft_results_standalone.html (should show all years with names)")

if __name__ == "__main__":
    main()