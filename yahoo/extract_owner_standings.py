#!/usr/bin/env python3
"""
Extract Owner Standings Data
Create comprehensive standings validation page showing regular season and playoff results
"""

import json
import os
from pathlib import Path

def load_standings_for_year(year):
    """Load standings data for a specific year."""
    standings_file = f"league_data/{year}/raw_data/standings.json"
    
    if not os.path.exists(standings_file):
        return None
    
    try:
        with open(standings_file, 'r', encoding='utf-8') as f:
            standings_data = json.load(f)
        
        # Process standings data
        processed_standings = []
        for team in standings_data:
            processed_standings.append({
                'team_name': team['name'],
                'regular_season_rank': int(team['rank']),
                'playoff_seed': int(team.get('playoff_seed', team['rank'])),
                'wins': int(team['outcome_totals']['wins']),
                'losses': int(team['outcome_totals']['losses']),
                'ties': int(team['outcome_totals'].get('ties', 0)),
                'win_percentage': float(team['outcome_totals']['percentage']),
                'games_back': team.get('games_back', 'N/A')
            })
        
        return processed_standings
        
    except Exception as e:
        print(f"Error loading standings for {year}: {e}")
        return None

def load_player_rankings_for_year(year):
    """Load player rankings data for a specific year."""
    rankings_file = f"league_data/{year}/raw_data/player_rankings.json"
    
    if not os.path.exists(rankings_file):
        return {"preseason": [], "postseason": [], "status": "missing"}
    
    try:
        with open(rankings_file, 'r', encoding='utf-8') as f:
            rankings_data = json.load(f)
        
        return {
            "preseason": rankings_data.get('player_rankings', []),
            "postseason": rankings_data.get('free_agent_popularity', []),
            "status": rankings_data.get('season_status', 'unknown'),
            "extraction_notes": rankings_data.get('extraction_notes', [])
        }
        
    except Exception as e:
        print(f"Error loading player rankings for {year}: {e}")
        return {"preseason": [], "postseason": [], "status": "error"}

