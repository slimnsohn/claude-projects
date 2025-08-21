#!/usr/bin/env python3
"""
Create comprehensive owner analysis page with historical standings.
"""

import json
import os
from collections import defaultdict

def create_owner_tracking():
    """Create owner tracking data across all years."""
    
    print("=== CREATING OWNER TRACKING ANALYSIS ===\n")
    
    # Track owners across years
    owner_history = defaultdict(lambda: {
        'years_active': [],
        'team_names': {},
        'standings': {},
        'total_seasons': 0,
        'best_regular_rank': float('inf'),
        'worst_regular_rank': 0,
        'playoff_appearances': 0,
        'total_wins': 0,
        'total_losses': 0,
        'total_ties': 0
    })
    
    # Process all years
    years_processed = []
    
    for year in range(2010, 2025):
        owners_file = f'league_data/{year}/processed_data/owners.json'
        if os.path.exists(owners_file):
            print(f"Processing {year}...")
            
            try:
                with open(owners_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                owners = data.get('owners', {})
                
                for email, owner_data in owners.items():
                    # Skip non-email keys (some years have team keys as email)
                    if '@' not in email and 'l.' in email:
                        continue
                    
                    team_name = owner_data.get('team_name', 'Unknown Team')
                    standings = owner_data.get('standings', {})
                    
                    # Extract standings data
                    regular_rank = int(standings.get('rank', 0))
                    playoff_seed = standings.get('playoff_seed')
                    outcome = standings.get('outcome_totals', {})
                    
                    wins = int(outcome.get('wins', 0))
                    losses = int(outcome.get('losses', 0))
                    ties = int(outcome.get('ties', 0))
                    
                    # Update owner history
                    owner_history[email]['years_active'].append(year)
                    owner_history[email]['team_names'][year] = team_name
                    owner_history[email]['standings'][year] = {
                        'regular_rank': regular_rank,
                        'playoff_seed': playoff_seed,
                        'wins': wins,
                        'losses': losses,
                        'ties': ties,
                        'win_percentage': round(wins / (wins + losses + ties) if (wins + losses + ties) > 0 else 0, 3)
                    }
                    
                    # Update aggregates
                    owner_history[email]['total_seasons'] += 1
                    owner_history[email]['total_wins'] += wins
                    owner_history[email]['total_losses'] += losses
                    owner_history[email]['total_ties'] += ties
                    
                    if regular_rank > 0:
                        owner_history[email]['best_regular_rank'] = min(owner_history[email]['best_regular_rank'], regular_rank)
                        owner_history[email]['worst_regular_rank'] = max(owner_history[email]['worst_regular_rank'], regular_rank)
                    
                    if playoff_seed and int(playoff_seed) > 0:
                        owner_history[email]['playoff_appearances'] += 1
                
                years_processed.append(year)
                
            except Exception as e:
                print(f"  Error processing {year}: {e}")
    
    # Calculate final metrics
    for email, data in owner_history.items():
        if data['total_seasons'] > 0:
            total_games = data['total_wins'] + data['total_losses'] + data['total_ties']
            data['career_win_percentage'] = round(data['total_wins'] / total_games if total_games > 0 else 0, 3)
            data['playoff_percentage'] = round(data['playoff_appearances'] / data['total_seasons'], 3)
            
            # Fix best rank if no valid ranks found
            if data['best_regular_rank'] == float('inf'):
                data['best_regular_rank'] = None
    
    print(f"\nProcessed {len(years_processed)} years: {years_processed}")
    print(f"Found {len(owner_history)} unique owners")
    
    return dict(owner_history), years_processed

def create_owner_analysis_page():
    """Create the owner analysis HTML page."""
    
    print("\n=== CREATING OWNER ANALYSIS PAGE ===\n")
    
    # Get owner data
    owner_data, years_processed = create_owner_tracking()
    
    # Sort owners by total seasons (most active first)
    sorted_owners = sorted(owner_data.items(), key=lambda x: (x[1]['total_seasons'], x[1]['career_win_percentage']), reverse=True)
    
    # Load CSS for styling
    try:
        with open('html_reports/css/style.css', 'r', encoding='utf-8') as f:
            css_content = f.read()
    except:
        css_content = "/* CSS file not found */"
    
    # Create HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Owner Analysis - Fantasy Basketball League</title>
    <style>
{css_content}

/* Additional owner analysis styles */
.owner-card {{
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-left: 5px solid #667eea;
}}

.owner-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-wrap: wrap;
}}

