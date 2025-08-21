#!/usr/bin/env python3
"""
Update simple_working.html with the recalculated value scores.
"""

import json
import os

def update_simple_working_html():
    """Update simple_working.html with new player data."""
    
    print("=== UPDATING SIMPLE_WORKING.HTML WITH NEW DATA ===\n")
    
    # Load the updated drafted players data
    with open('html_reports/data/drafted_players.json', 'r', encoding='utf-8') as f:
        drafted_data = json.load(f)
    
    drafted_players = drafted_data['players']
    print(f"Loaded {len(drafted_players)} drafted players with updated value scores")
    
    # Load the current HTML file
    html_file = 'html_reports/prod_ready/simple_working.html'
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the embedded data section and replace it
    start_marker = 'window.PLAYER_DATA = '
    end_marker = '};'
    
    start_pos = html_content.find(start_marker)
    if start_pos == -1:
        print("Could not find data section in HTML file")
        return
    
    # Find the end of the data object
    start_pos += len(start_marker)
    
    # Count braces to find the end
    brace_count = 0
    end_pos = start_pos
    for i, char in enumerate(html_content[start_pos:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = start_pos + i + 1
                break
    
    # Create new data section
    new_data = json.dumps(drafted_players, separators=(',', ':'))
    new_data_section = f'{new_data}'
    
    # Replace the data section
    new_html_content = (
        html_content[:start_pos] + 
        new_data_section + 
        html_content[end_pos:]
    )
    
    # Write the updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_html_content)
    
    print(f"Updated {html_file} with new player data")
    print(f"File size: {os.path.getsize(html_file) / 1024:.1f} KB")
    
    # Verify a few value scores
    print("\nSample value scores from updated data:")
    sample_players = list(drafted_players.items())[:5]
    for player_id, player in sample_players:
        if 'value_analysis' in player and 'value_score' in player['value_analysis']:
            vs = player['value_analysis']['value_score']
            perf = player['value_analysis']['performance_percentile']
            cost = player['value_analysis']['avg_cost']
            print(f"  {player['player_name']}: {vs:.2f} ({perf:.1f}th percentile, ${cost:.0f} avg cost)")

if __name__ == "__main__":
    update_simple_working_html()