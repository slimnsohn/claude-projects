#!/usr/bin/env python3
"""
Draft Value Analyzer

Analyzes which players provided the best value relative to their actual draft cost
in your Yahoo fantasy league using historical draft data and NBA performance.
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from fantasy_basketball_analyzer import FantasyBasketballAnalyzer

class DraftValueAnalyzer:
    def __init__(self):
        """Initialize the draft value analyzer."""
        self.fantasy_analyzer = FantasyBasketballAnalyzer()
        self.draft_data = None
        self.player_mappings = None
        self.value_analysis = None
        
    def load_yahoo_draft_data(self):
        """Load draft data from all years with auction drafts (2016-2024)."""
        print("Loading Yahoo draft data...")
        
        all_drafts = []
        auction_years = range(2016, 2025)  # 2016-2024 had auction drafts
        
        for year in auction_years:
            draft_file = f"league_data/{year}/raw_data/draft_results.json"
            if os.path.exists(draft_file):
                try:
                    with open(draft_file, 'r', encoding='utf-8') as f:
                        draft_data = json.load(f)
                    
                    # Extract draft results
                    for pick in draft_data:
                        if pick.get('draft_cost', 0) > 0:  # Only auction picks with cost
                            all_drafts.append({
                                'year': year,
                                'player_name': pick['player_name'],
                                'draft_cost': pick['draft_cost'],
                                'pick_number': pick.get('pick_number', 0),
                                'team_name': pick.get('team_name', 'Unknown')
                            })
                    
                    print(f"  Loaded {year}: {len([p for p in draft_data if p.get('draft_cost', 0) > 0])} auction picks")
                    
                except Exception as e:
                    print(f"  Error loading {year}: {e}")
        
        self.draft_data = pd.DataFrame(all_drafts)
        print(f"Total auction picks loaded: {len(self.draft_data):,}")
        
        return self.draft_data
    
    def load_player_mappings(self):
        """Load player name mappings between Yahoo and NBA data."""
        print("Loading player mappings...")
        
        mapping_files = [
            "historical_nba_stats/player_mappings/yahoo_nba_mapping.json",
            "historical_nba_stats/player_mappings/comprehensive_mapping.json",
            "html_reports/data/players.json"
        ]
        
        mappings = {}
        
        for mapping_file in mapping_files:
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'players' in data:  # players.json format
                        for player_id, player_data in data['players'].items():
                            yahoo_name = player_data.get('player_name', '')
                            if yahoo_name and 'nba_data' in player_data:
                                nba_name = player_data['nba_data'].get('player_name', '')
                                if nba_name:
                                    mappings[yahoo_name] = nba_name
                    else:  # direct mapping format
                        mappings.update(data)
                        
                except Exception as e:
                    print(f"  Error loading {mapping_file}: {e}")
        
        self.player_mappings = mappings
        print(f"Loaded {len(mappings)} player mappings")
        
        return mappings
    
    def analyze_draft_value(self, year=2024):
        """Analyze draft value for a specific year."""
        print(f"\\nAnalyzing draft value for {year}...")
        
        # Load fantasy analyzer data
        if self.fantasy_analyzer.data is None:
            self.fantasy_analyzer.load_data(min_games=20)
            self.fantasy_analyzer.normalize_stats()
        
        # Get draft data for the year
        year_drafts = self.draft_data[self.draft_data['year'] == year].copy()
        
        if year_drafts.empty:
            print(f"No draft data found for {year}")
            return None
        
        print(f"Analyzing {len(year_drafts)} drafted players from {year}")
        
        # Get fantasy performance data for the year
        fantasy_data = self.fantasy_analyzer.normalized_data[
            self.fantasy_analyzer.normalized_data['season'] == year
        ].copy()
        
        # Merge draft costs with fantasy performance
        value_analysis = []
        
        for _, draft_pick in year_drafts.iterrows():
            yahoo_name = draft_pick['player_name']
            draft_cost = draft_pick['draft_cost']
            
            # Try to find matching NBA player
            nba_name = self.find_nba_name(yahoo_name)
            
            if nba_name:
                # Find fantasy performance
                player_performance = fantasy_data[
                    fantasy_data['personName'].str.contains(nba_name, case=False, na=False)
                ]
                
                if not player_performance.empty:
                    perf = player_performance.iloc[0]
                    
                    # Calculate value metrics
                    fantasy_value = perf['fantasy_value']
                    value_per_dollar = fantasy_value / draft_cost if draft_cost > 0 else 0
                    
                    # Calculate expected cost based on performance
                    # Use league average cost per fantasy point
                    avg_cost_per_point = year_drafts['draft_cost'].sum() / fantasy_data['fantasy_value'].sum()
                    expected_cost = fantasy_value * avg_cost_per_point
                    
                    value_over_expected = expected_cost - draft_cost
                    value_percentage = ((expected_cost - draft_cost) / draft_cost * 100) if draft_cost > 0 else 0
                    
                    value_analysis.append({
                        'player_name': yahoo_name,
                        'nba_name': nba_name,
                        'draft_cost': draft_cost,
                        'fantasy_value': fantasy_value,
                        'value_per_dollar': value_per_dollar,
                        'expected_cost': expected_cost,
                        'value_over_expected': value_over_expected,
                        'value_percentage': value_percentage,
                        'games_played': perf['games_played'],
                        'team': perf['teamTricode'],
                        # Category percentiles
                        'points_pct': perf['points_per_game_norm'],
                        'rebounds_pct': perf['rebounds_per_game_norm'],
                        'assists_pct': perf['assists_per_game_norm'],
                        'steals_pct': perf['steals_per_game_norm'],
                        'blocks_pct': perf['blocks_per_game_norm'],
                        'threepm_pct': perf['threepointers_per_game_norm'],
                        'fg_pct': perf['field_goal_percentage_norm'],
                        'ft_pct': perf['free_throw_percentage_norm'],
                        'to_pct': perf['turnovers_per_game_norm']
                    })
        
        self.value_analysis = pd.DataFrame(value_analysis)
        
        print(f"Successfully analyzed {len(self.value_analysis)} players")
        
        return self.value_analysis
    
    def find_nba_name(self, yahoo_name):
        """Find NBA name for a Yahoo player name."""
        # Direct mapping
        if yahoo_name in self.player_mappings:
            return self.player_mappings[yahoo_name]
        
        # Try fuzzy matching
        yahoo_lower = yahoo_name.lower()
        
        # Common name variations
        name_variations = [
            yahoo_name,
            yahoo_name.replace(".", ""),
            yahoo_name.replace("Jr.", "").strip(),
            yahoo_name.replace("III", "").strip(),
            yahoo_name.replace("II", "").strip()
        ]
        
        for variation in name_variations:
            if variation in self.player_mappings:
                return self.player_mappings[variation]
        
        # Check if any NBA name contains the Yahoo name
        for yahoo_mapped, nba_name in self.player_mappings.items():
            if yahoo_lower in nba_name.lower() or nba_name.lower() in yahoo_lower:
                return nba_name
        
        return yahoo_name  # Return original if no mapping found
    
    def get_top_values(self, year=2024, top_n=30, min_cost=5):
        """Get top value players who outperformed their draft cost."""
        if self.value_analysis is None:
            self.analyze_draft_value(year)
        
        # Filter for meaningful draft costs and sort by value
        top_values = self.value_analysis[
            (self.value_analysis['draft_cost'] >= min_cost) &
            (self.value_analysis['games_played'] >= 30)  # Minimum games to avoid fluke performances
        ].sort_values('value_over_expected', ascending=False).head(top_n)
        
        return top_values
    
    def get_worst_values(self, year=2024, bottom_n=20, min_cost=10):
        """Get worst value players who underperformed their draft cost."""
        if self.value_analysis is None:
            self.analyze_draft_value(year)
        
        # Filter for meaningful draft costs and sort by worst value
        worst_values = self.value_analysis[
            (self.value_analysis['draft_cost'] >= min_cost) &
            (self.value_analysis['games_played'] >= 10)  # Allow injured players
        ].sort_values('value_over_expected', ascending=True).head(bottom_n)
        
        return worst_values
    
    def analyze_draft_patterns(self, year=2024):
        """Analyze draft patterns and value trends."""
        if self.value_analysis is None:
            self.analyze_draft_value(year)
        
        print(f"\\n{'='*70}")
        print(f"DRAFT VALUE ANALYSIS - {year} SEASON")
        print(f"{'='*70}")
        
        # Overall statistics
        total_spent = self.value_analysis['draft_cost'].sum()
        total_value = self.value_analysis['fantasy_value'].sum()
        avg_value_per_dollar = self.value_analysis['value_per_dollar'].mean()
        
        print(f"\\nOVERALL DRAFT EFFICIENCY:")
        print(f"Total spent: ${total_spent:,.0f}")
        print(f"Total fantasy value generated: {total_value:,.1f}")
        print(f"Average value per dollar: {avg_value_per_dollar:.2f}")
        
        # Value by draft cost tiers
        print(f"\\nVALUE BY DRAFT COST TIERS:")
        
        # Define cost tiers
        tiers = [
            (50, 200, "Superstars"),
            (25, 49, "Stars"), 
            (15, 24, "Solid Players"),
            (8, 14, "Role Players"),
            (1, 7, "Bargains")
        ]
        
        for min_cost, max_cost, tier_name in tiers:
            tier_data = self.value_analysis[
                (self.value_analysis['draft_cost'] >= min_cost) &
                (self.value_analysis['draft_cost'] <= max_cost)
            ]
            
            if not tier_data.empty:
                avg_value_per_dollar = tier_data['value_per_dollar'].mean()
                avg_value_over_expected = tier_data['value_over_expected'].mean()
                count = len(tier_data)
                
                print(f"  {tier_name:15} (${min_cost:2d}-${max_cost:2d}): "
                      f"{count:2d} players, "
                      f"Avg value/$ {avg_value_per_dollar:5.2f}, "
                      f"Avg over expected: ${avg_value_over_expected:6.1f}")
        
        # Category analysis
        print(f"\\nBEST VALUE CATEGORIES (avg percentile of top 10 values):")
        top_10_values = self.value_analysis.nlargest(10, 'value_over_expected')
        
        categories = [
            ('points_pct', 'Points'),
            ('rebounds_pct', 'Rebounds'),
            ('assists_pct', 'Assists'), 
            ('steals_pct', 'Steals'),
            ('blocks_pct', 'Blocks'),
            ('threepm_pct', '3PM'),
            ('fg_pct', 'FG%'),
            ('ft_pct', 'FT%'),
            ('to_pct', 'Turnovers')
        ]
        
        category_avgs = []
        for cat_col, cat_name in categories:
            avg_pct = top_10_values[cat_col].mean()
            category_avgs.append((cat_name, avg_pct))
        
        category_avgs.sort(key=lambda x: x[1], reverse=True)
        
        for cat_name, avg_pct in category_avgs:
            print(f"  {cat_name:10}: {avg_pct:5.1f}th percentile")
        
        return self.value_analysis
    
    def create_value_report(self, year=2024, save_to_file=True):
        """Create comprehensive value report."""
        print(f"\\n{'='*80}")
        print(f"TOP 30 VALUE PLAYERS - {year} SEASON")
        print(f"{'='*80}")
        
        # Get top values
        top_values = self.get_top_values(year, top_n=30)
        
        if top_values.empty:
            print("No value data available")
            return None
        
        print(f"\\nRANKING: Players who outperformed their draft cost the most")
        print(f"Value Over Expected = What they should have cost - What they actually cost")
        print(f"Value % = Percentage return on investment")
        print("-" * 110)
        
        # Display results
        for i, (_, player) in enumerate(top_values.iterrows(), 1):
            name = player['player_name'][:20]  # Truncate long names
            cost = player['draft_cost']
            expected = player['expected_cost']
            value_over = player['value_over_expected']
            value_pct = player['value_percentage']
            games = player['games_played']
            fantasy_val = player['fantasy_value']
            
            print(f"{i:2d}. {name:20} | "
                  f"Cost: ${cost:3.0f} | "
                  f"Should be: ${expected:3.0f} | "
                  f"Value: +${value_over:3.0f} | "
                  f"ROI: {value_pct:5.1f}% | "
                  f"Games: {games:2.0f} | "
                  f"Fantasy Value: {fantasy_val:5.1f}")
        
        # Show category strengths of top values
        print(f"\\n{'='*80}")
        print("CATEGORY ANALYSIS OF TOP 10 VALUE PLAYERS")
        print(f"{'='*80}")
        
        top_10 = top_values.head(10)
        
        print("\\nAverage category percentiles:")
        cat_analysis = [
            ('points_pct', 'Points'),
            ('rebounds_pct', 'Rebounds'), 
            ('assists_pct', 'Assists'),
            ('steals_pct', 'Steals'),
            ('blocks_pct', 'Blocks'),
            ('threepm_pct', '3PM'),
            ('fg_pct', 'FG%'),
            ('ft_pct', 'FT%'),
            ('to_pct', 'Turnovers')
        ]
        
        for cat_col, cat_name in cat_analysis:
            avg_pct = top_10[cat_col].mean()
            if avg_pct >= 80:
                grade = "ELITE"
            elif avg_pct >= 70:
                grade = "VERY GOOD"
            elif avg_pct >= 60:
                grade = "GOOD"
            elif avg_pct >= 50:
                grade = "AVERAGE"
            else:
                grade = "BELOW AVG"
                
            print(f"  {cat_name:10}: {avg_pct:5.1f}th percentile ({grade})")
        
        # Save to file if requested
        if save_to_file:
            filename = f"value_analysis_{year}.csv"
            top_values.to_csv(filename, index=False)
            print(f"\\nFull analysis saved to: {filename}")
        
        return top_values

def main():
    """Run comprehensive draft value analysis."""
    analyzer = DraftValueAnalyzer()
    
    # Load data
    analyzer.load_yahoo_draft_data()
    analyzer.load_player_mappings()
    
    # Analyze recent years
    for year in [2024, 2023, 2022]:
        print(f"\\n{'='*100}")
        print(f"ANALYZING {year} DRAFT VALUE")
        print(f"{'='*100}")
        
        try:
            # Run analysis
            analyzer.analyze_draft_value(year)
            analyzer.analyze_draft_patterns(year)
            
            # Get top and worst values
            print(f"\\nTOP 15 VALUES - {year}:")
            top_values = analyzer.get_top_values(year, top_n=15)
            
            for i, (_, player) in enumerate(top_values.iterrows(), 1):
                print(f"{i:2d}. {player['player_name']:25} | "
                      f"Cost: ${player['draft_cost']:2.0f} | "
                      f"Value: +${player['value_over_expected']:3.0f} | "
                      f"ROI: {player['value_percentage']:5.1f}%")
            
            print(f"\\nWORST 10 VALUES - {year}:")
            worst_values = analyzer.get_worst_values(year, bottom_n=10)
            
            for i, (_, player) in enumerate(worst_values.iterrows(), 1):
                print(f"{i:2d}. {player['player_name']:25} | "
                      f"Cost: ${player['draft_cost']:2.0f} | "
                      f"Value: ${player['value_over_expected']:4.0f} | "
                      f"Loss: {abs(player['value_percentage']):5.1f}%")
                      
        except Exception as e:
            print(f"Error analyzing {year}: {e}")
    
    # Create detailed report for most recent year
    print(f"\\n{'='*100}")
    print("CREATING DETAILED 2024 VALUE REPORT")
    print(f"{'='*100}")
    
    analyzer.create_value_report(2024, save_to_file=True)

if __name__ == "__main__":
    main()