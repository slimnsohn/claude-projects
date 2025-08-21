from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import pandas as pd
from difflib import SequenceMatcher
import os
import time

def similar(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def create_yahoo_nba_mapping():
    """
    Create mapping between Yahoo player IDs and NBA player IDs.
    Uses player names from both systems to create matches.
    """
    
    print("=== YAHOO-NBA PLAYER MAPPING ===\n")
    
    # Load NBA player mapping
    print("Loading NBA player mapping...")
    with open('historical_nba_stats/player_mappings/nba_player_mapping.json', 'r') as f:
        nba_players = json.load(f)
    
    print(f"Loaded {len(nba_players)} NBA players")
    
    # Initialize Yahoo connection
    print("Connecting to Yahoo Fantasy API...")
    oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
    
    # Use current league to get player data
    current_league_key = '454.l.44006'  # 2024 league
    league = yahoo_fantasy_api.league.League(oauth, current_league_key)
    
    print("Extracting Yahoo player data from recent years...")
    
    yahoo_players = {}
    all_league_years = [
        '454.l.44006',  # 2024
        '418.l.157217', # 2023
        '418.l.59628',  # 2022
        '414.l.82538',  # 2021
        '402.l.121244'  # 2020
    ]
    
    for league_key in all_league_years:
        try:
            print(f"Processing league {league_key}...")
            temp_league = yahoo_fantasy_api.league.League(oauth, league_key)
            
            # Get draft results to find player IDs
            draft_results = temp_league.draft_results()
            print(f"  Found {len(draft_results)} draft picks")
            
            for pick in draft_results:
                player_id = pick['player_id']
                
                if player_id not in yahoo_players:
                    try:
                        # Get player details
                        player_info = temp_league.player_details(player_id)
                        if player_info and len(player_info) > 0:
                            player_data = player_info[0]
                            name = player_data['name']['full']
                            position = player_data.get('display_position', '')
                            team = player_data.get('editorial_team_abbr', '')
                            
                            yahoo_players[player_id] = {
                                'name': name,
                                'position': position,
                                'team': team,
                                'yahoo_id': player_id
                            }
                            
                    except Exception as e:
                        print(f"  Error getting details for player {player_id}: {e}")
                        continue
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"Error processing league {league_key}: {e}")
            continue
    
    print(f"Extracted {len(yahoo_players)} unique Yahoo players")
    
    # Create name-based mapping
    print("\nMatching players by name...")
    
    mapping_results = {
        'exact_matches': {},
        'high_confidence_matches': {},  # >0.9 similarity
        'possible_matches': {},         # 0.8-0.9 similarity
        'no_matches': {},
        'statistics': {}
    }
    
    # Create reverse lookup for NBA players by name
    nba_by_name = {}
    for nba_id, nba_data in nba_players.items():
        nba_name = nba_data['name'].lower()
        nba_by_name[nba_name] = {
            'nba_id': nba_id,
            'name': nba_data['name']
        }
    
    exact_count = 0
    high_conf_count = 0 
    possible_count = 0
    no_match_count = 0
    
    for yahoo_id, yahoo_data in yahoo_players.items():
        yahoo_name = yahoo_data['name'].lower()
        
        # Try exact match first
        if yahoo_name in nba_by_name:
            nba_match = nba_by_name[yahoo_name]
            mapping_results['exact_matches'][yahoo_id] = {
                'yahoo_name': yahoo_data['name'],
                'nba_name': nba_match['name'], 
                'nba_id': nba_match['nba_id'],
                'yahoo_position': yahoo_data['position'],
                'yahoo_team': yahoo_data['team'],
                'match_type': 'exact'
            }
            exact_count += 1
            continue
        
        # Try similarity matching
        best_match = None
        best_similarity = 0
        
        for nba_name, nba_data in nba_by_name.items():
            similarity = similar(yahoo_name, nba_name)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = nba_data
        
        if best_similarity >= 0.9:
            mapping_results['high_confidence_matches'][yahoo_id] = {
                'yahoo_name': yahoo_data['name'],
                'nba_name': best_match['name'],
                'nba_id': best_match['nba_id'],
                'yahoo_position': yahoo_data['position'],
                'yahoo_team': yahoo_data['team'],
                'similarity': round(best_similarity, 3),
                'match_type': 'high_confidence'
            }
            high_conf_count += 1
            
        elif best_similarity >= 0.8:
            mapping_results['possible_matches'][yahoo_id] = {
                'yahoo_name': yahoo_data['name'],
                'nba_name': best_match['name'],
                'nba_id': best_match['nba_id'],
                'yahoo_position': yahoo_data['position'],
                'yahoo_team': yahoo_data['team'],
                'similarity': round(best_similarity, 3),
                'match_type': 'possible'
            }
            possible_count += 1
            
        else:
            mapping_results['no_matches'][yahoo_id] = {
                'yahoo_name': yahoo_data['name'],
                'yahoo_position': yahoo_data['position'],
                'yahoo_team': yahoo_data['team'],
                'best_similarity': round(best_similarity, 3),
                'best_match_name': best_match['name'] if best_match else 'None'
            }
            no_match_count += 1
    
    # Statistics
    mapping_results['statistics'] = {
        'total_yahoo_players': len(yahoo_players),
        'exact_matches': exact_count,
        'high_confidence_matches': high_conf_count,
        'possible_matches': possible_count,
        'no_matches': no_match_count,
        'match_rate': round((exact_count + high_conf_count) / len(yahoo_players) * 100, 1)
    }
    
    print(f"\nMapping Results:")
    print(f"  Exact matches: {exact_count}")
    print(f"  High confidence (>90% similar): {high_conf_count}")
    print(f"  Possible matches (80-90% similar): {possible_count}")
    print(f"  No good matches: {no_match_count}")
    print(f"  Overall match rate: {mapping_results['statistics']['match_rate']}%")
    
    # Save mapping results
    output_file = 'historical_nba_stats/player_mappings/yahoo_nba_mapping.json'
    with open(output_file, 'w') as f:
        json.dump(mapping_results, f, indent=2)
    
    print(f"\nMapping saved to: {output_file}")
    
    # Create consolidated mapping for easy lookup
    consolidated = {}
    
    # Add exact and high confidence matches to consolidated mapping
    for yahoo_id, match_data in mapping_results['exact_matches'].items():
        consolidated[yahoo_id] = {
            'nba_id': match_data['nba_id'],
            'player_name': match_data['yahoo_name'],
            'match_confidence': 'exact'
        }
    
    for yahoo_id, match_data in mapping_results['high_confidence_matches'].items():
        consolidated[yahoo_id] = {
            'nba_id': match_data['nba_id'], 
            'player_name': match_data['yahoo_name'],
            'match_confidence': 'high'
        }
    
    consolidated_file = 'historical_nba_stats/player_mappings/yahoo_to_nba_lookup.json'
    with open(consolidated_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"Consolidated lookup saved to: {consolidated_file}")
    print(f"Ready for analysis: {len(consolidated)} players with reliable NBA data matches")
    
    return mapping_results

if __name__ == "__main__":
    create_yahoo_nba_mapping()