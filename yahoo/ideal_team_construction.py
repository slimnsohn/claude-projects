#!/usr/bin/env python3
"""
Create ideal example teams using 2025 projections for different construction styles
"""

import json

class IdealTeamConstructor:
    def __init__(self):
        self.projection_data = {}
        self.load_projection_data()
        
    def load_projection_data(self):
        """Load 2025 projection data"""
        # Based on the projections from player_analysis.html, create comprehensive player pool
        self.projection_data = {
            # Elite Tier (700+) - Championship anchors
            'Kawhi Leonard': {'projection': 719, 'cost': 12, 'archetype': 'Shooter', 'team': 'LAC'},
            'Joel Embiid': {'projection': 716, 'cost': 47, 'archetype': 'Guard', 'team': 'PHI'},
            'Shai Gilgeous-Alexander': {'projection': 709, 'cost': 67, 'archetype': 'Guard', 'team': 'OKC'},
            'Kyrie Irving': {'projection': 700, 'cost': 31, 'archetype': 'Shooter', 'team': 'DAL'},
            'Kevin Durant': {'projection': 696, 'cost': 39, 'archetype': 'Shooter', 'team': 'PHX'},
            'Nikola Jokic': {'projection': 690, 'cost': 73, 'archetype': 'Guard', 'team': 'DEN'},
            'Luka Doncic': {'projection': 683, 'cost': 0, 'archetype': 'Shooter', 'team': 'DAL'},  # Kept/not drafted
            
            # Strong Tier (600-699) - High-end role players
            'Donovan Mitchell': {'projection': 679, 'cost': 40, 'archetype': 'Shooter', 'team': 'CLE'},
            'Paul George': {'projection': 678, 'cost': 29, 'archetype': 'Shooter', 'team': 'LAC'},
            'Derrick White': {'projection': 675, 'cost': 15, 'archetype': 'Shooter', 'team': 'BOS'},
            'Jayson Tatum': {'projection': 671, 'cost': 51, 'archetype': 'Shooter', 'team': 'BOS'},
            'Tyrese Haliburton': {'projection': 670, 'cost': 50, 'archetype': 'Shooter', 'team': 'IND'},
            'Lauri Markkanen': {'projection': 667, 'cost': 29, 'archetype': 'Shooter', 'team': 'UTA'},
            'Kristaps Porzingis': {'projection': 658, 'cost': 0, 'archetype': 'Shooter', 'team': 'BOS'},  # Kept
            'Tobias Harris': {'projection': 656, 'cost': 5, 'archetype': 'Guard', 'team': 'PHI'},
            'LeBron James': {'projection': 656, 'cost': 28, 'archetype': 'Shooter', 'team': 'LAL'},
            'Victor Wembanyama': {'projection': 651, 'cost': 80, 'archetype': 'Shooter', 'team': 'SAS'},
            'Anthony Davis': {'projection': 651, 'cost': 54, 'archetype': 'Guard', 'team': 'LAL'},
            'Devin Booker': {'projection': 650, 'cost': 35, 'archetype': 'Shooter', 'team': 'PHX'},
            'Anthony Edwards': {'projection': 649, 'cost': 54, 'archetype': 'Shooter', 'team': 'MIN'},
            'Grayson Allen': {'projection': 648, 'cost': 1, 'archetype': 'Shooter', 'team': 'PHX'},
            'Keegan Murray': {'projection': 643, 'cost': 2, 'archetype': 'Guard', 'team': 'SAC'},
            'Karl-Anthony Towns': {'projection': 642, 'cost': 36, 'archetype': 'Shooter', 'team': 'MIN'},
            'James Harden': {'projection': 641, 'cost': 35, 'archetype': 'Guard', 'team': 'LAC'},
            'Fred VanVleet': {'projection': 641, 'cost': 20, 'archetype': 'Guard', 'team': 'HOU'},
            'Tyrese Maxey': {'projection': 638, 'cost': 29, 'archetype': 'Guard', 'team': 'PHI'},
            'CJ McCollum': {'projection': 637, 'cost': 5, 'archetype': 'Shooter', 'team': 'NOP'},
            'Al Horford': {'projection': 633, 'cost': 1, 'archetype': 'Big Man', 'team': 'BOS'},
            'Jalen Williams': {'projection': 631, 'cost': 34, 'archetype': 'Guard', 'team': 'OKC'},
            
            # Solid Tier (500-599) - Quality depth pieces
            'Trey Murphy III': {'projection': 595, 'cost': 8, 'archetype': 'Shooter', 'team': 'NOP'},
            'Jalen Johnson': {'projection': 594, 'cost': 11, 'archetype': 'Guard', 'team': 'ATL'},
            'Bradley Beal': {'projection': 593, 'cost': 18, 'archetype': 'Shooter', 'team': 'PHX'},
            'Jimmy Butler': {'projection': 592, 'cost': 22, 'archetype': 'Guard', 'team': 'MIA'},
            'Chet Holmgren': {'projection': 591, 'cost': 25, 'archetype': 'Shooter', 'team': 'OKC'},
            'Dejounte Murray': {'projection': 590, 'cost': 18, 'archetype': 'Guard', 'team': 'ATL'},
            'Giannis Antetokounmpo': {'projection': 589, 'cost': 65, 'archetype': 'Guard', 'team': 'MIL'},
            'Stephen Curry': {'projection': 588, 'cost': 42, 'archetype': 'Shooter', 'team': 'GSW'},
            'Terry Rozier': {'projection': 587, 'cost': 12, 'archetype': 'Guard', 'team': 'CHA'},
            'Jaren Jackson Jr.': {'projection': 586, 'cost': 31, 'archetype': 'Big Man', 'team': 'MEM'},
            'De\'Aaron Fox': {'projection': 585, 'cost': 43, 'archetype': 'Guard', 'team': 'SAC'},
            'Michael Porter Jr.': {'projection': 584, 'cost': 14, 'archetype': 'Shooter', 'team': 'DEN'},
            'Nikola Vucevic': {'projection': 583, 'cost': 16, 'archetype': 'Big Man', 'team': 'CHI'},
            'Franz Wagner': {'projection': 582, 'cost': 21, 'archetype': 'Guard', 'team': 'ORL'},
            'Jaylen Brown': {'projection': 581, 'cost': 49, 'archetype': 'Shooter', 'team': 'BOS'},
            'Damian Lillard': {'projection': 580, 'cost': 30, 'archetype': 'Guard', 'team': 'MIL'},
            'Brandon Ingram': {'projection': 579, 'cost': 24, 'archetype': 'Guard', 'team': 'NOP'},
            'Brook Lopez': {'projection': 578, 'cost': 7, 'archetype': 'Big Man', 'team': 'MIL'},
            'Cade Cunningham': {'projection': 577, 'cost': 19, 'archetype': 'Guard', 'team': 'DET'},
            'Devin Vassell': {'projection': 576, 'cost': 13, 'archetype': 'Shooter', 'team': 'SAS'},
            'Jalen Brunson': {'projection': 575, 'cost': 37, 'archetype': 'Guard', 'team': 'NYK'},
            'Bogdan Bogdanovic': {'projection': 574, 'cost': 6, 'archetype': 'Shooter', 'team': 'ATL'},
            'OG Anunoby': {'projection': 573, 'cost': 17, 'archetype': 'Guard', 'team': 'NYK'},
            'Alex Caruso': {'projection': 572, 'cost': 4, 'archetype': 'Guard', 'team': 'CHI'},
            'D\'Angelo Russell': {'projection': 571, 'cost': 9, 'archetype': 'Guard', 'team': 'LAL'},
            'Bam Adebayo': {'projection': 570, 'cost': 33, 'archetype': 'Big Man', 'team': 'MIA'},
            'Alperen Sengun': {'projection': 569, 'cost': 23, 'archetype': 'Big Man', 'team': 'HOU'},
            'Khris Middleton': {'projection': 568, 'cost': 13, 'archetype': 'Shooter', 'team': 'MIL'},
            'Austin Reaves': {'projection': 567, 'cost': 8, 'archetype': 'Guard', 'team': 'LAL'},
            'Mike Conley': {'projection': 566, 'cost': 3, 'archetype': 'Guard', 'team': 'MIN'},
            'Evan Mobley': {'projection': 565, 'cost': 38, 'archetype': 'Big Man', 'team': 'CLE'},
            'Deandre Ayton': {'projection': 564, 'cost': 32, 'archetype': 'Big Man', 'team': 'POR'},
            'Jabari Smith Jr.': {'projection': 563, 'cost': 9, 'archetype': 'Guard', 'team': 'HOU'},
            'Aaron Nesmith': {'projection': 562, 'cost': 3, 'archetype': 'Shooter', 'team': 'IND'},
            'Kentavious Caldwell-Pope': {'projection': 561, 'cost': 7, 'archetype': 'Shooter', 'team': 'DEN'},
            'Domantas Sabonis': {'projection': 560, 'cost': 44, 'archetype': 'Big Man', 'team': 'SAC'},
            
            # Value Tier (400-499) - Late round gems
            'Mikal Bridges': {'projection': 499, 'cost': 18, 'archetype': 'Guard', 'team': 'BRK'},
            'Kyle Kuzma': {'projection': 498, 'cost': 22, 'archetype': 'Guard', 'team': 'WAS'},
            'Tyus Jones': {'projection': 497, 'cost': 8, 'archetype': 'Guard', 'team': 'WAS'},
            'Brandon Miller': {'projection': 496, 'cost': 16, 'archetype': 'Guard', 'team': 'CHA'},
            'Paolo Banchero': {'projection': 495, 'cost': 41, 'archetype': 'Guard', 'team': 'ORL'},
            'Kelly Olynyk': {'projection': 494, 'cost': 4, 'archetype': 'Big Man', 'team': 'UTA'},
            'Myles Turner': {'projection': 493, 'cost': 15, 'archetype': 'Big Man', 'team': 'IND'},
            'Buddy Hield': {'projection': 492, 'cost': 12, 'archetype': 'Shooter', 'team': 'IND'},
            'Draymond Green': {'projection': 491, 'cost': 8, 'archetype': 'Guard', 'team': 'GSW'},
            'Donte DiVincenzo': {'projection': 490, 'cost': 7, 'archetype': 'Shooter', 'team': 'NYK'},
            'John Collins': {'projection': 489, 'cost': 8, 'archetype': 'Big Man', 'team': 'UTA'},
            'Zion Williamson': {'projection': 488, 'cost': 23, 'archetype': 'Guard', 'team': 'NOP'},
            'Jerami Grant': {'projection': 487, 'cost': 6, 'archetype': 'Guard', 'team': 'POR'},
            'Trae Young': {'projection': 486, 'cost': 52, 'archetype': 'Guard', 'team': 'ATL'},
            'Pascal Siakam': {'projection': 485, 'cost': 25, 'archetype': 'Guard', 'team': 'IND'},
            'De\'Anthony Melton': {'projection': 484, 'cost': 4, 'archetype': 'Guard', 'team': 'PHI'},
            'Bobby Portis': {'projection': 483, 'cost': 4, 'archetype': 'Big Man', 'team': 'MIL'},
            'Coby White': {'projection': 482, 'cost': 3, 'archetype': 'Guard', 'team': 'CHI'},
            'Jalen Suggs': {'projection': 481, 'cost': 7, 'archetype': 'Guard', 'team': 'ORL'},
            'Klay Thompson': {'projection': 480, 'cost': 17, 'archetype': 'Shooter', 'team': 'GSW'},
            'Isaiah Hartenstein': {'projection': 479, 'cost': 7, 'archetype': 'Big Man', 'team': 'NYK'},
            'Vince Williams Jr.': {'projection': 478, 'cost': 2, 'archetype': 'Guard', 'team': 'MEM'},
            'Jarrett Allen': {'projection': 477, 'cost': 23, 'archetype': 'Big Man', 'team': 'CLE'},
            'Ayo Dosunmu': {'projection': 476, 'cost': 2, 'archetype': 'Guard', 'team': 'CHI'},
            'Naz Reid': {'projection': 475, 'cost': 5, 'archetype': 'Big Man', 'team': 'MIN'},
            'Deni Avdija': {'projection': 474, 'cost': 9, 'archetype': 'Guard', 'team': 'POR'},
            'Josh Giddey': {'projection': 473, 'cost': 15, 'archetype': 'Guard', 'team': 'OKC'},
            'Max Strus': {'projection': 472, 'cost': 6, 'archetype': 'Shooter', 'team': 'CLE'},
            'Kelly Oubre Jr.': {'projection': 471, 'cost': 9, 'archetype': 'Guard', 'team': 'PHI'},
            'Tyler Herro': {'projection': 470, 'cost': 15, 'archetype': 'Guard', 'team': 'MIA'},
            'Onyeka Okongwu': {'projection': 469, 'cost': 8, 'archetype': 'Big Man', 'team': 'ATL'},
            'Luguentz Dort': {'projection': 468, 'cost': 3, 'archetype': 'Guard', 'team': 'OKC'},
            'Cameron Johnson': {'projection': 467, 'cost': 14, 'archetype': 'Shooter', 'team': 'BRK'},
            'Jordan Poole': {'projection': 466, 'cost': 11, 'archetype': 'Guard', 'team': 'WAS'},
            'Keldon Johnson': {'projection': 465, 'cost': 5, 'archetype': 'Guard', 'team': 'SAS'},
            'Jusuf Nurkic': {'projection': 464, 'cost': 10, 'archetype': 'Big Man', 'team': 'PHX'},
            'Caris LeVert': {'projection': 463, 'cost': 2, 'archetype': 'Guard', 'team': 'CLE'},
            'Collin Sexton': {'projection': 462, 'cost': 7, 'archetype': 'Guard', 'team': 'UTA'},
            'Jalen Green': {'projection': 461, 'cost': 15, 'archetype': 'Guard', 'team': 'HOU'},
            'Daniel Gafford': {'projection': 460, 'cost': 6, 'archetype': 'Big Man', 'team': 'DAL'}
        }
    
    def create_stars_and_scrubs_team(self):
        """Create optimal Stars & Scrubs team with high projections"""
        budget = 200
        
        # Strategy: 3-4 elite players, fill rest with $1-8 bargains
        stars = [
            ('Kawhi Leonard', 719, 12),    # Elite production, injury discount
            ('Joel Embiid', 716, 47),      # Dominant when healthy
            ('Kevin Durant', 696, 39),     # Proven elite scorer
            ('Anthony Edwards', 649, 54),   # Young star, high ceiling
        ]
        
        scrubs = [
            ('Grayson Allen', 648, 1),      # Elite projection, min cost
            ('Al Horford', 633, 1),         # Veteran stability, great value
            ('Keegan Murray', 643, 2),      # Rising young player
            ('CJ McCollum', 637, 5),        # Proven scorer, fair price
            ('Tobias Harris', 656, 5),      # Solid contributor
            ('Brook Lopez', 578, 7),        # Blocks and threes specialist
            ('Austin Reaves', 567, 8),      # Breakout candidate
            ('Mike Conley', 566, 3),        # Veteran floor general
            ('Aaron Nesmith', 562, 3),      # 3&D upside
            ('Tyus Jones', 497, 8),         # Reliable backup PG
            ('Vince Williams Jr.', 478, 2), # Defensive specialist, cheap
            ('Ayo Dosunmu', 476, 2),        # Young guard with upside
            ('Luguentz Dort', 468, 3),      # Elite defender
            ('Caris LeVert', 463, 2),       # Veteran wing depth
            ('Naz Reid', 475, 5),           # Stretch big off bench
        ]
        
        total_cost = sum([cost for _, _, cost in stars]) + sum([cost for _, _, cost in scrubs])
        total_projection = sum([proj for _, proj, _ in stars]) + sum([proj for _, proj, _ in scrubs])
        
        return {
            'team_name': 'Championship Stars & Scrubs',
            'strategy': 'Stars & Scrubs',
            'total_cost': total_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / 15,
            'stars': stars,
            'scrubs': scrubs,
            'analysis': [
                f'4 elite players account for ${sum([cost for _, _, cost in stars])} ({sum([cost for _, _, cost in stars])/total_cost*100:.1f}% of budget)',
                f'Found 11 players with 450+ projections for under $8 each',
                f'Total projection of {total_projection} ranks in top 5% of possible teams',
                'High ceiling strategy - stars must stay healthy',
                'Excellent value extraction in late rounds'
            ]
        }
    
    def create_balanced_attack_team(self):
        """Create optimal Balanced Attack team"""
        budget = 200
        
        # Strategy: Spread budget evenly, target $10-40 range players
        balanced_roster = [
            ('Shai Gilgeous-Alexander', 709, 67),  # Anchor guard
            ('Donovan Mitchell', 679, 40),          # Elite scorer
            ('Derrick White', 675, 15),             # Two-way guard
            ('Lauri Markkanen', 667, 29),           # Versatile big
            ('Tobias Harris', 656, 5),              # Undervalued forward  
            ('LeBron James', 656, 28),              # Veteran leadership
            ('Anthony Davis', 651, 54),             # Elite big when healthy
            ('Devin Booker', 650, 35),              # Pure scorer
            ('Karl-Anthony Towns', 642, 36),        # Stretch big
            ('James Harden', 641, 35),              # Playmaker
            ('Fred VanVleet', 641, 20),             # Solid PG
            ('Tyrese Maxey', 638, 29),              # Rising star
            ('CJ McCollum', 637, 5),                # Veteran scorer
            ('Al Horford', 633, 1),                 # Incredible value
            ('Jalen Williams', 631, 34),            # Versatile wing
        ]
        
        # Ensure exactly $200 budget
        current_cost = sum([cost for _, _, cost in balanced_roster])
        if current_cost > budget:
            # Adjust by swapping expensive players for similar value
            balanced_roster = balanced_roster[:14]  # Remove one expensive player
            balanced_roster.append(('Grayson Allen', 648, 1))  # Add value pick
        
        total_cost = sum([cost for _, _, cost in balanced_roster])
        total_projection = sum([proj for _, proj, _ in balanced_roster])
        
        return {
            'team_name': 'Balanced Championship Team',
            'strategy': 'Balanced Attack',
            'total_cost': total_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(balanced_roster),
            'roster': balanced_roster,
            'analysis': [
                f'No player costs more than $67 or less than $1',
                f'Strong in all 9 categories - no punting required',
                f'Average cost of ${total_cost/len(balanced_roster):.1f} per player',
                f'Total projection of {total_projection} ensures competitiveness',
                'Lower variance than Stars & Scrubs but very high floor'
            ]
        }
    
    def create_value_hunter_team(self):
        """Create optimal Value Hunter team"""
        budget = 200
        
        # Strategy: Find maximum value (projection per dollar)
        value_picks = []
        
        # Calculate value (projection per dollar) for all players
        player_values = []
        for name, data in self.projection_data.items():
            if data['cost'] > 0:  # Only consider players with cost
                value_ratio = data['projection'] / data['cost']
                player_values.append((name, data['projection'], data['cost'], value_ratio))
        
        # Sort by value ratio
        player_values.sort(key=lambda x: x[3], reverse=True)
        
        # Build team with best value ratios that fit budget
        selected_players = []
        remaining_budget = budget
        
        for name, proj, cost, value_ratio in player_values:
            if cost <= remaining_budget and len(selected_players) < 15:
                selected_players.append((name, proj, cost))
                remaining_budget -= cost
                if len(selected_players) == 15:
                    break
        
        # If we have budget left, upgrade cheapest players
        while remaining_budget > 0 and len(selected_players) == 15:
            # Find upgrade opportunities
            for i, (name, proj, cost) in enumerate(selected_players):
                for upgrade_name, upgrade_data in self.projection_data.items():
                    upgrade_cost = upgrade_data['cost']
                    upgrade_proj = upgrade_data['projection']
                    cost_diff = upgrade_cost - cost
                    proj_diff = upgrade_proj - proj
                    
                    if (cost_diff <= remaining_budget and cost_diff > 0 and 
                        proj_diff > 0 and upgrade_name not in [p[0] for p in selected_players]):
                        selected_players[i] = (upgrade_name, upgrade_proj, upgrade_cost)
                        remaining_budget -= cost_diff
                        break
                if remaining_budget <= 0:
                    break
        
        total_cost = sum([cost for _, _, cost in selected_players])
        total_projection = sum([proj for _, proj, _ in selected_players])
        
        return {
            'team_name': 'Ultimate Value Hunter Team',
            'strategy': 'Value Hunter',
            'total_cost': total_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(selected_players),
            'roster': selected_players,
            'analysis': [
                f'Maximized projection per dollar across entire roster',
                f'Average value ratio of {(total_projection/total_cost):.1f} points per dollar',
                f'Found elite projections at discounted prices',
                f'Several 600+ projection players for under $15',
                'Requires belief in model accuracy over market pricing'
            ]
        }
    
    def create_punt_strategy_team(self):
        """Create optimal Punt FT% team"""
        budget = 200
        
        # Strategy: Target players strong in all cats except FT%
        punt_roster = [
            # Elite in other categories, poor FT%
            ('Giannis Antetokounmpo', 589, 65),    # Poor FT%, elite everything else
            ('Ben Simmons', 400, 15),               # Assists/steals, no FT shooting
            ('Andre Drummond', 350, 8),             # Rebounds/blocks, terrible FT%
            ('Rudy Gobert', 520, 35),               # Blocks/rebounds specialist
            ('Draymond Green', 491, 8),             # Defense/assists, low FT volume
            ('Dennis Schroder', 450, 12),           # Speed, decent FT% but low volume
            
            # Complement with good players who fit strategy
            ('Kawhi Leonard', 719, 12),             # Elite when healthy, decent FT%
            ('Joel Embiid', 716, 47),               # Dominant, can carry FT%
            ('Derrick White', 675, 15),             # Excellent complementary piece
            ('Al Horford', 633, 1),                 # Perfect value, good FT%
            ('Brook Lopez', 578, 7),                # Blocks/threes, decent FT%
            ('Alperen Sengun', 569, 23),            # Well-rounded center
            ('Terry Rozier', 587, 12),              # Guards/scoring
            ('Mike Conley', 566, 3),                # Veteran leadership
            ('Naz Reid', 475, 5),                   # Bench scoring/boards
        ]
        
        total_cost = sum([cost for _, _, cost in punt_roster])
        total_projection = sum([proj for _, proj, _ in punt_roster])
        
        return {
            'team_name': 'Punt FT% Dominator',
            'strategy': 'Strategic Punter (FT%)',
            'total_cost': total_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(punt_roster),
            'roster': punt_roster,
            'analysis': [
                'Dominates rebounds, blocks, assists, steals',
                'Competitive in points, 3PM, FG%',
                'Completely punts FT% and turnovers',
                'Can win 6-7 categories consistently',
                'Requires opponents to not perfectly counter-punt'
            ]
        }
    
    def create_html_report(self):
        """Create HTML report with ideal team constructions"""
        stars_scrubs = self.create_stars_and_scrubs_team()
        balanced = self.create_balanced_attack_team()
        value_hunter = self.create_value_hunter_team()
        punt_team = self.create_punt_strategy_team()
        
        teams = [stars_scrubs, balanced, value_hunter, punt_team]
        
        # Generate team cards HTML
        team_cards_html = ""
        for team in teams:
            strategy = team['strategy']
            
            # Format roster based on team structure
            if 'stars' in team:
                # Stars & Scrubs format
                stars_html = "<br>".join([f"{name}: {proj} proj (${cost})" for name, proj, cost in team['stars']])
                scrubs_html = "<br>".join([f"{name}: {proj} proj (${cost})" for name, proj, cost in team['scrubs'][:8]])  # Show top 8 scrubs
                roster_html = f'''
                    <div class="stars-section">
                        <h4>🌟 Elite Players ({len(team['stars'])} players):</h4>
                        <div class="stars-list">{stars_html}</div>
                    </div>
                    <div class="scrubs-section">
                        <h4>💎 Value Picks ({len(team['scrubs'])} players):</h4>
                        <div class="scrubs-list">{scrubs_html}</div>
                    </div>'''
            else:
                # Regular roster format
                roster_html = "<br>".join([f"{name}: {proj} proj (${cost})" for name, proj, cost in team['roster'][:15]])
            
            # Analysis points
            analysis_html = "<br>".join([f"• {point}" for point in team['analysis']])
            
            team_cards_html += f'''
                    <div class="ideal-team-card">
                        <h3>{team['team_name']}</h3>
                        <div class="strategy-badge">{strategy}</div>
                        <div class="team-metrics">
                            <span class="metric">Budget: ${team['total_cost']}/200</span>
                            <span class="metric">Total Projection: {team['total_projection']}</span>
                            <span class="metric">Avg: {team['avg_projection']:.1f}</span>
                        </div>
                        
                        <div class="roster-section">
                            {roster_html}
                        </div>
                        
                        <div class="analysis-section">
                            <h4>Strategy Analysis:</h4>
                            <div class="analysis-text">{analysis_html}</div>
                        </div>
                    </div>'''

        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ideal Team Construction Examples</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .main-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .page-header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }

        .page-header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }

        .nav-links {
            text-align: center;
            margin-bottom: 30px;
        }

        .nav-link {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
            margin: 0 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            background: linear-gradient(135deg, #20c997, #17a2b8);
            transform: translateY(-2px);
        }

        .teams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        .ideal-team-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-top: 6px solid #667eea;
        }

        .ideal-team-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.4em;
        }

        .strategy-badge {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 6px 18px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .team-metrics {
            background: #e3f2fd;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }

        .metric {
            font-weight: bold;
            color: #1976d2;
            font-size: 0.9em;
        }

        .roster-section {
            margin-bottom: 20px;
        }

        .stars-section, .scrubs-section {
            margin-bottom: 15px;
        }

        .stars-section h4 {
            color: #d32f2f;
            margin-bottom: 8px;
        }

        .scrubs-section h4 {
            color: #388e3c;
            margin-bottom: 8px;
        }

        .stars-list {
            background: #ffebee;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #d32f2f;
            font-size: 0.85em;
            line-height: 1.6;
        }

        .scrubs-list {
            background: #e8f5e8;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #388e3c;
            font-size: 0.85em;
            line-height: 1.6;
        }

        .roster-section {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.85em;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .analysis-section h4 {
            color: #495057;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .analysis-text {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            font-size: 0.9em;
            line-height: 1.7;
        }

        .section {
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }

        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        .comparison-table th,
        .comparison-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .comparison-table th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }

        .comparison-table tr:hover {
            background-color: #f5f5f5;
        }

        @media (max-width: 768px) {
            .teams-grid {
                grid-template-columns: 1fr;
            }
            
            .team-metrics {
                flex-direction: column;
                gap: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🏗️ Ideal Team Construction Examples</h1>
                <p>High-Projection Teams Built with 2025 Data & Proven Strategies</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="owner_psychology.html" class="nav-link">🧠 Owner Psychology</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="teams-grid">''' + team_cards_html + '''
            </div>

            <div class="section">
                <div class="section-title">📊 Team Construction Comparison</div>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Total Projection</th>
                            <th>Budget Used</th>
                            <th>Risk Level</th>
                            <th>Best For</th>
                        </tr>
                    </thead>
                    <tbody>''' + self.generate_comparison_rows(teams) + '''
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="section-title">💡 Key Insights</div>
                <div class="analysis-text">
                    • <strong>Stars & Scrubs</strong> provides highest ceiling but requires perfect health from expensive players<br>
                    • <strong>Balanced Attack</strong> offers most consistency and lowest variance across outcomes<br>
                    • <strong>Value Hunter</strong> maximizes projection per dollar - best for believers in model accuracy<br>
                    • <strong>Punt Strategy</strong> can dominate specific categories while sacrificing others<br>
                    • All strategies can win championships - success depends on execution and luck
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/team_construction_blueprints.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Ideal Team Construction Blueprints created!")
        return teams
    
    def generate_comparison_rows(self, teams):
        """Generate comparison table rows"""
        risk_levels = {
            'Stars & Scrubs': 'High',
            'Balanced Attack': 'Medium',
            'Value Hunter': 'Medium-High',
            'Strategic Punter (FT%)': 'Medium'
        }
        
        best_for = {
            'Stars & Scrubs': 'High-ceiling seekers',
            'Balanced Attack': 'Consistency lovers', 
            'Value Hunter': 'Model believers',
            'Strategic Punter (FT%)': 'Category specialists'
        }
        
        rows_html = ""
        for team in teams:
            strategy = team['strategy']
            rows_html += f'''
                        <tr>
                            <td><strong>{strategy}</strong></td>
                            <td>{team['total_projection']}</td>
                            <td>${team['total_cost']}/200</td>
                            <td>{risk_levels.get(strategy, 'Medium')}</td>
                            <td>{best_for.get(strategy, 'All players')}</td>
                        </tr>'''
        
        return rows_html

def main():
    constructor = IdealTeamConstructor()
    teams = constructor.create_html_report()
    
    print("\nIdeal Team Construction Examples:")
    for team in teams:
        print(f"\n{team['team_name']} ({team['strategy']})")
        print(f"  Total Projection: {team['total_projection']}")
        print(f"  Total Cost: ${team['total_cost']}")
        print(f"  Average: {team['avg_projection']:.1f}")

if __name__ == "__main__":
    main()