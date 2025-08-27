#!/usr/bin/env python3
"""
Quick Historical Team Analysis
Extract team draft costs and use simplified projection estimation
"""

import json
import pandas as pd
import numpy as np

def load_players_data():
    """Load the players data."""
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def estimate_player_projection(player_info, target_year):
    """Estimate a player's fantasy value for a given year using available stats."""
    
    seasons = player_info.get('seasons', {})
    
    # Get stats from year before target (what we'd know at draft time)
    prev_year = target_year - 1
    prev_stats = seasons.get(str(prev_year))
    
    if not prev_stats:
        # Try 2 years before
        prev_stats = seasons.get(str(prev_year - 1))
    
    if not prev_stats:
        return 300  # Default for unknown players
    
    # Simple fantasy value estimation based on category contributions
    try:
        # Normalize stats to per-game basis over 70 games (typical season)
        games = prev_stats.get('games_played', 70)
        multiplier = min(70 / max(games, 20), 2.0)  # Cap at 2x multiplier
        
        # Category values (approximate percentile contributions)
        fg_pct = prev_stats.get('fg_pct', 0.45) * 100  # Convert to percentile-like
        ft_pct = prev_stats.get('ft_pct', 0.75) * 100
        threepm = prev_stats.get('threepm_pg', 0) * multiplier * 15  # 3PM value
        pts = prev_stats.get('pts_pg', 0) * multiplier * 2.5  # Points value  
        reb = prev_stats.get('reb_pg', 0) * multiplier * 8  # Rebounds value
        ast = prev_stats.get('ast_pg', 0) * multiplier * 10  # Assists value
        stl = prev_stats.get('stl_pg', 0) * multiplier * 25  # Steals value
        blk = prev_stats.get('blk_pg', 0) * multiplier * 25  # Blocks value
        to_penalty = prev_stats.get('to_pg', 0) * multiplier * -15  # TO penalty
        
        # Combine into rough fantasy value
        total_value = (fg_pct + ft_pct + threepm + pts + reb + ast + stl + blk + to_penalty)
        
        # Adjust based on games played (durability factor)
        if games < 50:
            total_value *= 0.8
        elif games > 75:
            total_value *= 1.1
            
        return max(200, min(800, int(total_value)))  # Cap between 200-800
        
    except:
        return 300

def analyze_historical_teams():
    """Analyze historical team performance with estimated projections."""
    
    players_data = load_players_data()
    
    # Load final rankings from available data
    final_rankings = {}
    
    # Load draft results if available
    try:
        df = pd.read_csv('jsons/draft_results.csv')
        for _, row in df.iterrows():
            year = int(row['year'])
            team = row['team_name']
            
            if year not in final_rankings:
                final_rankings[year] = {}
            
            final_rankings[year][team] = {
                'final_rank': int(row.get('final_rank', 99)),
                'regular_season_rank': int(row.get('regular_season_rank', 99))
            }
    except:
        print("No draft_results.csv found")
    
    # Load 2020 rankings if available  
    try:
        df_2020 = pd.read_csv('jsons/2020_ranks_pre.csv')
        if 2020 not in final_rankings:
            final_rankings[2020] = {}
        
        for _, row in df_2020.iterrows():
            team = row['team_name']
            final_rankings[2020][team] = {
                'final_rank': int(row['final_rank']),
                'regular_season_rank': int(row.get('regular_season_rank', row['final_rank']))
            }
    except:
        print("No 2020_ranks_pre.csv found")
    
    # Group drafts by year and team
    teams_by_year = {}
    
    for player_id, player_info in players_data['players'].items():
        player_name = player_info['player_name']
        draft_history = player_info.get('yahoo_draft_history', [])
        
        for draft in draft_history:
            year = draft['year']
            team = draft['fantasy_team']
            cost = draft.get('draft_cost', 1)
            
            if year not in teams_by_year:
                teams_by_year[year] = {}
            if team not in teams_by_year[year]:
                teams_by_year[year][team] = []
            
            # Estimate projection for this player
            estimated_projection = estimate_player_projection(player_info, year)
            
            teams_by_year[year][team].append({
                'player': player_name,
                'cost': cost,
                'estimated_projection': estimated_projection
            })
    
    # Calculate team totals and combine with rankings
    results = {}
    
    for year in sorted(teams_by_year.keys()):
        results[year] = []
        
        for team, roster in teams_by_year[year].items():
            total_projection = sum(p['estimated_projection'] for p in roster)
            total_cost = sum(p['cost'] for p in roster)
            
            # Get final ranking
            ranking_info = final_rankings.get(year, {}).get(team, {})
            final_rank = ranking_info.get('final_rank', 99)
            
            results[year].append({
                'team': team,
                'year': year,
                'preseason_projection': int(total_projection),
                'total_cost': int(total_cost),
                'roster_size': len(roster),
                'final_rank': final_rank,
                'regular_season_rank': ranking_info.get('regular_season_rank', 99)
            })
        
        # Sort by final rank
        results[year].sort(key=lambda x: x['final_rank'])
    
    return results

