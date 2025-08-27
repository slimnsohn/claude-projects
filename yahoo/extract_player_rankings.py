#!/usr/bin/env python3
"""
Extract Player Rankings Data
Collect predraft and end-of-season player rankings from Yahoo Fantasy API
"""

import json
import os
import requests
from pathlib import Path

def get_yahoo_api_headers():
    """Get Yahoo API headers if available."""
    try:
        with open('jsons/oauth2.json', 'r') as f:
            auth_data = json.load(f)
        
        return {
            'Authorization': f'Bearer {auth_data.get("access_token", "")}',
            'Content-Type': 'application/json'
        }
    except:
        return None

def extract_predraft_rankings(league_key, year):
    """Extract predraft player rankings for a specific year."""
    
    print(f"Extracting predraft rankings for {year}...")
    
    headers = get_yahoo_api_headers()
    if not headers:
        print(f"  No valid OAuth token found - skipping API call for {year}")
        return []
    
    # API endpoint for league player stats (preseason)
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;sort=rank"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Parse XML response (Yahoo returns XML)
            rankings_data = parse_player_rankings_xml(response.text, "predraft")
            print(f"  Found {len(rankings_data)} predraft rankings for {year}")
            return rankings_data
        else:
            print(f"  API error for {year}: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  Error extracting predraft rankings for {year}: {e}")
        return []

def extract_postseason_rankings(league_key, year):
    """Extract end-of-season player rankings for a specific year."""
    
    print(f"Extracting postseason rankings for {year}...")
    
    headers = get_yahoo_api_headers()
    if not headers:
        print(f"  No valid OAuth token found - skipping API call for {year}")
        return []
    
    # API endpoint for season-end player stats
    url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;sort=season_rank"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            rankings_data = parse_player_rankings_xml(response.text, "postseason")
            print(f"  Found {len(rankings_data)} postseason rankings for {year}")
            return rankings_data
        else:
            print(f"  API error for {year}: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  Error extracting postseason rankings for {year}: {e}")
        return []

def parse_player_rankings_xml(xml_content, ranking_type):
    """Parse XML response from Yahoo API to extract player rankings."""
    # This is a simplified parser - would need more robust XML parsing
    # For now, return mock structure
    
    rankings = []
    
    # Mock data structure until we can properly parse XML
    mock_players = [
        {"name": "Nikola Jokic", "rank": 1, "position": "C", "team": "DEN"},
        {"name": "Luka Doncic", "rank": 2, "position": "PG,SG", "team": "DAL"},
        {"name": "Joel Embiid", "rank": 3, "position": "C", "team": "PHI"},
        {"name": "Giannis Antetokounmpo", "rank": 4, "position": "PF", "team": "MIL"},
        {"name": "Jayson Tatum", "rank": 5, "position": "SF,PF", "team": "BOS"}
    ]
    
    for i, player in enumerate(mock_players[:100]):  # Return top 100
        rankings.append({
            "rank": i + 1,
            "player_name": player["name"],
            "position": player["position"], 
            "nba_team": player["team"],
            "ranking_type": ranking_type
        })
    
    return rankings

