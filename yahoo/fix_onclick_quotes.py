#!/usr/bin/env python3
"""
Quick fix for malformed onclick handlers in player_analysis.html
"""
import re

def fix_malformed_onclick():
    # Read the HTML file
    with open('html_reports/prod_ready/player_analysis.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Fix malformed onclick handlers like: onclick="togglePlayerStats(&quot;Name'Part&#39;, this)"
    # Should be: onclick="togglePlayerStats(&quot;Name'Part&quot;, this)"
    
    # Pattern to match malformed onclick handlers
    def fix_onclick_handler(match):
        onclick_attr = match.group(0)
        print(f"Found malformed onclick: {onclick_attr}")
        
        # Try different patterns to extract player name
        player_name = None
        
        # Pattern 1: &quot;Name&#39; 
        name_match = re.search(r'&quot;([^&]+)&#39;', onclick_attr)
        if name_match:
            player_name = name_match.group(1)
        
        # Pattern 2: &#39;Name&#39;
        if not player_name:
            name_match = re.search(r'&#39;([^&]+)&#39;', onclick_attr)
            if name_match:
                player_name = name_match.group(1)
        
        # Pattern 3: &#39;Name&quot;
        if not player_name:
            name_match = re.search(r'&#39;([^&]+)&quot;', onclick_attr)
            if name_match:
                player_name = name_match.group(1)
        
        if player_name:
            fixed = f'onclick="togglePlayerStats(&quot;{player_name}&quot;, this)"'
            print(f"Fixed to: {fixed}")
            return fixed
        else:
            print(f"Couldn't extract name from: {onclick_attr}")
            return onclick_attr
    
    # Apply the fix - find all onclick handlers that have mixed quote entities
    malformed_patterns = [
        r'onclick="togglePlayerStats\([^)]*&#39;[^)]*\)"',  # Contains &#39;
        r'onclick="togglePlayerStats\([^)]*&quot;[^)]*&#39;[^)]*\)"',  # Mixed quotes
    ]
    
    original_count = 0
    for pattern in malformed_patterns:
        original_count += len(re.findall(pattern, html_content))
    
    print(f"Found {original_count} malformed onclick handlers")
    
    # Fix all malformed patterns
    for pattern in malformed_patterns:
        html_content = re.sub(pattern, fix_onclick_handler, html_content)
    
    # Verify the fix
    remaining_count = 0
    for pattern in malformed_patterns:
        remaining_count += len(re.findall(pattern, html_content))
    print(f"Remaining malformed handlers: {remaining_count}")
    
    # Save the fixed file
    with open('html_reports/prod_ready/player_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Fixed malformed onclick handlers!")

if __name__ == "__main__":
    fix_malformed_onclick()