def print_results():
    """Print historical analysis results."""
    
    results = analyze_historical_teams()
    
    print("="*90)
    print("HISTORICAL TEAM ANALYSIS: ESTIMATED PRESEASON PROJECTIONS vs FINAL RANKINGS")
    print("="*90)
    
    for year in sorted(results.keys(), reverse=True):
        year_data = results[year]
        
        print(f"\n{year} SEASON")
        print("-" * 75)
        print(f"{'Team':<30} {'Est. Projection':<15} {'Draft Cost':<12} {'Roster':<8} {'Final Rank'}")
        print("-" * 75)
        
        for team_data in year_data:
            team = team_data['team'][:29]
            projection = team_data['preseason_projection']
            cost = team_data['total_cost']
            roster = team_data['roster_size']
            final_rank = team_data['final_rank']
            
            # Add tier indicators
            tier_indicator = ""
            if projection >= 7500:
                tier_indicator = "CHAMP"
            elif projection >= 7000:
                tier_indicator = "ELITE"
            elif projection >= 6500:
                tier_indicator = "STRONG"
            elif projection >= 6000:
                tier_indicator = "AVG"
            else:
                tier_indicator = "WEAK"
            
            rank_display = f"#{final_rank}" if final_rank < 99 else "N/A"
            
            print(f"{team:<30} {projection:<15} ${cost:<11} {roster:<8} {rank_display:<10} {tier_indicator}")
    
    # Summary stats
    print(f"\n{'='*90}")
    print("PROJECTION TIER PERFORMANCE ANALYSIS")
    print(f"{'='*90}")
    
    all_data = []
    for year_data in results.values():
        complete_data = [d for d in year_data if d['final_rank'] < 99 and d['preseason_projection'] > 0]
        all_data.extend(complete_data)
    
    if all_data:
        tiers = {
            'Championship (7500+)': [d for d in all_data if d['preseason_projection'] >= 7500],
            'Elite (7000-7499)': [d for d in all_data if 7000 <= d['preseason_projection'] < 7500],
            'Strong (6500-6999)': [d for d in all_data if 6500 <= d['preseason_projection'] < 7000],
            'Average (6000-6499)': [d for d in all_data if 6000 <= d['preseason_projection'] < 6500],
            'Below Average (<6000)': [d for d in all_data if d['preseason_projection'] < 6000]
        }
        
        for tier_name, tier_data in tiers.items():
            if tier_data:
                avg_rank = np.mean([d['final_rank'] for d in tier_data])
                top_4_count = len([d for d in tier_data if d['final_rank'] <= 4])
                top_4_pct = (top_4_count / len(tier_data)) * 100
                
                print(f"{tier_name:<20}: {len(tier_data):<3} teams | Avg Rank: {avg_rank:.1f} | Top-4 Rate: {top_4_pct:.0f}%")
    
    # Save results
    with open('html_reports/data/quick_historical_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: html_reports/data/quick_historical_analysis.json")
    print(f"Analyzed {len(all_data)} team-seasons across {len(results)} years")

if __name__ == "__main__":
    print_results()