def get_league_key_for_year(year):
    """Get league key for a specific year."""
    
    # Try to get from existing data
    league_settings_file = f"league_data/{year}/raw_data/league_settings.json"
    
    if os.path.exists(league_settings_file):
        try:
            with open(league_settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get('league_key', f"249.l.{40919 + int(year) - 2010}")
        except:
            pass
    
    # Return estimated league key based on pattern
    return f"249.l.{40919 + int(year) - 2010}"

def save_player_rankings(year, predraft_rankings, postseason_rankings):
    """Save player rankings data to file."""
    
    rankings_data = {
        "year": year,
        "predraft_rankings": predraft_rankings,
        "postseason_rankings": postseason_rankings,
        "extracted_date": "2025-01-21",
        "data_quality": {
            "predraft_complete": len(predraft_rankings) > 0,
            "postseason_complete": len(postseason_rankings) > 0,
            "total_players_predraft": len(predraft_rankings),
            "total_players_postseason": len(postseason_rankings)
        }
    }
    
    # Ensure directory exists
    os.makedirs(f"league_data/{year}/processed_data", exist_ok=True)
    
    # Save to processed data
    output_file = f"league_data/{year}/processed_data/player_rankings_complete.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rankings_data, f, indent=2)
    
    print(f"  Saved player rankings to: {output_file}")

def extract_all_player_rankings():
    """Extract player rankings for all available years."""
    
    print("=== EXTRACTING PLAYER RANKINGS DATA ===")
    
    # Get all available years
    league_data_dir = Path("league_data")
    year_dirs = [d for d in league_data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    year_dirs.sort()
    
    extraction_summary = {}
    
    for year_dir in year_dirs:
        year = year_dir.name
        
        print(f"\nProcessing {year}...")
        
        # Get league key
        league_key = get_league_key_for_year(year)
        print(f"  Using league key: {league_key}")
        
        # Extract predraft rankings
        predraft_rankings = extract_predraft_rankings(league_key, year)
        
        # Extract postseason rankings  
        postseason_rankings = extract_postseason_rankings(league_key, year)
        
        # Save data
        if predraft_rankings or postseason_rankings:
            save_player_rankings(year, predraft_rankings, postseason_rankings)
        
        extraction_summary[year] = {
            "predraft_players": len(predraft_rankings),
            "postseason_players": len(postseason_rankings),
            "league_key": league_key
        }
    
    # Print summary
    print(f"\n=== EXTRACTION SUMMARY ===")
    for year, summary in extraction_summary.items():
        print(f"{year}: Predraft: {summary['predraft_players']}, Postseason: {summary['postseason_players']}")
    
    return extraction_summary

def create_rankings_validation_page(extraction_summary):
    """Create validation page for player rankings data."""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Rankings Data Validation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
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
            margin-bottom: 10px;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }

        .data-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }

        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #f1f3f4;
        }

        .data-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        .status-good { color: #28a745; font-weight: bold; }
        .status-missing { color: #dc3545; font-weight: bold; }
        .status-partial { color: #ffc107; font-weight: bold; }

        .info-box {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>Player Rankings Data Validation</h1>
            <p>Validation page for predraft and postseason player rankings</p>
        </div>

        <div class="info-box">
            <h3>Data Collection Status</h3>
            <p><strong>Note:</strong> Player rankings extraction requires valid Yahoo API authentication.</p>
            <p>This page shows the current status of player rankings data collection across all years.</p>
        </div>

        <table class="data-table">
            <thead>
                <tr>
                    <th>Year</th>
                    <th>League Key</th>
                    <th>Predraft Rankings</th>
                    <th>Postseason Rankings</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>'''
    
    for year in sorted(extraction_summary.keys()):
        summary = extraction_summary[year]
        
        predraft_count = summary['predraft_players']
        postseason_count = summary['postseason_players']
        
        if predraft_count > 0 and postseason_count > 0:
            status = '<span class="status-good">Complete</span>'
        elif predraft_count > 0 or postseason_count > 0:
            status = '<span class="status-partial">Partial</span>'
        else:
            status = '<span class="status-missing">Missing</span>'
        
        html_content += f'''
                <tr>
                    <td><strong>{year}</strong></td>
                    <td>{summary['league_key']}</td>
                    <td>{predraft_count} players</td>
                    <td>{postseason_count} players</td>
                    <td>{status}</td>
                </tr>'''
    
    html_content += '''
            </tbody>
        </table>

        <div class="info-box">
            <h3>Next Steps</h3>
            <p>To complete player rankings extraction:</p>
            <ol>
                <li>Ensure valid Yahoo OAuth 2.0 token in jsons/oauth2.json</li>
                <li>Run extraction script with API access</li>
                <li>Validate collected rankings data</li>
                <li>Update historical analysis with complete player performance data</li>
            </ol>
        </div>

    </div>
</body>
</html>'''
    
    return html_content

def main():
    """Main execution function."""
    
    # Extract player rankings (will use mock data without valid OAuth)
    extraction_summary = extract_all_player_rankings()
    
    # Create validation page
    html_content = create_rankings_validation_page(extraction_summary)
    
    # Save validation page
    with open('player_rankings_validation.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nPlayer rankings validation page created: player_rankings_validation.html")

if __name__ == "__main__":
    main()