#!/usr/bin/env python3
"""
Simple Draft Value Analysis

Finds the top 30 value players who outperformed their draft price
using the existing players.json data with draft history and performance.
"""

import json
import pandas as pd
import numpy as np

def load_player_data():
    """Load player data with draft history and performance."""
    print("Loading player data with draft history...")
    
    with open('html_reports/data/players.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    players = data['players']
    print(f"Loaded {len(players)} players")
    
    return players

def analyze_value_by_year(players, year=2024):
    """Analyze draft value for a specific year."""
    print(f"\\nAnalyzing draft value for {year}...")
    
    value_analysis = []
    
    for player_id, player_data in players.items():
        # Check if player has draft history
        draft_history = player_data.get('yahoo_draft_history', [])
        if not draft_history:
            continue
        
        # Find draft for this year
        year_draft = None
        for draft in draft_history:
            if draft.get('year') == year and draft.get('draft_cost', 0) > 0:
                year_draft = draft
                break
        
        if not year_draft:
            continue
        
        # Get performance for that year
        seasons = player_data.get('seasons', {})
        year_performance = seasons.get(str(year))
        
        if not year_performance:
            continue
        
        # Get value analysis if available
        value_data = player_data.get('value_analysis', {})
        
        # Calculate basic performance metrics
        games_played = year_performance.get('games_played', 0)
        if games_played < 20:  # Skip players with too few games
            continue
        
        # Use existing value score if available, otherwise calculate basic metric
        if 'value_score' in value_data:
            performance_score = value_data['value_score']
        else:
            # Basic performance calculation
            stats = [
                year_performance.get('pts_pg', 0),
                year_performance.get('reb_pg', 0),
                year_performance.get('ast_pg', 0),
                year_performance.get('stl_pg', 0),
                year_performance.get('blk_pg', 0),
                year_performance.get('threepm_pg', 0),
                year_performance.get('fg_pct', 0) * 100,
                year_performance.get('ft_pct', 0) * 100,
                max(0, 5 - year_performance.get('to_pg', 0))  # Turnovers penalty
            ]
            performance_score = sum(stats)
        
        draft_cost = year_draft['draft_cost']
        
        # Calculate value metrics
        value_per_dollar = performance_score / draft_cost if draft_cost > 0 else 0
        
        value_analysis.append({
            'player_name': player_data['player_name'],
            'draft_cost': draft_cost,
            'performance_score': performance_score,
            'value_per_dollar': value_per_dollar,
            'games_played': games_played,
            'team': year_performance.get('team', 'Unknown'),
            'fantasy_team': year_draft.get('fantasy_team', 'Unknown'),
            'pick_number': year_draft.get('pick_number', 0),
            # Stats
            'pts_pg': year_performance.get('pts_pg', 0),
            'reb_pg': year_performance.get('reb_pg', 0),
            'ast_pg': year_performance.get('ast_pg', 0),
            'stl_pg': year_performance.get('stl_pg', 0),
            'blk_pg': year_performance.get('blk_pg', 0),
            'threepm_pg': year_performance.get('threepm_pg', 0),
            'fg_pct': year_performance.get('fg_pct', 0),
            'ft_pct': year_performance.get('ft_pct', 0),
            'to_pg': year_performance.get('to_pg', 0)
        })
    
    return pd.DataFrame(value_analysis)

def calculate_expected_cost(df):
    """Calculate expected draft cost based on performance."""
    if df.empty:
        return df
    
    # Calculate average cost per performance point
    total_cost = df['draft_cost'].sum()
    total_performance = df['performance_score'].sum()
    
    if total_performance > 0:
        avg_cost_per_point = total_cost / total_performance
        df['expected_cost'] = df['performance_score'] * avg_cost_per_point
        df['value_over_expected'] = df['expected_cost'] - df['draft_cost']
        df['value_percentage'] = ((df['expected_cost'] - df['draft_cost']) / df['draft_cost'] * 100)
    else:
        df['expected_cost'] = df['draft_cost']
        df['value_over_expected'] = 0
        df['value_percentage'] = 0
    
    return df

def get_top_values(df, top_n=30):
    """Get top value players."""
    if df.empty:
        return df
    
    # Filter for meaningful costs and sort by value
    filtered = df[
        (df['draft_cost'] >= 3) &  # Minimum meaningful cost
        (df['games_played'] >= 30)  # Minimum games for reliability
    ].copy()
    
    return filtered.sort_values('value_over_expected', ascending=False).head(top_n)

def display_top_values(top_values, year):
    """Display top value players in a nice format."""
    if top_values.empty:
        print(f"No qualifying players found for {year}")
        return
    
    print(f"\\n{'='*100}")
    print(f"TOP {len(top_values)} VALUE PLAYERS - {year} SEASON")
    print(f"{'='*100}")
    print("Players who provided the most value relative to their draft cost")
    print("Value = What they should have cost based on performance - What they actually cost")
    print("-" * 100)
    
    for i, (_, player) in enumerate(top_values.iterrows(), 1):
        name = player['player_name'][:22]
        cost = player['draft_cost']
        expected = player['expected_cost']
        value_over = player['value_over_expected']
        value_pct = player['value_percentage']
        games = player['games_played']
        team = player['team']
        fantasy_team = player['fantasy_team'][:15]
        
        print(f"{i:2d}. {name:22} | "
              f"Cost: ${cost:2.0f} | "
              f"Worth: ${expected:3.0f} | "
              f"Value: +${value_over:2.0f} | "
              f"ROI: {value_pct:5.1f}% | "
              f"GP: {games:2.0f} | "
              f"{team:3} | "
              f"{fantasy_team:15}")

def analyze_value_patterns(df, year):
    """Analyze patterns in draft value."""
    if df.empty:
        return
    
    print(f"\\n{'='*80}")
    print(f"DRAFT VALUE PATTERNS - {year}")
    print(f"{'='*80}")
    
    # Overall stats
    total_spent = df['draft_cost'].sum()
    avg_value_per_dollar = df['value_per_dollar'].mean()
    
    print(f"\\nOVERALL DRAFT STATS:")
    print(f"Total players analyzed: {len(df)}")
    print(f"Total money spent: ${total_spent:,.0f}")
    print(f"Average value per dollar: {avg_value_per_dollar:.2f}")
    
    # Value by cost tiers
    print(f"\\nVALUE BY DRAFT COST TIERS:")
    
    tiers = [
        (40, 100, "Superstars"),
        (20, 39, "Stars"),
        (10, 19, "Solid Players"),
        (5, 9, "Role Players"),
        (1, 4, "Bargains")
    ]
    
    for min_cost, max_cost, tier_name in tiers:
        tier_data = df[
            (df['draft_cost'] >= min_cost) &
            (df['draft_cost'] <= max_cost)
        ]
        
        if not tier_data.empty:
            avg_vod = tier_data['value_per_dollar'].mean()
            avg_value_over = tier_data['value_over_expected'].mean()
            count = len(tier_data)
            
            print(f"  {tier_name:15} (${min_cost:2d}-${max_cost:2d}): "
                  f"{count:2d} players, "
                  f"Value/$ {avg_vod:5.2f}, "
                  f"Avg surplus: ${avg_value_over:5.1f}")
    
    # Best value categories
    print(f"\\nTOP VALUE STATS (Top 10 values):")
    top_10 = df.nlargest(10, 'value_over_expected')
    
    stats = [
        ('pts_pg', 'Points'),
        ('reb_pg', 'Rebounds'),
        ('ast_pg', 'Assists'),
        ('stl_pg', 'Steals'),
        ('blk_pg', 'Blocks'),
        ('threepm_pg', '3PM')
    ]
    
    for stat_col, stat_name in stats:
        avg_stat = top_10[stat_col].mean()
        print(f"  {stat_name:8}: {avg_stat:5.1f}")

def find_worst_values(df, bottom_n=15):
    """Find worst value players."""
    if df.empty:
        return df
    
    filtered = df[
        (df['draft_cost'] >= 5) &  # Only meaningful costs
        (df['games_played'] >= 15)  # Allow for some injury cases
    ].copy()
    
    return filtered.sort_values('value_over_expected', ascending=True).head(bottom_n)

def display_worst_values(worst_values, year):
    """Display worst value players."""
    if worst_values.empty:
        return
    
    print(f"\\n{'='*80}")
    print(f"WORST {len(worst_values)} VALUES - {year} SEASON")
    print(f"{'='*80}")
    print("Players who underperformed relative to their draft cost")
    print("-" * 80)
    
    for i, (_, player) in enumerate(worst_values.iterrows(), 1):
        name = player['player_name'][:22]
        cost = player['draft_cost']
        expected = player['expected_cost']
        value_over = player['value_over_expected']
        value_pct = player['value_percentage']
        games = player['games_played']
        team = player['team']
        
        print(f"{i:2d}. {name:22} | "
              f"Cost: ${cost:2.0f} | "
              f"Worth: ${expected:3.0f} | "
              f"Loss: ${value_over:3.0f} | "
              f"ROI: {value_pct:5.1f}% | "
              f"GP: {games:2.0f} | "
              f"{team:3}")

def main():
    """Run comprehensive draft value analysis."""
    # Load data
    players = load_player_data()
    
    # Analyze multiple years
    years = [2024, 2023, 2022, 2021]
    
    for year in years:
        print(f"\\n{'='*100}")
        print(f"ANALYZING {year} DRAFT VALUES")
        print(f"{'='*100}")
        
        # Get draft data for the year
        df = analyze_value_by_year(players, year)
        
        if df.empty:
            print(f"No draft data found for {year}")
            continue
        
        # Calculate expected costs and value metrics
        df = calculate_expected_cost(df)
        
        # Show results
        top_values = get_top_values(df, top_n=30)
        display_top_values(top_values, year)
        
        worst_values = find_worst_values(df, bottom_n=10)
        display_worst_values(worst_values, year)
        
        # Analyze patterns
        analyze_value_patterns(df, year)
        
        # Save detailed results for 2024
        if year == 2024:
            top_values.to_csv('top_30_values_2024.csv', index=False)
            print(f"\\nDetailed 2024 results saved to: top_30_values_2024.csv")

if __name__ == "__main__":
    main()