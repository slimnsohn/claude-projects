# 🏀 Fantasy Basketball Analysis Toolkit

## Overview
This toolkit analyzes 15 years of NBA stats to help you dominate your Yahoo 9-category head-to-head fantasy league. The 9 categories are:

**Counting Stats**: Points, Rebounds, Assists, Steals, Blocks, 3PM  
**Percentages**: FG%, FT%  
**Negative**: Turnovers (lower is better)

## 🚀 Quick Start

### 1. Basic Player Analysis
```python
# Load the analyzer
from fantasy_basketball_analyzer import FantasyBasketballAnalyzer

analyzer = FantasyBasketballAnalyzer()
analyzer.load_data()
analyzer.normalize_stats()

# Analyze any player
profile = analyzer.get_player_profile("Victor Wembanyama", season=2024)
```

### 2. Interactive Analysis
```bash
# Run the interactive analyzer for easy exploration
python interactive_fantasy_analyzer.py
```

### 3. Complete Draft Prep
```bash
# Run comprehensive draft preparation
python fantasy_analysis_guide.py
```

## 📊 Key Analysis Features

### Category Scarcity Analysis
**Why it matters**: Some categories are much rarer than others. Elite players in scarce categories provide huge competitive advantages.

```python
# Find which categories are most scarce
analyzer.analyze_category_scarcity(season=2024)
```

**Typical Scarcity Ranking**:
1. **Blocks** - Very few elite shot blockers
2. **Steals** - Hard to predict and find consistently  
3. **FT%** - Many high-volume scorers shoot poorly
4. **3PM** - Specialists vs. non-shooters
5. **FG%** - Efficiency varies widely

### Player Category Profiles
Every player gets percentile rankings (0-100th) in each category relative to all NBA players.

**Elite (90th+ percentile)**: Massive competitive advantage  
**Very Good (75-89th)**: Strong contributor  
**Good (60-74th)**: Solid contributor  
**Average (40-59th)**: Neutral impact  
**Below Average (<40th)**: Potential liability  

### Balance Score
Measures how well-rounded a player is across all categories:
- **0.5+**: Extremely balanced (rare)
- **0.4-0.5**: Well-balanced  
- **0.3-0.4**: Some weaknesses but manageable
- **<0.3**: Specialist with major holes

## 🎯 Draft Strategies

### Strategy 1: Balanced Build
- Target players with high balance scores (0.35+)
- Avoid major weaknesses in any category
- Safer floor, consistent weekly performance
- **Best for**: New players, competitive leagues

### Strategy 2: Category Punting  
- Intentionally ignore 1-2 categories (usually FT% and TO)
- Draft players who excel everywhere except punted cats
- Dominate 7 categories, concede 2
- **Best for**: Experienced players, less competitive leagues

### Strategy 3: Scarcity Focus
- Prioritize elite players in scarce categories
- Build around 1-2 category specialists
- Fill out roster with balanced contributors
- **Best for**: Leagues where few people understand scarcity

## 💎 How to Spot Undervalued Players

### The Perfect Undervalued Profile:
1. **High Balance Score (0.4+)**
   - Won't hurt you in any category
   - Consistent weekly value

2. **Elite in 1+ Scarce Categories**
   - Top 20 in Blocks/Steals/3PM
   - Provides weekly competitive edge

3. **60+ Games Played Consistently**
   - Availability is the best ability
   - Avoids injury-prone players

4. **Age 23-28 (Prime Years)**
   - Entering or in peak performance
   - Less injury risk than veterans

5. **Positive Team Context**
   - Increased role/minutes
   - Less competition for stats
   - Better supporting cast

### Red Flags to Avoid:
- **Major Category Weakness**: <20th percentile in important cats
- **Injury History**: <50 games in multiple seasons  
- **One-Category Dependence**: >50% of value from one category
- **Age Concerns**: 30+ with declining usage
- **Bad Team Fit**: Reduced role, crowded position

## 🏆 Advanced Techniques

### Head-to-Head Simulation
Test different roster combinations to see who wins more categories:

```python
# Simulate your team vs opponent
analyzer.simulate_head_to_head(
    ["LeBron James", "Anthony Davis"],
    ["Giannis Antetokounmpo", "Damian Lillard"], 
    season=2024
)
```

### Multi-Year Trending
Track player development and consistency:

```python
# See player improvement over time
for year in [2022, 2023, 2024]:
    profile = analyzer.get_player_profile("Anthony Edwards", season=year)
    print(f"{year}: Fantasy Value = {profile['fantasy_value']}")
```

### Category Correlation Analysis
Understand which categories tend to go together:
- **High Correlation**: Points & 3PM (scorers shoot threes)
- **Negative Correlation**: FG% & 3PM (volume vs efficiency)
- **Independent**: Blocks & most other categories

## 📈 Weekly Matchup Strategy

### Before Each Week:
1. **Check Opponent's Strengths**: What categories do they usually win?
2. **Identify Winnable Categories**: Where do you have advantages?
3. **Plan Streaming**: Add/drop players for specific categories
4. **Avoid Punting**: Don't give up categories you can win

### During the Week:
1. **Monitor Close Categories**: Add players to push you over the edge
2. **Secure Wins**: Don't risk safe categories for unlikely ones
3. **Percentage Management**: Sit poor shooters if FG%/FT% are close

## 🎲 Example Analysis

### Victor Wembanyama (2024):
- **Elite Categories**: Blocks (99th percentile), Rebounds (85th)
- **Strong Categories**: Points (78th), FG% (72nd)
- **Weak Categories**: FT% (45th), Turnovers (25th)
- **Strategy**: Build around his elite shot-blocking, pair with good FT% players

### Luka Doncic (2024):
- **Elite Categories**: Points (98th), Assists (95th), Rebounds (88th)  
- **Strong Categories**: 3PM (82nd)
- **Weak Categories**: FG% (35th), FT% (68th), Turnovers (15th)
- **Strategy**: Accept poor percentages/TOs, dominate counting stats

## 🔍 Tools Summary

| Tool | Purpose | Best For |
|------|---------|----------|
| `fantasy_basketball_analyzer.py` | Core analysis engine | Custom analysis |
| `interactive_fantasy_analyzer.py` | Easy player lookup | Quick comparisons |  
| `fantasy_analysis_guide.py` | Draft preparation | Pre-season prep |

## 💡 Key Takeaways

1. **Scarcity Matters Most**: Elite players in rare categories (Blocks, Steals) provide disproportionate value

2. **Balance vs. Specialization**: Decide between safe balanced players or risky specialists

3. **Games Played**: 60+ games is crucial - availability beats upside

4. **Know Your League**: Adjust strategy based on opponent sophistication

5. **Use Data**: Don't rely on "big names" - analyze actual statistical production

6. **Plan Ahead**: Understand your roster's strengths/weaknesses for trades and waiver adds

## 🏅 Advanced Pro Tips

- **Late-Round Targets**: Look for players with 50+ games, 0.3+ balance score
- **Trade Strategy**: Package complementary players, target scarce categories
- **Streaming**: Focus on games played and specific category needs
- **Playoff Prep**: Prioritize players on teams likely to rest stars
- **Injury Replacements**: Have a watchlist of players who could get minutes

This toolkit gives you a massive informational advantage. Use it wisely! 🏆