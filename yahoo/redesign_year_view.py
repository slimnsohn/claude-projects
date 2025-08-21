#!/usr/bin/env python3
"""
Redesign year view to be collapsible like owner view.
Years as keys (collapsible panels), owners as values (sortable tables).
"""

import json
import re

def redesign_year_view():
    """Redesign year view with collapsible year panels and sortable columns."""
    
    # Load owner data
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
                'regular_season': int(standings['playoff_seed']) if standings['playoff_seed'] and str(standings['playoff_seed']).isdigit() else 99,
                'playoffs': standings['regular_rank'],
                'wins': standings['wins'],
                'losses': standings['losses'],
                'ties': standings['ties'],
                'win_pct': round(standings['wins'] / (standings['wins'] + standings['losses'] + standings['ties']), 3) if (standings['wins'] + standings['losses'] + standings['ties']) > 0 else 0
            })
    
    # Sort data within each year by playoff rank
    for year in years_data:
        years_data[year].sort(key=lambda x: x['playoffs'])
    
    # Create new year view HTML with collapsible structure
    sorted_years = sorted(years_data.keys(), reverse=True)
    
    year_view_html = '''
            </div> <!-- End Owners View -->
            
            <!-- Year View Tab Content -->
            <div id="years-tab" class="tab-content">
                
                <!-- Year Summary Stats -->
                <div class="summary-stats">
                    <div class="summary-card">
                        <div class="summary-number">15</div>
                        <div class="summary-label">Seasons Analyzed</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-number">2010-2024</div>
                        <div class="summary-label">Year Range</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-number">''' + str(len([team for teams in years_data.values() for team in teams])) + '''</div>
                        <div class="summary-label">Total Team Seasons</div>
                    </div>
                </div>
                
                <div class="years-controls">
                    <button class="collapse-all-years-btn" onclick="toggleAllYears()">📁 Collapse All Years</button>
                </div>
                
                <!-- Year Cards -->
                <div class="years-grid">'''
    
    # Add year cards
    for year in sorted_years:
        teams = years_data[year]
        num_teams = len(teams)
        champion = teams[0] if teams else {'owner': 'Unknown', 'team_name': 'Unknown'}
        
        year_view_html += f'''
                    <div class="year-card">
                        <div class="year-header" onclick="toggleYear(this)">
                            <div>
                                <div class="year-name">{year} Season</div>
                                <div style="color: #666; font-size: 0.9em;">{num_teams} teams • Champion: {champion['owner']} ({champion['team_name']})</div>
                            </div>
                            <span class="collapse-icon">🔽</span>
                        </div>
                        <div class="year-content">
                        
                            <div class="year-stats">
                                <div class="stat-item">
                                    <span class="stat-value">{num_teams}</span>
                                    <span class="stat-label">Teams</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-value">{champion['owner']}</span>
                                    <span class="stat-label">Champion</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-value">{champion['team_name']}</span>
                                    <span class="stat-label">Winning Team</span>
                                </div>
                            </div>
                            
                            <div class="year-rankings">
                                <div class="table-controls">
                                    <h4>Season Rankings</h4>
                                    <div class="sort-info">Click column headers to sort</div>
                                </div>
                                <table class="sortable-table" id="table-{year}">
                                    <thead>
                                        <tr>
                                            <th class="sortable" onclick="sortTable('{year}', 0, 'number')">Playoffs <span class="sort-arrow">⬍</span></th>
                                            <th class="sortable" onclick="sortTable('{year}', 1, 'text')">Owner <span class="sort-arrow">⬍</span></th>
                                            <th class="sortable" onclick="sortTable('{year}', 2, 'text')">Team Name <span class="sort-arrow">⬍</span></th>
                                            <th class="sortable" onclick="sortTable('{year}', 3, 'number')">Regular Season <span class="sort-arrow">⬍</span></th>
                                            <th class="sortable" onclick="sortTable('{year}', 4, 'text')">Record <span class="sort-arrow">⬍</span></th>
                                            <th class="sortable" onclick="sortTable('{year}', 5, 'number')">Win % <span class="sort-arrow">⬍</span></th>
                                        </tr>
                                    </thead>
                                    <tbody>'''
        
        # Add team rows
        for team in teams:
            # Determine row class
            rank = team['playoffs']
            if rank == 1:
                row_class = 'rank-1'
            elif rank == 2:
                row_class = 'rank-2'
            elif rank == 3:
                row_class = 'rank-3'
            elif team['regular_season'] <= 8:
                row_class = 'playoffs'
            else:
                row_class = 'miss-playoffs'
            
            record = f"{team['wins']}-{team['losses']}-{team['ties']}"
            regular_display = team['regular_season'] if team['regular_season'] < 99 else 'N/A'
            
            year_view_html += f'''
                                        <tr class="{row_class}">
                                            <td><strong>{rank}</strong></td>
                                            <td>{team['owner']}</td>
                                            <td>{team['team_name']}</td>
                                            <td>{regular_display}</td>
                                            <td>{record}</td>
                                            <td>{team['win_pct']}</td>
                                        </tr>'''
        
        year_view_html += '''
                                    </tbody>
                                </table>
                            </div>
                            
                        </div>
                    </div>'''
    
    year_view_html += '''
                </div>
            </div> <!-- End Year View -->'''
    
    # Read current HTML and replace the year view section
    file_path = 'html_reports/prod_ready/owner_analysis.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the existing year view
    start_marker = '            </div> <!-- End Owners View -->'
    end_marker = '            </div> <!-- End Year View -->'
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print("Could not find year view markers")
        return
    
    # Replace the year view section
    new_content = content[:start_pos] + year_view_html + content[end_pos + len(end_marker):]
    
    # Add CSS for new year view structure
    css_addition = '''
/* Year View Styles - Collapsible Structure */
.years-controls {
    text-align: center;
    margin-bottom: 30px;
}

.collapse-all-years-btn {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 25px;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.3s ease;
}

.collapse-all-years-btn:hover {
    background: linear-gradient(135deg, #5a6fd8, #6a42a0);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.years-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

.year-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border: 1px solid #e9ecef;
}

.year-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    user-select: none;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

.year-header:hover {
    background-color: #f8f9fa;
    border-radius: 5px;
    padding: 5px 10px;
}

.year-name {
    font-size: 1.3em;
    font-weight: bold;
    color: #333;
}

.year-content {
    transition: all 0.3s ease;
    overflow: hidden;
    margin-top: 20px;
}

.year-content.collapsed {
    max-height: 0;
    opacity: 0;
    margin: 0;
    padding: 0;
}

.year-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
    padding: 20px;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border-radius: 8px;
}

.year-rankings {
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

.table-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: #667eea;
    color: white;
}

.table-controls h4 {
    margin: 0;
    font-size: 1.1em;
}

.sort-info {
    font-size: 0.9em;
    opacity: 0.9;
}

.sortable-table {
    width: 100%;
    border-collapse: collapse;
}

.sortable-table th {
    background: #f8f9fa;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    border-bottom: 2px solid #dee2e6;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.3s ease;
}

.sortable-table th:hover {
    background: #e9ecef;
}

.sortable-table th.sortable {
    position: relative;
}

.sort-arrow {
    margin-left: 8px;
    opacity: 0.5;
    font-size: 0.8em;
}

.sortable-table th.sort-asc .sort-arrow {
    opacity: 1;
    color: #667eea;
}

.sortable-table th.sort-desc .sort-arrow {
    opacity: 1;
    color: #667eea;
    transform: rotate(180deg);
    display: inline-block;
}

.sortable-table td {
    padding: 10px 15px;
    border-bottom: 1px solid #f1f3f4;
}

.sortable-table tbody tr:hover {
    background-color: #f8f9fa;
}

@media (max-width: 768px) {
    .year-stats {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    
    .table-controls {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
    
    .sortable-table {
        font-size: 0.9em;
    }
    
    .sortable-table th,
    .sortable-table td {
        padding: 8px 10px;
    }
}

'''
    
    # Insert CSS before closing style tag
    style_end = new_content.find('</style>')
    if style_end != -1:
        new_content = new_content[:style_end] + css_addition + new_content[style_end:]
    
    # Add JavaScript functions for year view
    js_addition = '''
        
        let allYearsCollapsed = false;
        let tableSortStates = {};
        
        function toggleYear(header) {
            const content = header.nextElementSibling;
            const icon = header.querySelector('.collapse-icon');
            
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                icon.classList.remove('collapsed');
                icon.textContent = '🔽';
            } else {
                content.classList.add('collapsed');
                icon.classList.add('collapsed');
                icon.textContent = '▶️';
            }
        }
        
        function toggleAllYears() {
            const button = document.querySelector('.collapse-all-years-btn');
            const headers = document.querySelectorAll('.year-header');
            const contents = document.querySelectorAll('.year-content');
            const icons = document.querySelectorAll('.year-card .collapse-icon');
            
            if (allYearsCollapsed) {
                // Expand all
                contents.forEach(content => content.classList.remove('collapsed'));
                icons.forEach(icon => {
                    icon.classList.remove('collapsed');
                    icon.textContent = '🔽';
                });
                button.textContent = '📁 Collapse All Years';
                allYearsCollapsed = false;
            } else {
                // Collapse all
                contents.forEach(content => content.classList.add('collapsed'));
                icons.forEach(icon => {
                    icon.classList.add('collapsed');
                    icon.textContent = '▶️';
                });
                button.textContent = '📂 Expand All Years';
                allYearsCollapsed = true;
            }
        }
        
        function sortTable(year, columnIndex, dataType) {
            const table = document.getElementById('table-' + year);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const header = table.querySelectorAll('th')[columnIndex];
            
            // Initialize sort state for this table if needed
            if (!tableSortStates[year]) {
                tableSortStates[year] = {};
            }
            
            // Determine sort direction
            let ascending = true;
            if (tableSortStates[year][columnIndex] === 'asc') {
                ascending = false;
                tableSortStates[year][columnIndex] = 'desc';
            } else {
                tableSortStates[year][columnIndex] = 'asc';
            }
            
            // Clear all sort indicators for this table
            table.querySelectorAll('th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Set sort indicator for current column
            header.classList.add(ascending ? 'sort-asc' : 'sort-desc');
            
            // Sort rows
            rows.sort((a, b) => {
                let aVal = a.cells[columnIndex].textContent.trim();
                let bVal = b.cells[columnIndex].textContent.trim();
                
                if (dataType === 'number') {
                    // Handle numeric sorting
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                    return ascending ? aVal - bVal : bVal - aVal;
                } else {
                    // Handle text sorting
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                    if (ascending) {
                        return aVal.localeCompare(bVal);
                    } else {
                        return bVal.localeCompare(aVal);
                    }
                }
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }
'''
    
    # Update showTab function to handle year view controls
    show_tab_update = '''
            // Show/hide collapse button based on tab
            const collapseBtn = document.querySelector('.collapse-all-btn');
            const collapseYearsBtn = document.querySelector('.collapse-all-years-btn');
            if (tabName === 'owners') {
                if (collapseBtn) collapseBtn.style.display = 'inline-block';
                if (collapseYearsBtn) collapseYearsBtn.style.display = 'none';
            } else {
                if (collapseBtn) collapseBtn.style.display = 'none';
                if (collapseYearsBtn) collapseYearsBtn.style.display = 'inline-block';
            }'''
    
    # Replace the collapse button logic in showTab function
    old_collapse_logic = '''            // Show/hide collapse button based on tab
            const collapseBtn = document.querySelector('.collapse-all-btn');
            if (tabName === 'owners') {
                collapseBtn.style.display = 'inline-block';
            } else {
                collapseBtn.style.display = 'none';
            }'''
    
    new_content = new_content.replace(old_collapse_logic, show_tab_update)
    
    # Insert new JavaScript before the closing script tag
    script_end = new_content.find('    </script>')
    if script_end != -1:
        new_content = new_content[:script_end] + js_addition + new_content[script_end:]
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Redesigned year view with collapsible structure")
    print(f"Created {len(sorted_years)} collapsible year panels with sortable tables")
    print("Features:")
    print("- Collapsible year panels (like owner view)")
    print("- Sortable columns in each year table") 
    print("- Year summary statistics")
    print("- Champion information for each year")

if __name__ == "__main__":
    redesign_year_view()