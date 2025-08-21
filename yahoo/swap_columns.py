#!/usr/bin/env python3
"""
Swap the 3rd and 4th data columns in owner analysis HTML.
Currently: Team Name | Final Rank | Playoff Seed | Record
Want: Team Name | Playoff Seed | Final Rank | Record
"""

import re

def swap_data_columns():
    """Swap the 3rd and 4th data columns in all table rows."""
    
    file_path = 'html_reports/prod_ready/owner_analysis.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match table rows with data
    # Looks for: <td>data</td><td>data</td><td>data1</td><td>data2</td><td>data</td><td>data</td>
    # We want to swap data1 and data2 (the 3rd and 4th columns)
    
    pattern = r'(<td><strong>\d{4}</strong></td>\s*<td>[^<]+</td>\s*<td>)([^<]+)(</td>\s*<td>)([^<]+)(</td>\s*<td>[^<]+</td>\s*<td>[^<]+</td>)'
    
    def swap_columns(match):
        before = match.group(1)  # <td><strong>year</strong></td><td>team</td><td>
        col1 = match.group(2)    # first data column (currently final rank)
        middle = match.group(3)  # </td><td>
        col2 = match.group(4)    # second data column (currently playoff seed)
        after = match.group(5)   # </td><td>record</td><td>winpct</td>
        
        # Swap col1 and col2
        return before + col2 + middle + col1 + after
    
    updated_content = re.sub(pattern, swap_columns, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Swapped data columns in owner analysis HTML")
    print("Now: Team Name | Regular Season | Playoffs | Record")

if __name__ == "__main__":
    swap_data_columns()