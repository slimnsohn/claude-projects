#!/usr/bin/env python3
"""
Comprehensive Yahoo Fantasy Player Ranking Extractor
Extracts preseason and end-of-season ranking data for all available years.
"""

from yahoo_oauth import OAuth2
import yahoo_fantasy_api
import json
import os
from collections import defaultdict
import pandas as pd

# Handle Unicode encoding issues
import sys
import codecs
import locale

def safe_unicode_write(text):
    """Safely handle Unicode characters for Windows console output."""
    if hasattr(sys.stdout, 'buffer'):
        return text.encode('utf-8', errors='replace').decode('utf-8')
    return text.encode('ascii', errors='replace').decode('ascii')

def extract_player_rankings_for_year(year, league_key):
    """
    Extract comprehensive ranking data for a specific year.
    """
    print(f"\\n=== EXTRACTING RANKINGS FOR {year} ===")
    
    try:
        oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
        league = yahoo_fantasy_api.league.League(oauth, league_key)
        
        # Get league settings to understand season status
        settings = league.settings()
        is_finished = settings.get('is_finished', False)
        season_status = "completed" if is_finished else "in_progress"
        
        ranking_data = {
            'year': int(year),
            'league_key': league_key,
            'season_status': season_status,
            'extraction_timestamp': pd.Timestamp.now().isoformat(),
            'player_ownership_rankings': [],
            'advanced_stat_rankings': [],
            'draft_order_rankings': [],
            'stat_id_analysis': {},
            'extraction_notes': []
        }
        
        print(f"League status: {season_status}")
        
        # 1. Extract ownership-based rankings (proxy for season-end popularity)
        print("Extracting ownership rankings...")
        try:
            all_ownership_data = []
            positions = ['PG', 'SG', 'SF', 'PF', 'C']
            
            for pos in positions:
                free_agents = league.free_agents(pos)
                for player in free_agents:
                    try:
                        # Handle potential Unicode in player names
                        name = player['name']
                        if isinstance(name, dict):
                            player_name = safe_unicode_write(name.get('full', 'Unknown'))
                        else:
                            player_name = safe_unicode_write(str(name))
                        
                        ownership_pct = 0
                        if 'percent_owned' in player:
                            if isinstance(player['percent_owned'], dict):
                                ownership_pct = float(player['percent_owned'].get('value', 0))
                            else:
                                ownership_pct = float(player['percent_owned'])
                        
                        all_ownership_data.append({
                            'player_id': player['player_id'],
                            'player_name': player_name,
                            'position': pos,
                            'ownership_percentage': ownership_pct,
                            'status': player.get('status', ''),
                            'is_free_agent': True
                        })
                        
                    except Exception as e:
                        ranking_data['extraction_notes'].append(f"Error processing free agent: {e}")
            
            # Sort by ownership (highest = most popular/valuable at season end)
            all_ownership_data.sort(key=lambda x: x['ownership_percentage'], reverse=True)
            
            # Add ownership rankings
            for rank, player in enumerate(all_ownership_data, 1):
                player['ownership_rank'] = rank
            
            ranking_data['player_ownership_rankings'] = all_ownership_data
            ranking_data['extraction_notes'].append(f"Extracted ownership data for {len(all_ownership_data)} free agents")
            
        except Exception as e:
            ranking_data['extraction_notes'].append(f"Error extracting ownership data: {e}")
        
        # 2. Extract draft order as preseason rankings
        print("Extracting draft order rankings...")
        try:
            draft_results = league.draft_results()
            draft_rankings = []
            
            for pick in draft_results:
                try:
                    # Get player details
                    player_id = pick['player_id']
                    details = league.player_details(player_id)
                    
                    if details and len(details) > 0:
                        player_data = details[0]
                        name = player_data.get('name', {})
                        player_name = safe_unicode_write(name.get('full', f"Player {player_id}"))
                        
                        draft_info = {
                            'player_id': player_id,
                            'player_name': player_name,
                            'draft_pick': pick['pick'],
                            'draft_round': pick['round'],
                            'draft_cost': pick['cost'],
                            'preseason_rank': pick['pick'],  # Draft position = preseason ranking
                            'team_key': pick['team_key']
                        }
                        
                        draft_rankings.append(draft_info)
                        
                except Exception as e:
                    ranking_data['extraction_notes'].append(f"Error processing draft pick: {e}")
            
            # Sort by draft position (preseason rankings)
            draft_rankings.sort(key=lambda x: x['draft_pick'])
            ranking_data['draft_order_rankings'] = draft_rankings
            ranking_data['extraction_notes'].append(f"Extracted preseason rankings for {len(draft_rankings)} drafted players")
            
        except Exception as e:
            ranking_data['extraction_notes'].append(f"Error extracting draft data: {e}")
        
        # 3. Analyze advanced stat IDs that might be rankings
        print("Analyzing advanced stat IDs...")
        try:
            stat_id_data = defaultdict(list)
            
            # Sample top 20 draft picks for analysis
            draft_results = league.draft_results()
            for pick in draft_results[:20]:
                player_id = pick['player_id']
                details = league.player_details(player_id)
                
                if details and len(details) > 0:
                    player_data = details[0]
                    name = player_data.get('name', {})
                    player_name = safe_unicode_write(name.get('full', f"Player {player_id}"))
                    
                    # Analyze player stats
                    if 'player_stats' in player_data:
                        stats = player_data['player_stats'].get('stats', [])
                        
                        for stat in stats:
                            if isinstance(stat, dict) and 'stat' in stat:
                                stat_info = stat['stat']
                                stat_id = stat_info.get('stat_id', '')
                                value = stat_info.get('value', '')
                                
                                # Focus on high ID stats that might be rankings
                                if isinstance(stat_id, str) and stat_id.isdigit():
                                    stat_id_num = int(stat_id)
                                    if stat_id_num > 9000000:  # Very high IDs likely advanced stats
                                        stat_id_data[stat_id].append({
                                            'player_id': player_id,
                                            'player_name': player_name,
                                            'value': value,
                                            'draft_pick': pick['pick']
                                        })
            
            # Analyze patterns in these stat IDs
            for stat_id, values in stat_id_data.items():
                if len(values) >= 5:  # Only analyze if we have enough samples
                    # Check if values look like rankings/percentiles
                    numeric_values = []
                    fraction_values = []
                    
                    for entry in values:
                        val = entry['value']
                        if '/' in str(val):
                            # Looks like a fraction (rank/total or made/attempted)
                            try:
                                parts = str(val).split('/')
                                if len(parts) == 2:
                                    numerator = float(parts[0])
                                    denominator = float(parts[1])
                                    if denominator > 0:
                                        percentage = (numerator / denominator) * 100
                                        fraction_values.append({
                                            'player_name': entry['player_name'],
                                            'raw_value': val,
                                            'percentage': percentage,
                                            'draft_pick': entry['draft_pick']
                                        })
                            except:
                                pass
                        else:
                            try:
                                numeric_values.append(float(val))
                            except:
                                pass
                    
                    if fraction_values or numeric_values:
                        ranking_data['stat_id_analysis'][stat_id] = {
                            'sample_size': len(values),
                            'fraction_samples': fraction_values[:10],  # Top 10 samples
                            'numeric_samples': numeric_values[:10],
                            'potential_ranking_stat': len(fraction_values) > len(values) * 0.8  # Most values are fractions
                        }
            
            ranking_data['extraction_notes'].append(f"Analyzed {len(stat_id_data)} high-ID stats")
            
        except Exception as e:
            ranking_data['extraction_notes'].append(f"Error analyzing stat IDs: {e}")
        
        # 4. Save the ranking data
        output_dir = f'league_data/{year}/processed_data'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'player_rankings.json')
        
        # Handle Unicode properly when writing JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ranking_data, f, indent=2, ensure_ascii=False)
        
        print(f"SUCCESS: Rankings saved to {output_file}")
        print(f"  - Ownership rankings: {len(ranking_data['player_ownership_rankings'])} players")
        print(f"  - Draft rankings: {len(ranking_data['draft_order_rankings'])} players")
        print(f"  - Advanced stats analyzed: {len(ranking_data['stat_id_analysis'])} stat types")
        
        return ranking_data
        
    except Exception as e:
        print(f"ERROR: Failed to extract rankings for {year}: {e}")
        return None

