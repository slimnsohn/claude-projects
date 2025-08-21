#!/usr/bin/env python3
"""
Quick Player Ranking Extractor
Focus on getting preseason (draft order) and end-of-season (ownership) rankings.
"""

from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import os

def extract_rankings_for_year(year, league_key):
    """
    Extract ranking data for a specific year (simplified version).
    """
    print(f"Extracting rankings for {year}...")
    
    try:
        oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
        league = yahoo_fantasy_api.league.League(oauth, league_key)
        
        ranking_data = {
            'year': int(year),
            'league_key': league_key,
            'preseason_rankings': [],  # Based on draft order
            'end_season_rankings': []  # Based on ownership %
        }
        
        # 1. Get preseason rankings from draft order
        print(f"  Getting draft order (preseason rankings)...")
        try:
            draft_results = league.draft_results()
            for pick in draft_results:
                player_id = pick['player_id']
                
                # Get player name
                try:
                    details = league.player_details(player_id)
                    if details and len(details) > 0:
                        name = details[0].get('name', {})
                        player_name = name.get('full', f"Player {player_id}") if isinstance(name, dict) else str(name)
                        
                        ranking_data['preseason_rankings'].append({
                            'player_id': player_id,
                            'player_name': player_name.encode('ascii', errors='replace').decode('ascii'),  # Handle Unicode
                            'preseason_rank': pick['pick'],
                            'draft_cost': pick['cost']
                        })
                except:
                    # If we can't get player details, still record the ranking
                    ranking_data['preseason_rankings'].append({
                        'player_id': player_id,
                        'player_name': f"Player {player_id}",
                        'preseason_rank': pick['pick'],
                        'draft_cost': pick['cost']
                    })
            
            print(f"    Found {len(ranking_data['preseason_rankings'])} preseason rankings")
            
        except Exception as e:
            print(f"    Error getting draft data: {e}")
        
        # 2. Get end-of-season rankings from ownership percentages (for free agents)
        print(f"  Getting ownership data (end-season popularity)...")
        try:
            ownership_data = []
            
            # Get free agents (these have ownership percentages)
            for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
                free_agents = league.free_agents(pos)
                
                for player in free_agents[:50]:  # Limit to top 50 per position
                    try:
                        name = player['name']
                        player_name = name.get('full', 'Unknown') if isinstance(name, dict) else str(name)
                        player_name = player_name.encode('ascii', errors='replace').decode('ascii')  # Handle Unicode
                        
                        ownership_pct = 0
                        if 'percent_owned' in player:
                            if isinstance(player['percent_owned'], dict):
                                ownership_pct = float(player['percent_owned'].get('value', 0))
                            else:
                                ownership_pct = float(player['percent_owned'])
                        
                        ownership_data.append({
                            'player_id': player['player_id'],
                            'player_name': player_name,
                            'ownership_percentage': ownership_pct,
                            'position': pos
                        })
                        
                    except Exception as e:
                        continue  # Skip problematic players
            
            # Sort by ownership percentage and add ranks
            ownership_data.sort(key=lambda x: x['ownership_percentage'], reverse=True)
            for rank, player in enumerate(ownership_data, 1):
                player['end_season_rank'] = rank
            
            ranking_data['end_season_rankings'] = ownership_data[:100]  # Top 100
            print(f"    Found {len(ranking_data['end_season_rankings'])} end-season rankings")
            
        except Exception as e:
            print(f"    Error getting ownership data: {e}")
        
        # 3. Save the data
        output_dir = f'league_data/{year}/processed_data'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'player_rankings.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ranking_data, f, indent=2, ensure_ascii=False)
        
        print(f"  SUCCESS: Saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """
    Extract rankings for available years.
    """
    print("=== QUICK RANKING EXTRACTION ===\\n")
    
    # Test years (start with recent ones that are more likely to work)
    test_years = [
        ('2024', '454.l.44006'),
        ('2023', '428.l.32747'),
        ('2022', '418.l.104779'),
        ('2021', '410.l.124782'),
        ('2020', '402.l.121244')
    ]
    
    successful = []
    failed = []
    
    for year, league_key in test_years:
        if extract_rankings_for_year(year, league_key):
            successful.append(year)
        else:
            failed.append(year)
    
    print(f"\\n=== SUMMARY ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    main()