def extract_all_standings():
    """Extract standings for all available years."""
    all_standings = {}
    
    # Check what years we have data for
    league_data_dir = Path("league_data")
    
    if not league_data_dir.exists():
        print("No league_data directory found")
        return all_standings
    
    # Get all year directories
    year_dirs = [d for d in league_data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    year_dirs.sort()
    
    for year_dir in year_dirs:
        year = year_dir.name
        print(f"Processing {year}...")
        
        # Load standings
        standings = load_standings_for_year(year)
        
        # Load player rankings
        player_rankings = load_player_rankings_for_year(year)
        
        all_standings[year] = {
            'team_standings': standings,
            'player_rankings': player_rankings,
            'data_quality': {
                'has_standings': standings is not None,
                'has_player_rankings': len(player_rankings['preseason']) > 0,
                'season_status': player_rankings.get('status', 'unknown')
            }
        }
    
    return all_standings

def create_validation_html(all_standings):
    """Create the HTML validation page."""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Owner Standings Validation</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .page-header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }

        .page-header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .data-summary {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #28a745;
        }

        .year-section {
            margin-bottom: 40px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            overflow: hidden;
        }

        .year-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .year-title {
            font-size: 1.3em;
            font-weight: bold;
        }

        .data-status {
            display: flex;
            gap: 15px;
        }

        .status-badge {
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }

        .status-good { background: #28a745; color: white; }
        .status-missing { background: #dc3545; color: white; }
        .status-partial { background: #ffc107; color: black; }

        .standings-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        .standings-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }

        .standings-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #f1f3f4;
        }

        .standings-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        .standings-table tbody tr:hover {
            background-color: #e3f2fd;
        }

        .rank-1 { background-color: #d4edda !important; border-left: 4px solid #28a745; }
        .rank-2 { background-color: #d1ecf1 !important; border-left: 4px solid #17a2b8; }
        .rank-3 { background-color: #fff3cd !important; border-left: 4px solid #ffc107; }
        .rank-playoffs { background-color: #e2e3e5 !important; }
        .rank-bottom { background-color: #f8d7da !important; }

        .validation-notes {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }

        .sign-off-section {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-top: 30px;
            text-align: center;
        }

        .sign-off-button {
            background: white;
            color: #28a745;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 15px;
            transition: all 0.3s ease;
        }

        .sign-off-button:hover {
            background: #f8f9fa;
            transform: translateY(-2px);
        }

        @media (max-width: 768px) {
            .standings-table {
                font-size: 0.9em;
            }
            
            .data-status {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>Owner Standings Validation</h1>
                <p>Complete data validation for team standings and player rankings across all years</p>
            </div>

            <div class="data-summary">
                <h3>Data Summary</h3>
                <p><strong>Purpose:</strong> Validate team regular season standings, playoff seeding, and player ranking data for historical analysis accuracy.</p>
                <p><strong>Coverage:</strong> ''' + f"{len(all_standings)} years" + ''' of league data (2010-2024)</p>
                <p><strong>Status:</strong> Ready for validation and sign-off</p>
            </div>'''
    
    # Add year-by-year sections
    for year in sorted(all_standings.keys()):
        year_data = all_standings[year]
        standings = year_data.get('team_standings', [])
        data_quality = year_data.get('data_quality', {})
        
        # Status badges
        standings_status = "status-good" if data_quality.get('has_standings') else "status-missing"
        rankings_status = "status-good" if data_quality.get('has_player_rankings') else "status-missing"
        
        standings_text = "Standings ✓" if data_quality.get('has_standings') else "Standings ✗"
        rankings_text = "Rankings ✓" if data_quality.get('has_player_rankings') else "Rankings ✗"
        
        html_content += f'''
            <div class="year-section">
                <div class="year-header">
                    <div class="year-title">{year} Season</div>
                    <div class="data-status">
                        <span class="status-badge {standings_status}">{standings_text}</span>
                        <span class="status-badge {rankings_status}">{rankings_text}</span>
                    </div>
                </div>'''
        
        if standings:
            html_content += '''
                <table class="standings-table">
                    <thead>
                        <tr>
                            <th>Team Name</th>
                            <th>Regular Season Rank</th>
                            <th>Playoff Seed</th>
                            <th>Record (W-L-T)</th>
                            <th>Win %</th>
                            <th>Games Back</th>
                        </tr>
                    </thead>
                    <tbody>'''
            
            for team in standings:
                # Determine row class based on performance
                rank = team['regular_season_rank']
                if rank == 1:
                    row_class = "rank-1"
                elif rank == 2:
                    row_class = "rank-2"
                elif rank == 3:
                    row_class = "rank-3"
                elif rank <= 6:  # Assuming 6-team playoffs
                    row_class = "rank-playoffs"
                elif rank >= len(standings) - 2:  # Bottom 3
                    row_class = "rank-bottom"
                else:
                    row_class = ""
                
                record = f"{team['wins']}-{team['losses']}"
                if team['ties'] > 0:
                    record += f"-{team['ties']}"
                
                html_content += f'''
                        <tr class="{row_class}">
                            <td><strong>{team['team_name']}</strong></td>
                            <td>#{team['regular_season_rank']}</td>
                            <td>#{team['playoff_seed']}</td>
                            <td>{record}</td>
                            <td>{team['win_percentage']:.3f}</td>
                            <td>{team['games_back']}</td>
                        </tr>'''
            
            html_content += '''
                    </tbody>
                </table>'''
        else:
            html_content += '''
                <div style="padding: 20px; text-align: center; color: #dc3545;">
                    <p>No standings data available for this year</p>
                </div>'''
        
        html_content += '</div>'
    
    # Add validation notes and sign-off section
    html_content += '''
            <div class="validation-notes">
                <h3>Validation Checklist</h3>
                <p><strong>Please verify the following for each year:</strong></p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>Team names are correct and consistent</li>
                    <li>Regular season rankings reflect actual final standings</li>
                    <li>Playoff seeding aligns with regular season performance</li>
                    <li>Win-loss records and percentages appear accurate</li>
                    <li>Missing data years are noted for future collection</li>
                </ul>
            </div>

            <div class="sign-off-section">
                <h3>Data Validation Sign-Off</h3>
                <p>Once you've reviewed the standings data above and confirmed accuracy, please sign off to proceed with historical analysis.</p>
                <button class="sign-off-button" onclick="signOff()">
                    SIGN OFF ON STANDINGS DATA
                </button>
                <div id="sign-off-status" style="margin-top: 15px; font-weight: bold; display: none;"></div>
            </div>

        </div>
    </div>

    <script>
        function signOff() {
            const statusDiv = document.getElementById('sign-off-status');
            const button = document.querySelector('.sign-off-button');
            
            button.style.background = '#28a745';
            button.style.color = 'white';
            button.innerHTML = '✓ SIGNED OFF';
            button.disabled = true;
            
            statusDiv.innerHTML = '✅ Data validation completed and signed off on ' + new Date().toLocaleDateString();
            statusDiv.style.display = 'block';
            
            // You could add actual API call here to record sign-off
            console.log('Standings data validation signed off at:', new Date());
        }
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main execution function."""
    print("=== EXTRACTING OWNER STANDINGS DATA ===")
    
    # Extract all standings data
    all_standings = extract_all_standings()
    
    if not all_standings:
        print("No standings data found!")
        return
    
    # Create validation HTML page
    html_content = create_validation_html(all_standings)
    
    # Save to file
    output_file = 'sign_off_on_owner_standings.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Validation page created: {output_file}")
    
    # Print summary
    print(f"\nData Summary:")
    print(f"Years processed: {len(all_standings)}")
    
    for year, data in all_standings.items():
        quality = data['data_quality']
        standings_status = "YES" if quality['has_standings'] else "NO"
        rankings_status = "YES" if quality['has_player_rankings'] else "NO"
        print(f"  {year}: Standings {standings_status} | Rankings {rankings_status}")

if __name__ == "__main__":
    main()