def extract_all_years_rankings():
    """
    Extract ranking data for all available years.
    """
    print("=== COMPREHENSIVE RANKING EXTRACTION FOR ALL YEARS ===\\n")
    
    # Load league keys for all years
    league_keys_file = 'league_data/master_data/league_keys.json'
    if not os.path.exists(league_keys_file):
        print("ERROR: League keys file not found. Please run comprehensive_data_extractor.py first.")
        return
    
    with open(league_keys_file, 'r') as f:
        league_data = json.load(f)
    
    # Extract just the league_keys section
    league_keys = league_data.get('league_keys', {})
    
    print(f"Found league keys for {len(league_keys)} years")
    
    successful_extractions = []
    failed_extractions = []
    
    # Process each year
    for year_str, league_key in league_keys.items():
        try:
            year = int(year_str)
            if year >= 2020:  # Start with recent years that are more likely to work
                result = extract_player_rankings_for_year(year, league_key)
                if result:
                    successful_extractions.append(year)
                else:
                    failed_extractions.append(year)
        except Exception as e:
            print(f"ERROR: Failed to process year {year_str}: {e}")
            failed_extractions.append(year_str)
    
    # Summary
    print(f"\\n=== EXTRACTION SUMMARY ===")
    print(f"Successful: {len(successful_extractions)} years - {successful_extractions}")
    print(f"Failed: {len(failed_extractions)} years - {failed_extractions}")
    
    # Create summary report
    summary = {
        'extraction_date': pd.Timestamp.now().isoformat(),
        'successful_years': successful_extractions,
        'failed_years': failed_extractions,
        'total_years_processed': len(successful_extractions) + len(failed_extractions),
        'success_rate': len(successful_extractions) / max(1, len(successful_extractions) + len(failed_extractions))
    }
    
    with open('league_data/master_data/ranking_extraction_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Extraction summary saved to league_data/master_data/ranking_extraction_summary.json")

if __name__ == "__main__":
    # Test with a single year first
    print("Testing with 2024 first...")
    test_result = extract_player_rankings_for_year('2024', '454.l.44006')
    
    if test_result:
        print("\\nTest successful! Proceeding with all years...")
        extract_all_years_rankings()
    else:
        print("\\nTest failed. Check the error messages above.")