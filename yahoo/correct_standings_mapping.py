#!/usr/bin/env python3
"""
Correct Standings Data Mapping
Store properly mapped standings data as flat data for validation
"""

import json
import os
import csv
from pathlib import Path

def correct_standings_mapping():
    """Extract and correctly map all standings data."""
    
    print("=== CORRECTING STANDINGS DATA MAPPING ===")
    print("Mapping correction: playoff_seed = regular season standing, rank = playoff results")
    
    all_corrected_data = []
    
    # Get all year directories
    league_data_dir = Path("league_data")
    year_dirs = [d for d in league_data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    year_dirs.sort()
    
    for year_dir in year_dirs:
        year = year_dir.name
        standings_file = f"league_data/{year}/raw_data/standings.json"
        
        if not os.path.exists(standings_file):
            continue
            
        print(f"Processing {year}...")
        
        try:
            with open(standings_file, 'r', encoding='utf-8') as f:
                raw_standings = json.load(f)
            
            for team_data in raw_standings:
                # CORRECTED MAPPING:
                regular_season_standing = int(team_data.get('playoff_seed', 99))  # This is actually reg season
                playoff_result = int(team_data['rank'])  # This is actually playoff result
                
                corrected_record = {
                    'year': int(year),
                    'team_name': team_data['name'],
                    'regular_season_standing': regular_season_standing,  # Final league position
                    'playoff_result': playoff_result,  # Tournament outcome
                    'wins': int(team_data['outcome_totals']['wins']),
                    'losses': int(team_data['outcome_totals']['losses']),
                    'ties': int(team_data['outcome_totals'].get('ties', 0)),
                    'win_percentage': float(team_data['outcome_totals']['percentage']),
                    'games_back': team_data.get('games_back', 'N/A'),
                    'team_key': team_data.get('team_key', '')
                }
                
                all_corrected_data.append(corrected_record)
                
        except Exception as e:
            print(f"Error processing {year}: {e}")
            continue
    
    print(f"Total records processed: {len(all_corrected_data)}")
    return all_corrected_data

def save_corrected_flat_data(corrected_data):
    """Save corrected data as flat files."""
    
    # Save as JSON
    json_output = 'corrected_standings_flat_data.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2)
    print(f"Saved JSON: {json_output}")
    
    # Save as CSV for easy validation
    csv_output = 'corrected_standings_flat_data.csv'
    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        if corrected_data:
            fieldnames = corrected_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(corrected_data)
    print(f"Saved CSV: {csv_output}")

def create_corrected_signoff_html(corrected_data):
    """Create sign-off page with correctly mapped data."""
    
    # Group data by year
    data_by_year = {}
    for record in corrected_data:
        year = record['year']
        if year not in data_by_year:
            data_by_year[year] = []
        data_by_year[year].append(record)
    
    # Sort each year by regular season standing
    for year in data_by_year:
        data_by_year[year].sort(key=lambda x: x['regular_season_standing'])
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORRECTED Owner Standings Validation</title>
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

        .correction-notice {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
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
            font-size: 1.3em;
            font-weight: bold;
        }

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

        /* Regular Season Standing colors */
        .reg-season-1 { background-color: #d4edda !important; border-left: 4px solid #28a745; }
        .reg-season-2 { background-color: #d1ecf1 !important; border-left: 4px solid #17a2b8; }
        .reg-season-3 { background-color: #fff3cd !important; border-left: 4px solid #ffc107; }
        .reg-season-playoffs { background-color: #e2e3e5 !important; }
        .reg-season-bottom { background-color: #f8d7da !important; }

        /* Playoff Results highlighting */
        .playoff-champion { font-weight: bold; color: #28a745; }
        .playoff-runner-up { font-weight: bold; color: #17a2b8; }
        .playoff-semifinal { font-weight: bold; color: #ffc107; }

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
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>CORRECTED Owner Standings Validation</h1>
                <p>Properly mapped team standings: Regular Season & Playoff Results</p>
            </div>

            <div class="correction-notice">
                <h3>Data Mapping Correction Applied</h3>
                <p><strong>Regular Season Standing:</strong> Final league position (1st, 2nd, 3rd, etc.)</p>
                <p><strong>Playoff Result:</strong> Tournament outcome position</p>
                <p>Data has been remapped from the raw Yahoo API response for accuracy</p>
            </div>

            <div class="data-summary">
                <h3>Corrected Data Summary</h3>
                <p><strong>Total Records:</strong> ''' + str(len(corrected_data)) + ''' team seasons</p>
                <p><strong>Years Covered:</strong> ''' + str(len(data_by_year)) + ''' seasons (2010-2024)</p>
                <p><strong>Data Source:</strong> Yahoo Fantasy API standings, correctly mapped</p>
            </div>'''
    
    # Add year-by-year sections
    for year in sorted(data_by_year.keys()):
        year_data = data_by_year[year]
        
        html_content += f'''
            <div class="year-section">
                <div class="year-header">
                    {year} Season - {len(year_data)} Teams
                </div>
                <table class="standings-table">
                    <thead>
                        <tr>
                            <th>Team Name</th>
                            <th>Regular Season Standing</th>
                            <th>Playoff Result</th>
                            <th>Record (W-L-T)</th>
                            <th>Win %</th>
                            <th>Games Back</th>
                        </tr>
                    </thead>
                    <tbody>'''
        
        for team in year_data:
            # Row styling based on regular season standing
            reg_standing = team['regular_season_standing']
            if reg_standing == 1:
                row_class = "reg-season-1"
            elif reg_standing == 2:
                row_class = "reg-season-2"
            elif reg_standing == 3:
                row_class = "reg-season-3"
            elif reg_standing <= 6:  # Playoff teams
                row_class = "reg-season-playoffs"
            elif reg_standing >= len(year_data) - 2:  # Bottom teams
                row_class = "reg-season-bottom"
            else:
                row_class = ""
            
            # Playoff result styling
            playoff_result = team['playoff_result']
            playoff_class = ""
            if playoff_result == 1:
                playoff_class = "playoff-champion"
            elif playoff_result == 2:
                playoff_class = "playoff-runner-up"
            elif playoff_result <= 4:
                playoff_class = "playoff-semifinal"
            
            # Build record string
            record = f"{team['wins']}-{team['losses']}"
            if team['ties'] > 0:
                record += f"-{team['ties']}"
            
            html_content += f'''
                        <tr class="{row_class}">
                            <td><strong>{team['team_name']}</strong></td>
                            <td>#{team['regular_season_standing']}</td>
                            <td class="{playoff_class}">#{team['playoff_result']}</td>
                            <td>{record}</td>
                            <td>{team['win_percentage']:.3f}</td>
                            <td>{team['games_back']}</td>
                        </tr>'''
        
        html_content += '''
                    </tbody>
                </table>
            </div>'''
    
    html_content += '''
            <div class="sign-off-section">
                <h3>CORRECTED Data Validation Sign-Off</h3>
                <p>Please verify the corrected mappings above are accurate:</p>
                <ul style="text-align: left; margin: 15px 0; padding-left: 40px;">
                    <li><strong>Regular Season Standing</strong> = Final league position</li>
                    <li><strong>Playoff Result</strong> = Tournament outcome</li>
                    <li>Team names and records match your records</li>
                </ul>
                <button class="sign-off-button" onclick="signOff()">
                    SIGN OFF ON CORRECTED STANDINGS
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
            button.innerHTML = '✓ CORRECTED DATA SIGNED OFF';
            button.disabled = true;
            
            statusDiv.innerHTML = '✅ Corrected standings data validated and signed off on ' + new Date().toLocaleDateString();
            statusDiv.style.display = 'block';
            
            console.log('Corrected standings data validation signed off at:', new Date());
        }
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main execution."""
    
    # Extract and correct the data mapping
    corrected_data = correct_standings_mapping()
    
    if not corrected_data:
        print("No data found to correct!")
        return
    
    # Save flat data files
    save_corrected_flat_data(corrected_data)
    
    # Create corrected sign-off HTML
    html_content = create_corrected_signoff_html(corrected_data)
    
    # Save corrected HTML file
    output_file = 'sign_off_on_owner_standings.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nCORRECTED validation page created: {output_file}")
    print("Raw flat data files created:")
    print("  - corrected_standings_flat_data.json")
    print("  - corrected_standings_flat_data.csv")

if __name__ == "__main__":
    main()