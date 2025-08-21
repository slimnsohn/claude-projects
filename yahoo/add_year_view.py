#!/usr/bin/env python3
"""
Add year view tab to owner analysis HTML.
"""

import json
import re

def add_year_view():
    """Add year view tab with data organized by year."""
    
    # Load owner data to extract year information
    with open('html_reports/data/owner_analysis.json', 'r', encoding='utf-8') as f:
        owner_data = json.load(f)
    
    # Organize data by year
    years_data = {}
    for email, data in owner_data['owner_data'].items():
        for year, standings in data['standings'].items():
            if year not in years_data:
                years_data[year] = []
            
            team_name = data['team_names'].get(year, 'Unknown Team')
            owner_name = data.get('display_name', email.split('@')[0])
            
            years_data[year].append({
                'owner': owner_name,
                'email': email,
                'team_name': team_name,
                'regular_season': standings['playoff_seed'] if standings['playoff_seed'] else 'N/A',
                'playoffs': standings['regular_rank'],
                'wins': standings['wins'],
                'losses': standings['losses'],
                'ties': standings['ties'],
                'win_pct': round(standings['wins'] / (standings['wins'] + standings['losses'] + standings['ties']), 3) if (standings['wins'] + standings['losses'] + standings['ties']) > 0 else 0
            })
    
    # Sort years data
    for year in years_data:
        years_data[year].sort(key=lambda x: x['playoffs'])  # Sort by final playoff ranking
    
    # Create year view HTML
    year_view_html = '''
            </div> <!-- End Owners View -->
            
            <!-- Year View Tab Content -->
            <div id="years-tab" class="tab-content">
                <div class="year-selector">
                    <h3>Select Year</h3>
                    <div class="year-buttons">'''
    
    # Add year buttons
    sorted_years = sorted(years_data.keys(), reverse=True)
    for i, year in enumerate(sorted_years):
        active_class = ' active' if i == 0 else ''
        year_view_html += f'''
                        <button class="year-btn{active_class}" onclick="showYear('{year}')">{year}</button>'''
    
    year_view_html += '''
                    </div>
                </div>
                
                <div class="year-content">'''
    
    # Add year tables
    for i, year in enumerate(sorted_years):
        active_class = ' active' if i == 0 else ''
        teams = years_data[year]
        
        year_view_html += f'''
                    <div id="year-{year}" class="year-table{active_class}">
                        <h3>{year} Season Results</h3>
                        <table class="history-table">
                            <thead>
                                <tr>
                                    <th>Final Rank</th>
                                    <th>Owner</th>
                                    <th>Team Name</th>
                                    <th>Regular Season</th>
                                    <th>Record</th>
                                    <th>Win %</th>
                                </tr>
                            </thead>
                            <tbody>'''
        
        for team in teams:
            # Determine row class based on final ranking
            rank = team['playoffs']
            if rank == 1:
                row_class = 'rank-1'
            elif rank == 2:
                row_class = 'rank-2'
            elif rank == 3:
                row_class = 'rank-3'
            elif team['regular_season'] != 'N/A' and str(team['regular_season']).isdigit() and int(team['regular_season']) <= 8:
                row_class = 'playoffs'
            else:
                row_class = 'miss-playoffs'
            
            record = f"{team['wins']}-{team['losses']}-{team['ties']}"
            
            year_view_html += f'''
                                <tr class="{row_class}">
                                    <td><strong>{rank}</strong></td>
                                    <td>{team['owner']}</td>
                                    <td>{team['team_name']}</td>
                                    <td>{team['regular_season']}</td>
                                    <td>{record}</td>
                                    <td>{team['win_pct']}</td>
                                </tr>'''
        
        year_view_html += '''
                            </tbody>
                        </table>
                    </div>'''
    
    year_view_html += '''
                </div>
            </div> <!-- End Year View -->'''
    
    # Read current HTML
    file_path = 'html_reports/prod_ready/owner_analysis.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert year view before the script section
    script_pos = content.find('    <script>')
    if script_pos == -1:
        print("Could not find script section")
        return
    
    # Insert year view
    new_content = content[:script_pos] + year_view_html + '\n\n' + content[script_pos:]
    
    # Add CSS for year view
    css_addition = '''
/* Year View Styles */
.year-selector {
    margin-bottom: 30px;
    text-align: center;
}

.year-selector h3 {
    margin-bottom: 20px;
    color: #333;
}

.year-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
}

.year-btn {
    padding: 8px 16px;
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.3s ease;
}

.year-btn:hover {
    background: #e9ecef;
    border-color: #667eea;
}

.year-btn.active {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-color: #667eea;
}

.year-content {
    position: relative;
}

.year-table {
    display: none;
}

.year-table.active {
    display: block;
}

.year-table h3 {
    margin-bottom: 20px;
    text-align: center;
    color: #333;
    font-size: 1.5em;
}

@media (max-width: 768px) {
    .year-buttons {
        gap: 5px;
    }
    
    .year-btn {
        padding: 6px 12px;
        font-size: 0.9em;
    }
}

'''
    
    # Insert CSS before closing style tag
    style_end = new_content.find('</style>')
    if style_end != -1:
        new_content = new_content[:style_end] + css_addition + new_content[style_end:]
    
    # Add JavaScript functions
    js_addition = '''
        
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
            
            // Show/hide collapse button based on tab
            const collapseBtn = document.querySelector('.collapse-all-btn');
            if (tabName === 'owners') {
                collapseBtn.style.display = 'inline-block';
            } else {
                collapseBtn.style.display = 'none';
            }
        }
        
        function showYear(year) {
            // Hide all year tables
            document.querySelectorAll('.year-table').forEach(table => {
                table.classList.remove('active');
            });
            
            // Remove active class from all year buttons
            document.querySelectorAll('.year-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected year
            document.getElementById('year-' + year).classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }
'''
    
    # Insert JavaScript before the closing script tag
    script_end = new_content.find('    </script>')
    if script_end != -1:
        new_content = new_content[:script_end] + js_addition + new_content[script_end:]
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Added year view tab to owner analysis")
    print(f"Created year tables for {len(sorted_years)} years: {', '.join(sorted_years)}")

if __name__ == "__main__":
    add_year_view()