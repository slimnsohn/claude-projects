#!/usr/bin/env python3
"""
Create ideal example teams with strict $200 budget constraint
"""

import json

class FixedBudgetTeamConstructor:
    def __init__(self):
        self.projection_data = {
            # Elite Tier (700+)
            'Kawhi Leonard': {'projection': 719, 'cost': 12, 'archetype': 'Shooter', 'team': 'LAC'},
            'Joel Embiid': {'projection': 716, 'cost': 47, 'archetype': 'Guard', 'team': 'PHI'},
            'Shai Gilgeous-Alexander': {'projection': 709, 'cost': 67, 'archetype': 'Guard', 'team': 'OKC'},
            'Kyrie Irving': {'projection': 700, 'cost': 31, 'archetype': 'Shooter', 'team': 'DAL'},
            'Kevin Durant': {'projection': 696, 'cost': 39, 'archetype': 'Shooter', 'team': 'PHX'},
            'Nikola Jokic': {'projection': 690, 'cost': 73, 'archetype': 'Guard', 'team': 'DEN'},
            
            # Strong Tier (600-699)
            'Donovan Mitchell': {'projection': 679, 'cost': 40, 'archetype': 'Shooter', 'team': 'CLE'},
            'Paul George': {'projection': 678, 'cost': 29, 'archetype': 'Shooter', 'team': 'LAC'},
            'Derrick White': {'projection': 675, 'cost': 15, 'archetype': 'Shooter', 'team': 'BOS'},
            'Jayson Tatum': {'projection': 671, 'cost': 51, 'archetype': 'Shooter', 'team': 'BOS'},
            'Tyrese Haliburton': {'projection': 670, 'cost': 50, 'archetype': 'Shooter', 'team': 'IND'},
            'Lauri Markkanen': {'projection': 667, 'cost': 29, 'archetype': 'Shooter', 'team': 'UTA'},
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
            
            # Solid Tier (500-599)
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
            
            # Value Tier (400-499)
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
            'Daniel Gafford': {'projection': 460, 'cost': 6, 'archetype': 'Big Man', 'team': 'DAL'},
            
            # Additional deep value players
            'Marcus Smart': {'projection': 450, 'cost': 3, 'archetype': 'Guard', 'team': 'MEM'},
            'Clint Capela': {'projection': 445, 'cost': 8, 'archetype': 'Big Man', 'team': 'ATL'},
            'Jonas Valanciunas': {'projection': 440, 'cost': 6, 'archetype': 'Big Man', 'team': 'NOP'},
            'Norman Powell': {'projection': 435, 'cost': 4, 'archetype': 'Guard', 'team': 'LAC'},
            'Rui Hachimura': {'projection': 430, 'cost': 3, 'archetype': 'Forward', 'team': 'LAL'},
            'Robert Williams III': {'projection': 425, 'cost': 5, 'archetype': 'Big Man', 'team': 'POR'},
            'Malik Monk': {'projection': 420, 'cost': 4, 'archetype': 'Guard', 'team': 'SAC'},
            'Talen Horton-Tucker': {'projection': 415, 'cost': 2, 'archetype': 'Guard', 'team': 'UTA'},
            'Duncan Robinson': {'projection': 410, 'cost': 2, 'archetype': 'Shooter', 'team': 'MIA'},
            'Derrick Jones Jr.': {'projection': 405, 'cost': 2, 'archetype': 'Forward', 'team': 'DAL'}
        }
    
    def build_stars_and_scrubs_200(self):
        """Build Stars & Scrubs team within $200 budget"""
        budget = 200
        roster = []
        current_cost = 0
        
        # Priority 1: Get 3 elite players (must stay under $200 total)
        stars = [
            ('Kawhi Leonard', 719, 12),  # Incredible value for elite projection
            ('Joel Embiid', 716, 47),    # Dominant center
            ('Kevin Durant', 696, 39),   # Veteran scorer
        ]
        
        for name, proj, cost in stars:
            roster.append((name, proj, cost))
            current_cost += cost
        
        remaining_budget = budget - current_cost  # $102 left for 12 players
        
        # Priority 2: Fill with best value picks under remaining budget
        value_candidates = [
            ('Grayson Allen', 648, 1),
            ('Al Horford', 633, 1), 
            ('Keegan Murray', 643, 2),
            ('Vince Williams Jr.', 478, 2),
            ('Ayo Dosunmu', 476, 2),
            ('Caris LeVert', 463, 2),
            ('Talen Horton-Tucker', 415, 2),
            ('Duncan Robinson', 410, 2),
            ('Derrick Jones Jr.', 405, 2),
            ('Mike Conley', 566, 3),
            ('Aaron Nesmith', 562, 3),
            ('Coby White', 482, 3),
            ('Luguentz Dort', 468, 3),
            ('Marcus Smart', 450, 3),
            ('Rui Hachimura', 430, 3)
        ]
        
        # Sort by projection and add until budget is reached
        value_candidates.sort(key=lambda x: x[1], reverse=True)
        
        for name, proj, cost in value_candidates:
            if current_cost + cost <= budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        # Fill remaining spots with $1-2 players if needed
        if len(roster) < 15:
            cheap_fills = [
                ('Tobias Harris', 656, 5),
                ('CJ McCollum', 637, 5),
                ('Keldon Johnson', 465, 5),
                ('Naz Reid', 475, 5),
                ('Alex Caruso', 572, 4),
                ('Kelly Olynyk', 494, 4),
                ('De\'Anthony Melton', 484, 4),
                ('Bobby Portis', 483, 4),
                ('Malik Monk', 420, 4),
                ('Norman Powell', 435, 4)
            ]
            
            for name, proj, cost in cheap_fills:
                if current_cost + cost <= budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Budget Stars & Scrubs',
            'strategy': 'Stars & Scrubs',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(roster),
            'analysis': [
                f'3 elite players cost ${current_cost - sum([cost for _, _, cost in roster[3:]])} ({(current_cost - sum([cost for _, _, cost in roster[3:]]))/current_cost*100:.1f}% of budget)',
                f'Found {len(roster)-3} value players averaging ${sum([cost for _, _, cost in roster[3:]])/(len(roster)-3):.1f} each',
                f'Elite trio averages {sum([proj for _, proj, _ in roster[:3]])/3:.0f} projection each',
                f'Value players average {sum([proj for _, proj, _ in roster[3:]])/(len(roster)-3):.0f} projection each',
                'High ceiling, requires star health'
            ]
        }
    
    def build_balanced_attack_200(self):
        """Build Balanced Attack team within $200 budget"""
        budget = 200
        roster = []
        current_cost = 0
        
        # Target players in $10-40 range for balance
        balanced_targets = [
            ('Derrick White', 675, 15),    # Elite 2-way guard
            ('Lauri Markkanen', 667, 29),  # Versatile big
            ('LeBron James', 656, 28),     # Veteran leadership  
            ('Devin Booker', 650, 35),     # Pure scorer
            ('Kyrie Irving', 700, 31),     # Elite guard
            ('Paul George', 678, 29),      # 2-way wing
            ('James Harden', 641, 35),     # Playmaker
            ('Fred VanVleet', 641, 20),    # Solid PG
            ('Tyrese Maxey', 638, 29),     # Rising star
            ('Jimmy Butler', 592, 22),     # Veteran leader
            ('Franz Wagner', 582, 21),     # Young wing
            ('Cade Cunningham', 577, 19),  # Young PG
            ('OG Anunoby', 573, 17),       # 3&D wing
            ('Nikola Vucevic', 583, 16),   # Scoring big
            ('Myles Turner', 493, 15)      # Blocks specialist
        ]
        
        # Sort by value (projection per dollar) and select
        balanced_targets.sort(key=lambda x: x[1]/x[2], reverse=True)
        
        for name, proj, cost in balanced_targets:
            if current_cost + cost <= budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Balanced Excellence',
            'strategy': 'Balanced Attack', 
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(roster),
            'analysis': [
                f'All players cost between $15-35 (balanced spending)',
                f'Average cost: ${current_cost/len(roster):.1f} per player',
                f'No single point of failure - depth across roster',
                f'Competitive in all 9 categories',
                'Consistent floor, good ceiling'
            ]
        }
    
    def build_value_hunter_200(self):
        """Build Value Hunter team within exactly $200 budget"""
        budget = 200
        
        # Calculate value ratio for all players and sort
        value_players = []
        for name, data in self.projection_data.items():
            if data['cost'] > 0:
                value_ratio = data['projection'] / data['cost']
                value_players.append((name, data['projection'], data['cost'], value_ratio))
        
        value_players.sort(key=lambda x: x[3], reverse=True)  # Sort by value ratio
        
        roster = []
        current_cost = 0
        
        # Greedy selection by value ratio
        for name, proj, cost, ratio in value_players:
            if current_cost + cost <= budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        avg_value_ratio = total_projection / current_cost
        
        return {
            'name': 'Value Maximizer',
            'strategy': 'Value Hunter',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(roster),
            'analysis': [
                f'Maximized projection per dollar: {avg_value_ratio:.1f} points/$',
                f'Found {len([p for p in roster if p[1] >= 600])} players with 600+ projections',
                f'Average cost only ${current_cost/len(roster):.1f} per player',
                f'Several elite values: {roster[0][0]} ({roster[0][1]} proj, ${roster[0][2]})',
                'Requires belief in model over market'
            ]
        }
    
    def build_punt_ft_200(self):
        """Build Punt FT% team within $200 budget"""
        budget = 200
        roster = []
        current_cost = 0
        
        # Target players good at everything except FT%
        punt_targets = [
            # Core punt players (strong everywhere but FT%)
            ('Giannis Antetokounmpo', 589, 65),  # Elite but poor FT%
            ('Draymond Green', 491, 8),           # Assists/defense, low FT attempts
            ('Brook Lopez', 578, 7),              # Blocks/threes, decent FT%
            ('Alperen Sengun', 569, 23),          # Well-rounded center
            ('Jarrett Allen', 477, 23),           # Rebounds/blocks
            ('Clint Capela', 445, 8),             # Pure rebounder/shot blocker
            ('Robert Williams III', 425, 5),      # Blocks when healthy
            ('Jonas Valanciunas', 440, 6),        # Rebounds/blocks
            
            # Complement with good FT shooters for balance
            ('Kawhi Leonard', 719, 12),           # Elite when healthy
            ('Derrick White', 675, 15),           # Perfect complementary piece
            ('Al Horford', 633, 1),               # Incredible value
            ('Mike Conley', 566, 3),              # Veteran leadership
            ('Terry Rozier', 587, 12),            # Scoring guard
            ('Tyus Jones', 497, 8),               # Pass-first PG
            ('Austin Reaves', 567, 8)             # Young guard
        ]
        
        # Add players within budget
        for name, proj, cost in punt_targets:
            if current_cost + cost <= budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'FT% Punt Specialist',
            'strategy': 'Punt FT%',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': total_projection / len(roster),
            'analysis': [
                'Elite in rebounds, blocks, assists, steals',
                'Competitive in points, 3PM, FG%', 
                'Completely sacrifice FT% category',
                f'Can win 6-7 categories vs balanced teams',
                'Requires opponents not to counter-punt'
            ]
        }
    
    def create_fixed_html_report(self):
        """Create HTML report with budget-compliant teams"""
        stars_scrubs = self.build_stars_and_scrubs_200()
        balanced = self.build_balanced_attack_200()
        value_hunter = self.build_value_hunter_200()
        punt_team = self.build_punt_ft_200()
        
        teams = [stars_scrubs, balanced, value_hunter, punt_team]
        
        # Verify all teams are under budget
        for team in teams:
            if team['total_cost'] > 200:
                print(f"WARNING: {team['name']} exceeds budget: ${team['total_cost']}")
        
        # Generate team cards HTML
        team_cards_html = ""
        for team in teams:
            # Show top 8 players to save space
            roster_display = team['roster'][:8]
            remaining_count = len(team['roster']) - 8
            
            roster_html = "<br>".join([f"{name}: {proj} proj (${cost})" for name, proj, cost in roster_display])
            if remaining_count > 0:
                roster_html += f"<br><em>...and {remaining_count} more players</em>"
            
            analysis_html = "<br>".join([f"• {point}" for point in team['analysis']])
            
            # Color code based on budget usage
            budget_color = "#28a745" if team['total_cost'] <= 200 else "#dc3545"
            
            team_cards_html += f'''
                    <div class="ideal-team-card">
                        <h3>{team['name']}</h3>
                        <div class="strategy-badge">{team['strategy']}</div>
                        <div class="team-metrics">
                            <span class="metric" style="color: {budget_color}">Budget: ${team['total_cost']}/200</span>
                            <span class="metric">Total: {team['total_projection']}</span>
                            <span class="metric">Avg: {team['avg_projection']:.1f}</span>
                        </div>
                        
                        <div class="roster-section">
                            <h4>Key Players:</h4>
                            <div class="roster-list">{roster_html}</div>
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
    <title>Budget-Compliant Team Construction</title>
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
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }

        .ideal-team-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            border-top: 5px solid #667eea;
        }

        .ideal-team-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .strategy-badge {
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .team-metrics {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }

        .metric {
            font-weight: bold;
            color: #1976d2;
            font-size: 0.85em;
        }

        .roster-section h4, .analysis-section h4 {
            color: #495057;
            margin-bottom: 8px;
            font-size: 1em;
        }

        .roster-list {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.8em;
            line-height: 1.5;
            margin-bottom: 15px;
        }

        .analysis-text {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            font-size: 0.85em;
            line-height: 1.6;
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
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            font-size: 0.9em;
        }

        .comparison-table th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }

        .comparison-table tr:hover {
            background-color: #f5f5f5;
        }

        .budget-compliant {
            color: #28a745;
            font-weight: bold;
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
                <h1>🏗️ Budget-Compliant Team Construction</h1>
                <p>Championship Teams Built Within $200 Auction Budget</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="owner_psychology.html" class="nav-link">🧠 Owner Psychology</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="teams-grid">''' + team_cards_html + '''
            </div>

            <div class="section">
                <div class="section-title">📊 Budget-Compliant Comparison</div>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Team Strategy</th>
                            <th>Total Cost</th>
                            <th>Total Projection</th>
                            <th>Efficiency (Proj/$)</th>
                            <th>Risk Level</th>
                        </tr>
                    </thead>
                    <tbody>''' + self.generate_budget_comparison_rows(teams) + '''
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="section-title">💡 Budget Management Insights</div>
                <div class="analysis-text">
                    • <strong>Budget Discipline:</strong> All teams stay within $200 constraint while maximizing value<br>
                    • <strong>Stars & Scrubs:</strong> Invests heavily in 3 elite players, fills rest with incredible value finds<br>
                    • <strong>Balanced Attack:</strong> Spreads budget evenly across all positions for consistency<br>
                    • <strong>Value Hunter:</strong> Maximizes projection per dollar - best bang for buck<br>
                    • <strong>Punt Strategy:</strong> Sacrifices one category to dominate others within budget<br>
                    • <strong>Key Lesson:</strong> Championship teams can be built with any strategy if you maximize value within constraints
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        with open('html_reports/prod_ready/team_construction_blueprints.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Budget-Compliant Team Construction Blueprints created!")
        return teams
    
    def generate_budget_comparison_rows(self, teams):
        """Generate comparison table rows for budget teams"""
        risk_levels = {
            'Stars & Scrubs': 'High',
            'Balanced Attack': 'Medium',
            'Value Hunter': 'Medium-High', 
            'Punt FT%': 'Medium'
        }
        
        rows_html = ""
        for team in teams:
            efficiency = team['total_projection'] / team['total_cost']
            budget_class = "budget-compliant" if team['total_cost'] <= 200 else ""
            
            rows_html += f'''
                        <tr>
                            <td><strong>{team['strategy']}</strong></td>
                            <td class="{budget_class}">${team['total_cost']}/200</td>
                            <td>{team['total_projection']}</td>
                            <td>{efficiency:.1f}</td>
                            <td>{risk_levels.get(team['strategy'], 'Medium')}</td>
                        </tr>'''
        
        return rows_html

def main():
    constructor = FixedBudgetTeamConstructor()
    teams = constructor.create_fixed_html_report()
    
    print("\nBudget-Compliant Team Examples:")
    for team in teams:
        print(f"\n{team['name']} ({team['strategy']})")
        print(f"  Budget: ${team['total_cost']}/200 ✓" if team['total_cost'] <= 200 else f"  Budget: ${team['total_cost']}/200 ❌")
        print(f"  Total Projection: {team['total_projection']}")
        print(f"  Efficiency: {team['total_projection']/team['total_cost']:.1f} proj/$")

if __name__ == "__main__":
    main()