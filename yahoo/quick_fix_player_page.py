#!/usr/bin/env python3
"""
Quick fix for player_analysis.html - remove age column and add stats popup
"""

import json
import re

def load_player_stats_data():
    """Load player statistics for popup."""
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_player_stats_lookup():
    """Create lookup for 2024 player stats."""
    players_data = load_player_stats_data()
    lookup = {}
    
    for player_id, player_info in players_data['players'].items():
        player_name = player_info['player_name']
        seasons = player_info.get('seasons', {})
        
        # Get 2024 stats
        stats_2024 = seasons.get('2024')
        if stats_2024:
            lookup[player_name] = {
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
    
    return lookup

def fix_player_analysis_html():
    """Fix the existing HTML file."""
    
    # Read current file
    with open('html_reports/prod_ready/player_analysis.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Get player stats lookup
    player_stats_lookup = get_player_stats_lookup()
    
    # Remove age column header
    html_content = html_content.replace('<th>Age</th>', '')
    
    # Remove all age column data (the <td>29</td> entries)
    html_content = re.sub(r'<td>29</td>\s*', '', html_content)
    
    # Make player names clickable with accordion functionality
    html_content = re.sub(
        r'<td class="player-name">([^<]+)</td>',
        r'<td class="player-name" onclick="togglePlayerStats(&quot;\1&quot;, this)" style="cursor: pointer; text-decoration: underline;">\1</td>',
        html_content
    )
    
    # Fix all onclick handlers systematically
    # First, handle any existing showPlayerStats calls
    html_content = re.sub(
        r'onclick="showPlayerStats\(([^)]+)\)"',
        r'onclick="togglePlayerStats(\1, this)"',
        html_content
    )
    
    # Now fix all malformed onclick handlers with a comprehensive approach
    # Find all onclick="togglePlayerStats(...)" and fix them
    def fix_onclick(match):
        full_match = match.group(0)
        # Extract player name from various possible formats
        if '&quot;' in full_match:
            # Already properly formatted
            return full_match
        elif "\\'" in full_match:
            # Has escaped quotes, extract the name
            name_match = re.search(r"togglePlayerStats\(\\'([^']*(?:'[^']*)*)\\'", full_match)
            if name_match:
                player_name = name_match.group(1)
                return f'onclick="togglePlayerStats(&quot;{player_name}&quot;, this)"'
        return full_match
    
    html_content = re.sub(
        r'onclick="togglePlayerStats\([^)]+\)"',
        fix_onclick,
        html_content
    )
    
    # Add note about clicking player names and debug button
    html_content = html_content.replace(
        '<p><strong>Team Context:</strong> Projections assume similar role/usage as 2024</p>',
        '<p><strong>Team Context:</strong> Projections assume similar role/usage as 2024</p>\n                    <p><strong>Interactive:</strong> Click any player name to expand/collapse their 2024 season stats</p>\n                    <button onclick="testFunction()" style="background: red; color: white; padding: 10px; margin: 10px;">Test JavaScript</button>'
    )
    
    # Add accordion styles and JavaScript before closing body tag
    accordion_html = '''
    <style>
        .player-stats-accordion {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            margin: 5px 0;
            padding: 15px;
            animation: slideDown 0.3s ease;
        }
        
        .stats-grid-accordion {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .stat-item-accordion {
            text-align: center;
            padding: 8px;
            background: white;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        }
        
        .stat-value-accordion {
            font-size: 1.1em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label-accordion {
            font-size: 0.75em;
            color: #6c757d;
            margin-top: 3px;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                max-height: 0;
                padding: 0 15px;
            }
            to {
                opacity: 1;
                max-height: 200px;
                padding: 15px;
            }
        }
        
        @keyframes slideUp {
            from {
                opacity: 1;
                max-height: 200px;
                padding: 15px;
            }
            to {
                opacity: 0;
                max-height: 0;
                padding: 0 15px;
            }
        }
        
        .slide-up {
            animation: slideUp 0.3s ease forwards;
        }
    </style>

    <script>
        // Test function to verify JavaScript is working
        function testFunction() {
            alert('JavaScript is working!');
        }
        
        // Player stats data
        const playerStatsData = ''' + json.dumps(player_stats_lookup, indent=8) + ''';

        function togglePlayerStats(playerName, clickedCell) {
            console.log('togglePlayerStats called with player:', playerName);
            console.log('clickedCell:', clickedCell);
            console.log('playerStatsData keys:', Object.keys(playerStatsData).slice(0, 5));
            
            const stats = playerStatsData[playerName];
            console.log('Found stats for', playerName + ':', stats);
            
            if (!stats) {
                console.error('No stats found for player:', playerName);
                alert('No 2024 stats available for ' + playerName);
                return;
            }
            
            // Find the row that contains this cell
            const row = clickedCell.closest('tr');
            const existingAccordion = row.nextElementSibling;
            
            // If accordion exists, remove it
            if (existingAccordion && existingAccordion.classList.contains('accordion-row')) {
                existingAccordion.classList.add('slide-up');
                setTimeout(() => {
                    existingAccordion.remove();
                }, 300);
                return;
            }
            
            // Create new accordion row
            const accordionRow = document.createElement('tr');
            accordionRow.classList.add('accordion-row');
            
            // Count columns in the current row to span across all
            const columnCount = row.children.length;
            
            accordionRow.innerHTML = `
                <td colspan="${columnCount}">
                    <div class="player-stats-accordion">
                        <h4 style="margin-bottom: 10px; color: #495057;">${playerName} - 2024 Season Stats</h4>
                        <div class="stats-grid-accordion">
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.games_played}</div>
                                <div class="stat-label-accordion">Games</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.team}</div>
                                <div class="stat-label-accordion">Team</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.pts_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">PPG</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.reb_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">RPG</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.ast_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">APG</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.stl_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">SPG</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.blk_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">BPG</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.threepm_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">3PM</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${(stats.fg_pct * 100).toFixed(1)}%</div>
                                <div class="stat-label-accordion">FG%</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${(stats.ft_pct * 100).toFixed(1)}%</div>
                                <div class="stat-label-accordion">FT%</div>
                            </div>
                            <div class="stat-item-accordion">
                                <div class="stat-value-accordion">${stats.to_pg.toFixed(1)}</div>
                                <div class="stat-label-accordion">TO</div>
                            </div>
                        </div>
                    </div>
                </td>
            `;
            
            // Insert the accordion row after the current row
            row.parentNode.insertBefore(accordionRow, row.nextSibling);
        }
    </script>
</body>'''
    
    html_content = html_content.replace('</body>', accordion_html)
    
    # Also remove age references from archetype cards
    html_content = re.sub(r'<p><strong>Avg Age:</strong> 29\.0</p>', '', html_content)
    
    # Remove old popup JavaScript functions and elements to avoid conflicts
    html_content = re.sub(r'function showPlayerStats\(playerName\).*?function hidePlayerStats\(\).*?}\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<!-- Stats Popup -->.*?</div>\s*', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div class="stats-popup-overlay".*?</div>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div class="stats-popup".*?</div>', '', html_content, flags=re.DOTALL)
    
    return html_content

def main():
    """Main execution."""
    print("=== QUICK FIXING PLAYER ANALYSIS PAGE ===")
    
    # Fix the HTML
    fixed_html = fix_player_analysis_html()
    
    # Save the fixed file
    with open('html_reports/prod_ready/player_analysis.html', 'w', encoding='utf-8') as f:
        f.write(fixed_html)
    
    print("Player analysis page fixed!")
    print("Changes made:")
    print("- Removed age column header")
    print("- Removed all age data (was showing 29 for everyone)")
    print("- Made player names clickable")
    print("- Added accordion-style dropdown for 2024 stats")
    print("- Added note about interactive functionality")
    print(f"- Loaded 2024 stats for accordion display")

if __name__ == "__main__":
    main()