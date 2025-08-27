#!/usr/bin/env python3
"""
Update the archetype/positions section to separate into single stock and index groups
"""
import re
import json

def load_player_stats_data():
    """Load player statistics."""
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_positions_section():
    # Read current file
    with open('html_reports/prod_ready/player_analysis.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Define the new positions structure
    single_stock_positions = [
        "Point Guard",
        "Shooting Guard", 
        "Small Forward",
        "Power Forward",
        "Center"
    ]
    
    index_positions = [
        "Guard (PG/SG)",
        "Forward (SF/PF)", 
        "Big Man (PF/C)",
        "Utility (Multi-position)"
    ]
    
    # Create new archetype section HTML
    new_archetype_section = '''
            <div class="projection-section">
                <div class="section-title">🏀 Single Stock Positions</div>
                <div class="archetype-grid">
                    <div class="archetype-card">
                        <h4>Point Guard</h4>
                        <p><strong>Elite playmakers and court generals</strong></p>
                        <p>High assists, steals, and court vision</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Shooting Guard</h4>
                        <p><strong>Scoring specialists and shooters</strong></p>
                        <p>High points, 3PM, and shooting efficiency</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Small Forward</h4>
                        <p><strong>Versatile wing players</strong></p>
                        <p>Balanced stats across categories</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Power Forward</h4>
                        <p><strong>Strong interior presence</strong></p>
                        <p>High rebounds, blocks, and interior scoring</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Center</h4>
                        <p><strong>Dominant big men</strong></p>
                        <p>Elite rebounds, blocks, FG%, interior scoring</p>
                    </div>
                </div>
            </div>

            <div class="projection-section">
                <div class="section-title">📈 Index Groupings</div>
                <div class="archetype-grid">
                    <div class="archetype-card">
                        <h4>Guard Index</h4>
                        <p><strong>PG/SG combined value</strong></p>
                        <p>Assists, steals, 3PM, points emphasis</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Forward Index</h4>
                        <p><strong>SF/PF hybrid value</strong></p>
                        <p>Balanced across all categories</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Big Man Index</h4>
                        <p><strong>PF/C interior dominance</strong></p>
                        <p>Rebounds, blocks, FG% premium</p>
                    </div>
                    <div class="archetype-card">
                        <h4>Utility Index</h4>
                        <p><strong>Multi-position flexibility</strong></p>
                        <p>Positional eligibility value added</p>
                    </div>
                </div>
            </div>'''
    
    # Find and replace the current archetype analysis section
    archetype_pattern = r'<div class="projection-section">\s*<div class="section-title">🎯 Player Archetype Analysis</div>.*?</div>\s*</div>'
    
    html_content = re.sub(
        archetype_pattern,
        new_archetype_section.strip(),
        html_content,
        flags=re.DOTALL
    )
    
    # Save the updated file
    with open('html_reports/prod_ready/player_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Updated positions section!")
    print("Changes made:")
    print("- Split into Single Stock Positions (PG, SG, SF, PF, C)")
    print("- Added Index Groupings (Guard, Forward, Big Man, Utility)")
    print("- Updated descriptions for each position category")

if __name__ == "__main__":
    update_positions_section()