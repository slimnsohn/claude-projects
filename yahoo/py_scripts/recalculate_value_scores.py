#!/usr/bin/env python3
"""
Recalculate value scores using proper category ranking method.
Each of the 9 fantasy categories is ranked independently, then combined.
"""

import json
import os
import pandas as pd
import numpy as np

def load_player_data():
    """Load current player data."""
    
    print("=== LOADING PLAYER DATA ===\n")
    
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data['players']
    print(f"Loaded {len(players)} players")
    
    return players

def calculate_proper_value_scores(players):
    """Calculate value scores using category ranking method."""
    
    print("=== CALCULATING PROPER VALUE SCORES ===\n")
    
    # Extract players with both draft history and season stats
    analysis_players = []
    
    for player_id, player in players.items():
        # Must have draft history and recent season stats
        if (player.get('yahoo_draft_history') and 
            len(player['yahoo_draft_history']) > 0 and
            player.get('seasons') and 
            len(player['seasons']) > 0):
            
            # Get most recent season stats
            recent_year = max(player['seasons'].keys())
            recent_stats = player['seasons'][recent_year]
            
            # Calculate average draft cost
            costs = [draft['draft_cost'] for draft in player['yahoo_draft_history'] if draft['draft_cost'] > 0]
            if costs:
                avg_cost = sum(costs) / len(costs)
                
                analysis_player = {
                    'player_id': player_id,
                    'player_name': player['player_name'],
                    'avg_cost': avg_cost,
                    'times_drafted': len(player['yahoo_draft_history']),
                    # 9 fantasy categories
                    'fg_pct': recent_stats.get('fg_pct', 0),
                    'ft_pct': recent_stats.get('ft_pct', 0), 
                    'threepm_pg': recent_stats.get('threepm_pg', 0),
                    'pts_pg': recent_stats.get('pts_pg', 0),
                    'reb_pg': recent_stats.get('reb_pg', 0),
                    'ast_pg': recent_stats.get('ast_pg', 0),
                    'stl_pg': recent_stats.get('stl_pg', 0),
                    'blk_pg': recent_stats.get('blk_pg', 0),
                    'to_pg': recent_stats.get('to_pg', 0)
                }
                
                analysis_players.append(analysis_player)
    
    print(f"Found {len(analysis_players)} players with draft history and stats")
    
    if len(analysis_players) < 10:
        print("Not enough players for ranking analysis")
        return {}
    
    # Convert to DataFrame for easier ranking
    df = pd.DataFrame(analysis_players)
    
    # Rank each category (1 = best, higher numbers = worse)
    # For most categories, higher is better, but for turnovers, lower is better
    print("Ranking players in each category...")
    
    # Higher is better categories
    df['fg_pct_rank'] = df['fg_pct'].rank(ascending=False)
    df['ft_pct_rank'] = df['ft_pct'].rank(ascending=False)
    df['threepm_pg_rank'] = df['threepm_pg'].rank(ascending=False)
    df['pts_pg_rank'] = df['pts_pg'].rank(ascending=False)
    df['reb_pg_rank'] = df['reb_pg'].rank(ascending=False)
    df['ast_pg_rank'] = df['ast_pg'].rank(ascending=False)
    df['stl_pg_rank'] = df['stl_pg'].rank(ascending=False)
    df['blk_pg_rank'] = df['blk_pg'].rank(ascending=False)
    
    # Lower is better for turnovers
    df['to_pg_rank'] = df['to_pg'].rank(ascending=True)
    
    # Calculate composite rank (average of all category ranks)
    rank_columns = ['fg_pct_rank', 'ft_pct_rank', 'threepm_pg_rank', 'pts_pg_rank', 
                   'reb_pg_rank', 'ast_pg_rank', 'stl_pg_rank', 'blk_pg_rank', 'to_pg_rank']
    
    df['composite_rank'] = df[rank_columns].mean(axis=1)
    
    # Convert composite rank to percentile (0-100, where 100 is best)
    df['performance_percentile'] = 100 - (df['composite_rank'] - 1) / (len(df) - 1) * 100
    
    # Calculate value score: Performance per dollar
    # Higher performance percentile and lower cost = better value
    df['value_score'] = df['performance_percentile'] / df['avg_cost']
    
    # Create value score dictionary
    value_scores = {}
    
    for _, row in df.iterrows():
        player_id = row['player_id']
        value_scores[player_id] = {
            'performance_percentile': round(row['performance_percentile'], 1),
            'composite_rank': round(row['composite_rank'], 1),
            'value_score': round(row['value_score'], 2),
            'avg_cost': round(row['avg_cost'], 1),
            'category_ranks': {
                'fg_pct_rank': int(row['fg_pct_rank']),
                'ft_pct_rank': int(row['ft_pct_rank']),
                'threepm_pg_rank': int(row['threepm_pg_rank']),
                'pts_pg_rank': int(row['pts_pg_rank']),
                'reb_pg_rank': int(row['reb_pg_rank']),
                'ast_pg_rank': int(row['ast_pg_rank']),
                'stl_pg_rank': int(row['stl_pg_rank']),
                'blk_pg_rank': int(row['blk_pg_rank']),
                'to_pg_rank': int(row['to_pg_rank'])
            }
        }
    
    # Print some examples
    print("\nTop 5 performers (by percentile):")
    top_performers = df.nlargest(5, 'performance_percentile')
    for _, row in top_performers.iterrows():
        print(f"  {row['player_name']}: {row['performance_percentile']:.1f}th percentile, avg cost ${row['avg_cost']:.0f}")
    
    print("\nTop 5 values (by value score):")
    top_values = df.nlargest(5, 'value_score')
    for _, row in top_values.iterrows():
        print(f"  {row['player_name']}: {row['value_score']:.2f} value score (${row['avg_cost']:.0f}, {row['performance_percentile']:.1f}th percentile)")
    
    return value_scores