.owner-name {{
    font-size: 1.3em;
    font-weight: bold;
    color: #333;
}}

.owner-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 10px;
    margin-bottom: 20px;
}}

.stat-item {{
    text-align: center;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 5px;
}}

.stat-value {{
    font-size: 1.4em;
    font-weight: bold;
    color: #667eea;
    display: block;
}}

.stat-label {{
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
}}

.year-history {{
    overflow-x: auto;
}}

.history-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
}}

.history-table th,
.history-table td {{
    padding: 8px 12px;
    text-align: center;
    border-bottom: 1px solid #e9ecef;
}}

.history-table th {{
    background: #667eea;
    color: white;
    font-weight: 500;
    position: sticky;
    top: 0;
}}

.rank-1 {{ background-color: #d4edda; font-weight: bold; }}
.rank-2 {{ background-color: #e7f3d3; }}
.rank-3 {{ background-color: #f0f8d8; }}
.playoffs {{ background-color: #cce5ff; }}
.miss-playoffs {{ background-color: #ffe6e6; }}

.summary-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}}

.summary-card {{
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}}

.summary-number {{
    font-size: 2.5em;
    font-weight: bold;
    margin-bottom: 5px;
}}

.summary-label {{
    font-size: 1.1em;
    opacity: 0.9;
}}

@media (max-width: 768px) {{
    .owner-stats {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .history-table {{
        font-size: 0.8em;
    }}
    
    .history-table th,
    .history-table td {{
        padding: 6px 8px;
    }}
}}

    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <!-- Page Header -->
            <div class="page-header">
                <h1>👥 Owner Analysis</h1>
                <p>Historical Performance Tracking ({len(years_processed)} seasons: {min(years_processed)}-{max(years_processed)})</p>
            </div>
            
            <!-- Summary Statistics -->
            <div class="summary-stats">
                <div class="summary-card">
                    <div class="summary-number">{len(sorted_owners)}</div>
                    <div class="summary-label">Total Owners</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{len(years_processed)}</div>
                    <div class="summary-label">Seasons Tracked</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{sum(data['total_seasons'] for _, data in sorted_owners)}</div>
                    <div class="summary-label">Total Team-Seasons</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">{len([o for o, d in sorted_owners if d['total_seasons'] >= 10])}</div>
                    <div class="summary-label">10+ Season Veterans</div>
                </div>
            </div>
            
            <!-- Owner Cards -->
            <div class="owners-grid">
'''
    
    # Add owner cards
    for email, data in sorted_owners:
        # Get most recent team name
        recent_year = max(data['years_active'])
        recent_team_name = data['team_names'][recent_year]
        
        # Calculate additional stats
        avg_rank = round(sum(data['standings'][year]['regular_rank'] for year in data['years_active'] if data['standings'][year]['regular_rank'] > 0) / 
                        len([year for year in data['years_active'] if data['standings'][year]['regular_rank'] > 0]) if data['years_active'] else 0, 1)
        
        html_content += f'''
                <div class="owner-card">
                    <div class="owner-header">
                        <div class="owner-name">{recent_team_name}</div>
                        <div style="color: #666; font-size: 0.9em;">{email}</div>
                    </div>
                    
                    <div class="owner-stats">
                        <div class="stat-item">
                            <span class="stat-value">{data['total_seasons']}</span>
                            <div class="stat-label">Seasons</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['career_win_percentage']}</span>
                            <div class="stat-label">Win %</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['best_regular_rank'] if data['best_regular_rank'] else 'N/A'}</span>
                            <div class="stat-label">Best Rank</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{avg_rank if avg_rank > 0 else 'N/A'}</span>
                            <div class="stat-label">Avg Rank</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['playoff_appearances']}</span>
                            <div class="stat-label">Playoffs</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">{data['playoff_percentage']}</span>
                            <div class="stat-label">Playoff %</div>
                        </div>
                    </div>
                    
                    <div class="year-history">
                        <table class="history-table">
                            <thead>
                                <tr>
                                    <th>Year</th>
                                    <th>Team Name</th>
                                    <th>Regular Rank</th>
                                    <th>Playoff Seed</th>
                                    <th>Record</th>
                                    <th>Win %</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        # Add year-by-year history (most recent first)
        for year in sorted(data['years_active'], reverse=True):
            team_name = data['team_names'][year]
            standings = data['standings'][year]
            
            regular_rank = standings['regular_rank']
            playoff_seed = standings['playoff_seed'] if standings['playoff_seed'] else 'N/A'
            wins = standings['wins']
            losses = standings['losses']
            ties = standings['ties']
            win_pct = standings['win_percentage']
            
            # Determine row class based on performance
            row_class = ''
            if regular_rank == 1:
                row_class = 'rank-1'
            elif regular_rank == 2:
                row_class = 'rank-2'
            elif regular_rank == 3:
                row_class = 'rank-3'
            elif playoff_seed != 'N/A' and int(playoff_seed) > 0:
                row_class = 'playoffs'
            else:
                row_class = 'miss-playoffs'
            
            record = f"{wins}-{losses}"
            if ties > 0:
                record += f"-{ties}"
            
            html_content += f'''
                                <tr class="{row_class}">
                                    <td><strong>{year}</strong></td>
                                    <td>{team_name}</td>
                                    <td>{regular_rank}</td>
                                    <td>{playoff_seed}</td>
                                    <td>{record}</td>
                                    <td>{win_pct}</td>
                                </tr>
            '''
        
        html_content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
        '''
    
    # Close HTML
    html_content += '''
            </div>
            
            <!-- Legend -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px;">
                <h4 style="margin-bottom: 15px;">Legend</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9em;">
                    <div><span style="background: #d4edda; padding: 2px 8px; border-radius: 3px;">1st Place</span></div>
                    <div><span style="background: #e7f3d3; padding: 2px 8px; border-radius: 3px;">2nd Place</span></div>
                    <div><span style="background: #f0f8d8; padding: 2px 8px; border-radius: 3px;">3rd Place</span></div>
                    <div><span style="background: #cce5ff; padding: 2px 8px; border-radius: 3px;">Made Playoffs</span></div>
                    <div><span style="background: #ffe6e6; padding: 2px 8px; border-radius: 3px;">Missed Playoffs</span></div>
                </div>
            </div>
            
            <!-- Data Coverage -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; text-align: center;">
                <h4 style="color: #333; margin-bottom: 10px;">📊 Data Coverage</h4>
                <p style="color: #666; font-size: 0.9em;">
                    Analysis based on {len(years_processed)} consecutive seasons ({min(years_processed)}-{max(years_processed)}) • 
                    {len(sorted_owners)} unique owners • {sum(data['total_seasons'] for _, data in sorted_owners)} total team-seasons
                </p>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Write the file
    output_file = 'html_reports/prod_ready/owner_analysis.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Owner analysis page created: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"Covers {len(sorted_owners)} owners across {len(years_processed)} seasons")
    
    # Also save raw data for further analysis
    analysis_data = {
        'owner_data': owner_data,
        'years_processed': years_processed,
        'summary': {
            'total_owners': len(sorted_owners),
            'total_seasons': len(years_processed),
            'total_team_seasons': sum(data['total_seasons'] for _, data in sorted_owners),
            'veterans_10plus': len([o for o, d in sorted_owners if d['total_seasons'] >= 10])
        }
    }
    
    with open('html_reports/data/owner_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print("Raw analysis data saved to: html_reports/data/owner_analysis.json")
    
    return True

if __name__ == "__main__":
    create_owner_analysis_page()