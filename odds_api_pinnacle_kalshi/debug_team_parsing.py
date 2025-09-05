#!/usr/bin/env python3

"""
Debug how the WSU vs SDSU game is parsed by the Kalshi client
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from kalshi.client import KalshiClient

def debug_wsu_parsing():
    """Debug the team parsing for WSU vs SDSU"""
    
    client = KalshiClient()
    
    # Test the parsing function directly
    game_id = "SDSUWSU"  # From the ticker KXNCAAFGAME-25SEP06SDSUWSU-WSU
    
    print(f"Testing game_id: {game_id}")
    
    # Call the internal parsing method
    result = client._parse_college_teams(game_id)
    
    if result:
        print(f"Parsed result:")
        print(f"  Home team: {result['home_team']}")
        print(f"  Away team: {result['away_team']}")
    else:
        print("Failed to parse teams")
    
    # Also test with the college team mappings
    print(f"\nCollege team mappings relevant to WSU/SDSU:")
    
    # Check what the mapping contains for these teams
    college_teams = {
        'WSU': 'Washington St.',
        'SDSU': 'San Diego St.',
        'WASH': 'Washington',
        'UW': 'Washington'
    }
    
    for code, name in college_teams.items():
        print(f"  {code}: {name}")
        
    # Test the parsing logic manually
    print(f"\nManual parsing test:")
    if game_id.endswith('WSU'):
        prefix = game_id[:-3]  # Remove 'WSU'
        print(f"  Prefix: {prefix}")
        if prefix in college_teams:
            print(f"  Found prefix mapping: {prefix} -> {college_teams[prefix]}")
            print(f"  Result would be: {college_teams[prefix]} @ Washington St.")
    
if __name__ == "__main__":
    debug_wsu_parsing()