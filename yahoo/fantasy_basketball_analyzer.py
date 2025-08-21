#!/usr/bin/env python3
"""
Fantasy Basketball Analyzer for Yahoo 9-Category Head-to-Head League

This tool analyzes player performance across 9 fantasy categories:
- Points, Rebounds, Assists, Steals, Blocks, 3PM, FG%, FT%, Turnovers (negative)

Features:
- Category impact profiling
- Player comparison analysis
- Head-to-head simulation
- Draft value assessment
- Visualization tools
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os
from pathlib import Path
import json

warnings.filterwarnings('ignore')

class FantasyBasketballAnalyzer:
    def __init__(self, data_path="historical_nba_stats"):
        """Initialize analyzer with historical NBA stats."""
        self.data_path = Path(data_path)
        self.categories = [
            'points_per_game', 'rebounds_per_game', 'assists_per_game',
            'steals_per_game', 'blocks_per_game', 'threepointers_per_game',
            'field_goal_percentage', 'free_throw_percentage', 'turnovers_per_game'
        ]
        self.category_names = {
            'points_per_game': 'Points',
            'rebounds_per_game': 'Rebounds', 
            'assists_per_game': 'Assists',
            'steals_per_game': 'Steals',
            'blocks_per_game': 'Blocks',
            'threepointers_per_game': '3PM',
            'field_goal_percentage': 'FG%',
            'free_throw_percentage': 'FT%',
            'turnovers_per_game': 'Turnovers'
        }
        self.data = None
        self.normalized_data = None
        
    def load_data(self, min_games=20):
        """Load and combine all years of fantasy-relevant stats."""
        print("Loading historical NBA stats...")
        
        all_data = []
        years_loaded = 0
        
        for year_dir in sorted(self.data_path.glob("[0-9]*")):
            if year_dir.is_dir():
                stats_file = year_dir / "fantasy_relevant_stats.csv"
                if stats_file.exists():
                    try:
                        year_data = pd.read_csv(stats_file)
                        year_data['season'] = int(year_dir.name)
                        all_data.append(year_data)
                        years_loaded += 1
                    except Exception as e:
                        print(f"Error loading {year_dir.name}: {e}")
        
        if not all_data:
            raise ValueError("No data files found!")
        
        # Combine all years
        self.data = pd.concat(all_data, ignore_index=True)
        
        # Filter for minimum games played
        self.data = self.data[self.data['games_played'] >= min_games].copy()
        
        # Clean data
        self.data = self.data.dropna(subset=self.categories)
        
        print(f"Loaded {years_loaded} years of data")
        print(f"Total player-seasons: {len(self.data):,}")
        print(f"Unique players: {self.data['personName'].nunique():,}")
        print(f"Years: {self.data['season'].min()}-{self.data['season'].max()}")
        
        return self.data
    
    def normalize_stats(self, method='percentile'):
        """Normalize stats for cross-category comparison."""
        if self.data is None:
            raise ValueError("Must load data first!")
        
        print(f"Normalizing stats using {method} method...")
        
        normalized_df = self.data.copy()
        
        # Group by season for year-relative normalization
        for season in normalized_df['season'].unique():
            season_mask = normalized_df['season'] == season
            season_data = normalized_df[season_mask]
            
            for cat in self.categories:
                if method == 'percentile':
                    # Convert to percentile rank (0-100)
                    if cat == 'turnovers_per_game':
                        # For turnovers, lower is better, so invert
                        normalized_df.loc[season_mask, f'{cat}_norm'] = (
                            100 - stats.rankdata(season_data[cat], method='average') / len(season_data) * 100
                        )
                    else:
                        # Higher is better for all other stats
                        normalized_df.loc[season_mask, f'{cat}_norm'] = (
                            stats.rankdata(season_data[cat], method='average') / len(season_data) * 100
                        )
                        
                elif method == 'zscore':
                    # Z-score normalization
                    mean_val = season_data[cat].mean()
                    std_val = season_data[cat].std()
                    
                    if cat == 'turnovers_per_game':
                        # Invert z-score for turnovers
                        normalized_df.loc[season_mask, f'{cat}_norm'] = -(season_data[cat] - mean_val) / std_val
                    else:
                        normalized_df.loc[season_mask, f'{cat}_norm'] = (season_data[cat] - mean_val) / std_val
        
        self.normalized_data = normalized_df
        
        # Create category impact profile
        self.create_category_impact_profile()
        
        return self.normalized_data
    
    def create_category_impact_profile(self):
        """Create each player's category impact profile."""
        if self.normalized_data is None:
            raise ValueError("Must normalize data first!")
        
        # Calculate overall fantasy value (sum of normalized categories)
        norm_cats = [f'{cat}_norm' for cat in self.categories]
        self.normalized_data['fantasy_value'] = self.normalized_data[norm_cats].sum(axis=1)
        
        # Calculate category strengths/weaknesses
        for cat in self.categories:
            norm_cat = f'{cat}_norm'
            # Category strength relative to player's overall value
            self.normalized_data[f'{cat}_strength'] = (
                self.normalized_data[norm_cat] / self.normalized_data['fantasy_value'] * 100
            )
    
    def get_player_profile(self, player_name, season=None):
        """Get detailed category profile for a specific player."""
        if self.normalized_data is None:
            raise ValueError("Must normalize data first!")
        
        # Filter for player
        player_data = self.normalized_data[
            self.normalized_data['personName'].str.contains(player_name, case=False)
        ]
        
        if season:
            player_data = player_data[player_data['season'] == season]
        
        if player_data.empty:
            print(f"No data found for player: {player_name}")
            return None
        
        # Get most recent season if multiple
        if len(player_data) > 1 and season is None:
            player_data = player_data[player_data['season'] == player_data['season'].max()]
        
        player_row = player_data.iloc[0]
        
        profile = {
            'name': player_row['personName'],
            'season': player_row['season'],
            'team': player_row['teamTricode'],
            'games': player_row['games_played'],
            'fantasy_value': player_row['fantasy_value'],
            'raw_stats': {},
            'percentiles': {},
            'strengths': {},
            'category_ranks': {}
        }
        
        # Add stats for each category
        for cat in self.categories:
            cat_name = self.category_names[cat]
            profile['raw_stats'][cat_name] = player_row[cat]
            profile['percentiles'][cat_name] = player_row[f'{cat}_norm']
            profile['strengths'][cat_name] = player_row[f'{cat}_strength']
        
        return profile
    
    def compare_players(self, player_names, season=None):
        """Compare multiple players across all categories."""
        profiles = []
        for name in player_names:
            profile = self.get_player_profile(name, season)
            if profile:
                profiles.append(profile)
        
        if not profiles:
            print("No valid players found for comparison")
            return None
        
        # Create comparison DataFrame
        comparison_data = []
        for profile in profiles:
            row = {'Player': profile['name'], 'Season': profile['season']}
            row.update(profile['percentiles'])
            comparison_data.append(row)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        return comparison_df
    
    def simulate_head_to_head(self, team1_players, team2_players, season=None):
        """Simulate head-to-head matchup between two teams."""
        
        def get_team_totals(players):
            team_totals = {}
            valid_players = 0
            
            for player in players:
                profile = self.get_player_profile(player, season)
                if profile:
                    valid_players += 1
                    for cat_name, percentile in profile['percentiles'].items():
                        if cat_name not in team_totals:
                            team_totals[cat_name] = 0
                        team_totals[cat_name] += percentile
            
            return team_totals, valid_players
        
        team1_totals, team1_count = get_team_totals(team1_players)
        team2_totals, team2_count = get_team_totals(team2_players)
        
        if not team1_totals or not team2_totals:
            print("Error: Could not find stats for one or both teams")
            return None
        
        # Compare categories
        results = {}
        team1_wins = 0
        team2_wins = 0
        
        print(f"\\nHEAD-TO-HEAD SIMULATION")
        print(f"Team 1: {', '.join(team1_players)} ({team1_count} players)")
        print(f"Team 2: {', '.join(team2_players)} ({team2_count} players)")
        print("-" * 60)
        
        for cat_name in self.category_names.values():
            if cat_name in team1_totals and cat_name in team2_totals:
                team1_val = team1_totals[cat_name]
                team2_val = team2_totals[cat_name]
                
                if team1_val > team2_val:
                    winner = "Team 1"
                    team1_wins += 1
                elif team2_val > team1_val:
                    winner = "Team 2"
                    team2_wins += 1
                else:
                    winner = "Tie"
                
                results[cat_name] = {
                    'team1': team1_val,
                    'team2': team2_val,
                    'winner': winner
                }
                
                print(f"{cat_name:12} | Team1: {team1_val:6.1f} | Team2: {team2_val:6.1f} | Winner: {winner}")
        
        print("-" * 60)
        print(f"FINAL RESULT: Team 1: {team1_wins} | Team 2: {team2_wins}")
        
        if team1_wins > team2_wins:
            print("*** Team 1 WINS! ***")
        elif team2_wins > team1_wins:
            print("*** Team 2 WINS! ***")
        else:
            print("*** TIE GAME! ***")
        
        return results
    
    def find_category_specialists(self, category, season=None, top_n=20):
        """Find the best players in a specific category."""
        if self.normalized_data is None:
            raise ValueError("Must normalize data first!")
        
        data = self.normalized_data.copy()
        if season:
            data = data[data['season'] == season]
        
        # Find the category column
        cat_col = None
        for cat in self.categories:
            if self.category_names[cat].lower() == category.lower():
                cat_col = f'{cat}_norm'
                break
        
        if cat_col is None:
            print(f"Category '{category}' not found. Available: {list(self.category_names.values())}")
            return None
        
        # Get top players
        top_players = data.nlargest(top_n, cat_col)[
            ['personName', 'season', 'teamTricode', self.categories[self.categories.index(cat_col.replace('_norm', ''))], cat_col]
        ].copy()
        
        top_players.columns = ['Player', 'Season', 'Team', f'{category} (Raw)', f'{category} (Percentile)']
        
        return top_players
    
    def analyze_category_scarcity(self, season=None):
        """Analyze which categories are most scarce/valuable."""
        if self.normalized_data is None:
            raise ValueError("Must normalize data first!")
        
        data = self.normalized_data.copy()
        if season:
            data = data[data['season'] == season]
        
        scarcity_analysis = {}
        
        print(f"\\nCATEGORY SCARCITY ANALYSIS{' - ' + str(season) if season else ' - ALL YEARS'}")
        print("=" * 60)
        
        for cat in self.categories:
            cat_name = self.category_names[cat]
            norm_col = f'{cat}_norm'
            
            # Calculate various scarcity metrics
            std_dev = data[norm_col].std()
            top_10_pct = data[norm_col].quantile(0.9)
            top_5_pct = data[norm_col].quantile(0.95)
            elite_gap = top_5_pct - top_10_pct
            
            scarcity_analysis[cat_name] = {
                'std_dev': std_dev,
                'top_10_pct': top_10_pct,
                'top_5_pct': top_5_pct,
                'elite_gap': elite_gap,
                'scarcity_score': std_dev * elite_gap  # Combined metric
            }
            
            print(f"{cat_name:12} | Std: {std_dev:5.1f} | 90th: {top_10_pct:5.1f} | 95th: {top_5_pct:5.1f} | Gap: {elite_gap:5.1f}")
        
        # Rank by scarcity
        sorted_categories = sorted(scarcity_analysis.items(), key=lambda x: x[1]['scarcity_score'], reverse=True)
        
        print("\\n" + "=" * 60)
        print("CATEGORIES RANKED BY SCARCITY (most scarce first):")
        for i, (cat_name, metrics) in enumerate(sorted_categories, 1):
            print(f"{i:2d}. {cat_name:12} (Scarcity Score: {metrics['scarcity_score']:6.1f})")
        
        return scarcity_analysis
    
    def create_player_heatmap(self, player_names, season=None, save_path=None):
        """Create heatmap visualization of player category strengths."""
        comparison_df = self.compare_players(player_names, season)
        if comparison_df is None:
            return None
        
        # Prepare data for heatmap
        heatmap_data = comparison_df.set_index('Player')
        heatmap_data = heatmap_data.drop(['Season'], axis=1)
        
        # Create heatmap
        plt.figure(figsize=(12, 6))
        sns.heatmap(heatmap_data.T, annot=True, cmap='RdYlGn', center=50, 
                    fmt='.1f', cbar_kws={'label': 'Percentile Rank'})
        
        plt.title(f'Player Category Comparison{" - " + str(season) if season else ""}', 
                  fontsize=16, fontweight='bold')
        plt.xlabel('Players', fontweight='bold')
        plt.ylabel('Categories', fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return heatmap_data
    
    def create_radar_chart(self, player_name, season=None, save_path=None):
        """Create radar chart for individual player."""
        profile = self.get_player_profile(player_name, season)
        if profile is None:
            return None
        
        categories = list(profile['percentiles'].keys())
        values = list(profile['percentiles'].values())
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values, 'o-', linewidth=2, label=profile['name'])
        ax.fill(angles, values, alpha=0.25)
        
        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        
        # Add gridlines
        ax.grid(True)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20th', '40th', '60th', '80th', '100th'])
        
        plt.title(f'{profile["name"]} - {profile["season"]} Season\\nCategory Percentile Rankings', 
                  y=1.08, fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return profile
    
    def identify_undervalued_players(self, season, min_fantasy_value=400):
        """Identify potentially undervalued players for upcoming draft."""
        if self.normalized_data is None:
            raise ValueError("Must normalize data first!")
        
        season_data = self.normalized_data[self.normalized_data['season'] == season].copy()
        season_data = season_data[season_data['fantasy_value'] >= min_fantasy_value]
        
        print(f"\\nUNDERVALUED PLAYER ANALYSIS - {season} SEASON")
        print("=" * 60)
        
        # Calculate breakout candidates (players with high variance)
        analysis = []
        
        for _, player in season_data.iterrows():
            player_history = self.normalized_data[
                self.normalized_data['personName'] == player['personName']
            ].sort_values('season')
            
            if len(player_history) >= 2:
                # Calculate improvement trends
                recent_value = player['fantasy_value']
                
                # Category balance (not too dependent on one category)
                norm_cats = [f'{cat}_norm' for cat in self.categories]
                category_values = player[norm_cats].values
                balance_score = 1 - np.std(category_values) / np.mean(category_values)
                
                analysis.append({
                    'Player': player['personName'],
                    'Team': player['teamTricode'],
                    'Fantasy_Value': recent_value,
                    'Balance_Score': balance_score,
                    'Games_Played': player['games_played'],
                    'Age_Estimate': 2024 - season + 25,  # Rough estimate
                })
        
        analysis_df = pd.DataFrame(analysis)
        
        # Score players (balance good, high value, reasonable games)
        analysis_df['Undervalued_Score'] = (
            analysis_df['Fantasy_Value'] * 0.4 +
            analysis_df['Balance_Score'] * 100 * 0.3 +
            np.minimum(analysis_df['Games_Played'], 70) * 0.3
        )
        
        # Filter and sort
        candidates = analysis_df[
            (analysis_df['Games_Played'] >= 50) &
            (analysis_df['Balance_Score'] > 0.3)
        ].sort_values('Undervalued_Score', ascending=False).head(20)
        
        print("TOP UNDERVALUED CANDIDATES:")
        print(candidates[['Player', 'Team', 'Fantasy_Value', 'Balance_Score', 'Games_Played']].to_string(index=False))
        
        return candidates

def main():
    """Example usage of the Fantasy Basketball Analyzer."""
    
    # Initialize analyzer
    analyzer = FantasyBasketballAnalyzer()
    
    # Load data
    data = analyzer.load_data(min_games=30)
    
    # Normalize stats
    normalized_data = analyzer.normalize_stats(method='percentile')
    
    # Example analyses
    print("\\n" + "="*60)
    print("FANTASY BASKETBALL ANALYZER DEMO")
    print("="*60)
    
    # 1. Category scarcity analysis
    analyzer.analyze_category_scarcity(season=2024)
    
    # 2. Player profile example
    print("\\n" + "="*60)
    profile = analyzer.get_player_profile("LeBron James", season=2024)
    if profile:
        print(f"\\nPLAYER PROFILE: {profile['name']} ({profile['season']})")
        print(f"Team: {profile['team']} | Games: {profile['games']} | Fantasy Value: {profile['fantasy_value']:.1f}")
        print("\\nCategory Percentiles:")
        for cat, pct in profile['percentiles'].items():
            print(f"  {cat:12}: {pct:5.1f}th percentile")
    
    # 3. Compare players
    print("\\n" + "="*60)
    print("PLAYER COMPARISON:")
    comparison = analyzer.compare_players(["LeBron James", "Kevin Durant", "Stephen Curry"], season=2024)
    if comparison is not None:
        print(comparison.to_string(index=False))
    
    # 4. Head-to-head simulation
    analyzer.simulate_head_to_head(
        ["LeBron James", "Kevin Durant"], 
        ["Stephen Curry", "Giannis Antetokounmpo"], 
        season=2024
    )
    
    # 5. Find category specialists
    print("\\n" + "="*60)
    blocks_leaders = analyzer.find_category_specialists("Blocks", season=2024, top_n=10)
    if blocks_leaders is not None:
        print("\\nTOP SHOT BLOCKERS (2024):")
        print(blocks_leaders.to_string(index=False))
    
    # 6. Undervalued players
    undervalued = analyzer.identify_undervalued_players(2024)

if __name__ == "__main__":
    main()