def update_player_data_with_new_scores(players, value_scores):
    """Update player data with new value scores."""
    
    print(f"\n=== UPDATING PLAYER DATA ===\n")
    
    updated_count = 0
    
    for player_id, player in players.items():
        if player_id in value_scores:
            # Update value analysis
            if 'value_analysis' not in player:
                player['value_analysis'] = {}
            
            player['value_analysis'].update(value_scores[player_id])
            updated_count += 1
    
    print(f"Updated {updated_count} players with new value scores")
    
    return players

def save_updated_data(players):
    """Save updated player data."""
    
    print("\n=== SAVING UPDATED DATA ===\n")
    
    # Save to main players file
    data = {'players': players}
    
    with open('html_reports/data/players.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Updated players.json with new value scores")
    
    # Also save just the drafted players for simple_working.html
    drafted_players = {}
    for player_id, player in players.items():
        if (player.get('yahoo_draft_history') and len(player['yahoo_draft_history']) > 0):
            drafted_players[player_id] = player
    
    drafted_data = {'players': drafted_players}
    
    with open('html_reports/data/drafted_players.json', 'w', encoding='utf-8') as f:
        json.dump(drafted_data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated drafted_players.json with {len(drafted_players)} players")

def update_simple_working_html():
    """Update the tooltip in simple_working.html with new formula."""
    
    print("\n=== UPDATING HTML TOOLTIP ===\n")
    
    file_path = 'html_reports/prod_ready/simple_working.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the tooltip text
        old_tooltip = 'Value Score: (PPG + RPG + APG + STL + BLK + 3PM - TO) / Average Draft Cost × 10. Higher is better. >1.5 = High Value, 0.8-1.5 = Medium, <0.8 = Low Value'
        
        new_tooltip = 'Value Score: Performance Percentile / Average Draft Cost. Each of the 9 fantasy categories (FG%, FT%, 3PM, PTS, REB, AST, STL, BLK, TO) is ranked independently, then combined into a performance percentile (0-100). Higher value score = better performance per dollar spent.'
        
        content = content.replace(old_tooltip, new_tooltip)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Updated simple_working.html tooltip with new formula")
        
    except Exception as e:
        print(f"Error updating HTML: {e}")

def main():
    """Main function to recalculate value scores."""
    
    print("=== RECALCULATING VALUE SCORES WITH PROPER RANKING ===\n")
    
    # Load current data
    players = load_player_data()
    
    # Calculate new value scores
    value_scores = calculate_proper_value_scores(players)
    
    if value_scores:
        # Update player data
        updated_players = update_player_data_with_new_scores(players, value_scores)
        
        # Save updated data
        save_updated_data(updated_players)
        
        # Update HTML tooltip
        update_simple_working_html()
        
        print("\n=== VALUE SCORE RECALCULATION COMPLETE ===")
        print("New formula: Performance Percentile / Average Draft Cost")
        print("Where Performance Percentile = composite ranking across all 9 fantasy categories")
        print("Files updated:")
        print("  - html_reports/data/players.json")
        print("  - html_reports/data/drafted_players.json") 
        print("  - html_reports/prod_ready/simple_working.html")
    else:
        print("Failed to calculate value scores")

if __name__ == "__main__":
    main()