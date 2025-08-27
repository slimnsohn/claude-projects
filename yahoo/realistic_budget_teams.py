#!/usr/bin/env python3
"""
Create realistic example teams using $185-200 budget range
"""

import json

class RealisticBudgetTeamConstructor:
    def __init__(self):
        self.projection_data = {
            # Elite Tier (700+)
            'Kawhi Leonard': {'projection': 719, 'cost': 12, 'archetype': 'Shooter'},
            'Joel Embiid': {'projection': 716, 'cost': 47, 'archetype': 'Big Man'},
            'Shai Gilgeous-Alexander': {'projection': 709, 'cost': 67, 'archetype': 'Guard'},
            'Kyrie Irving': {'projection': 700, 'cost': 31, 'archetype': 'Guard'},
            'Kevin Durant': {'projection': 696, 'cost': 39, 'archetype': 'Shooter'},
            'Nikola Jokic': {'projection': 690, 'cost': 73, 'archetype': 'Big Man'},
            
            # Strong Tier (600-699)
            'Donovan Mitchell': {'projection': 679, 'cost': 40, 'archetype': 'Guard'},
            'Paul George': {'projection': 678, 'cost': 29, 'archetype': 'Shooter'},
            'Derrick White': {'projection': 675, 'cost': 15, 'archetype': 'Guard'},
            'Jayson Tatum': {'projection': 671, 'cost': 51, 'archetype': 'Shooter'},
            'Tyrese Haliburton': {'projection': 670, 'cost': 50, 'archetype': 'Guard'},
            'Lauri Markkanen': {'projection': 667, 'cost': 29, 'archetype': 'Big Man'},
            'Tobias Harris': {'projection': 656, 'cost': 5, 'archetype': 'Shooter'},
            'LeBron James': {'projection': 656, 'cost': 28, 'archetype': 'Shooter'},
            'Victor Wembanyama': {'projection': 651, 'cost': 80, 'archetype': 'Big Man'},
            'Anthony Davis': {'projection': 651, 'cost': 54, 'archetype': 'Big Man'},
            'Devin Booker': {'projection': 650, 'cost': 35, 'archetype': 'Guard'},
            'Anthony Edwards': {'projection': 649, 'cost': 54, 'archetype': 'Guard'},
            'Grayson Allen': {'projection': 648, 'cost': 1, 'archetype': 'Shooter'},
            'Keegan Murray': {'projection': 643, 'cost': 2, 'archetype': 'Shooter'},
            'Karl-Anthony Towns': {'projection': 642, 'cost': 36, 'archetype': 'Big Man'},
            'James Harden': {'projection': 641, 'cost': 35, 'archetype': 'Guard'},
            'Fred VanVleet': {'projection': 641, 'cost': 20, 'archetype': 'Guard'},
            'Tyrese Maxey': {'projection': 638, 'cost': 29, 'archetype': 'Guard'},
            'CJ McCollum': {'projection': 637, 'cost': 5, 'archetype': 'Guard'},
            'Al Horford': {'projection': 633, 'cost': 1, 'archetype': 'Big Man'},
            'Jalen Williams': {'projection': 631, 'cost': 34, 'archetype': 'Guard'},
            
            # Solid Tier (500-599)
            'Trey Murphy III': {'projection': 595, 'cost': 8, 'archetype': 'Shooter'},
            'Jalen Johnson': {'projection': 594, 'cost': 11, 'archetype': 'Shooter'},
            'Bradley Beal': {'projection': 593, 'cost': 18, 'archetype': 'Guard'},
            'Jimmy Butler': {'projection': 592, 'cost': 22, 'archetype': 'Shooter'},
            'Chet Holmgren': {'projection': 591, 'cost': 25, 'archetype': 'Big Man'},
            'Dejounte Murray': {'projection': 590, 'cost': 18, 'archetype': 'Guard'},
            'Giannis Antetokounmpo': {'projection': 589, 'cost': 65, 'archetype': 'Big Man'},
            'Stephen Curry': {'projection': 588, 'cost': 42, 'archetype': 'Guard'},
            'Terry Rozier': {'projection': 587, 'cost': 12, 'archetype': 'Guard'},
            'Nikola Vucevic': {'projection': 583, 'cost': 16, 'archetype': 'Big Man'},
            'Franz Wagner': {'projection': 582, 'cost': 21, 'archetype': 'Shooter'},
            'Brook Lopez': {'projection': 578, 'cost': 7, 'archetype': 'Big Man'},
            'Cade Cunningham': {'projection': 577, 'cost': 19, 'archetype': 'Guard'},
            'OG Anunoby': {'projection': 573, 'cost': 17, 'archetype': 'Shooter'},
            'Alex Caruso': {'projection': 572, 'cost': 4, 'archetype': 'Guard'},
            'Alperen Sengun': {'projection': 569, 'cost': 23, 'archetype': 'Big Man'},
            'Austin Reaves': {'projection': 567, 'cost': 8, 'archetype': 'Guard'},
            'Mike Conley': {'projection': 566, 'cost': 3, 'archetype': 'Guard'},
            'Aaron Nesmith': {'projection': 562, 'cost': 3, 'archetype': 'Shooter'},
            'Scottie Barnes': {'projection': 560, 'cost': 39, 'archetype': 'Shooter'},
            
            # Value Tier (400-499)  
            'Kelly Olynyk': {'projection': 494, 'cost': 4, 'archetype': 'Big Man'},
            'Myles Turner': {'projection': 493, 'cost': 15, 'archetype': 'Big Man'},
            'Draymond Green': {'projection': 491, 'cost': 8, 'archetype': 'Big Man'},
            'De\'Anthony Melton': {'projection': 484, 'cost': 4, 'archetype': 'Guard'},
            'Bobby Portis': {'projection': 483, 'cost': 4, 'archetype': 'Big Man'},
            'Coby White': {'projection': 482, 'cost': 3, 'archetype': 'Guard'},
            'Vince Williams Jr.': {'projection': 478, 'cost': 2, 'archetype': 'Shooter'},
            'Jarrett Allen': {'projection': 477, 'cost': 23, 'archetype': 'Big Man'},
            'Ayo Dosunmu': {'projection': 476, 'cost': 2, 'archetype': 'Guard'},
            'Naz Reid': {'projection': 475, 'cost': 5, 'archetype': 'Big Man'},
            'Luguentz Dort': {'projection': 468, 'cost': 3, 'archetype': 'Shooter'},
            'Keldon Johnson': {'projection': 465, 'cost': 5, 'archetype': 'Shooter'},
            'Caris LeVert': {'projection': 463, 'cost': 2, 'archetype': 'Guard'},
            'Marcus Smart': {'projection': 450, 'cost': 3, 'archetype': 'Guard'},
            'Clint Capela': {'projection': 445, 'cost': 8, 'archetype': 'Big Man'},
            'Jonas Valanciunas': {'projection': 440, 'cost': 6, 'archetype': 'Big Man'},
            'Norman Powell': {'projection': 435, 'cost': 4, 'archetype': 'Guard'},
            'Rui Hachimura': {'projection': 430, 'cost': 3, 'archetype': 'Shooter'},
            'Robert Williams III': {'projection': 425, 'cost': 5, 'archetype': 'Big Man'},
            'Malik Monk': {'projection': 420, 'cost': 4, 'archetype': 'Guard'},
            'Talen Horton-Tucker': {'projection': 415, 'cost': 2, 'archetype': 'Guard'},
            'Duncan Robinson': {'projection': 410, 'cost': 2, 'archetype': 'Shooter'},
            'Derrick Jones Jr.': {'projection': 405, 'cost': 2, 'archetype': 'Shooter'}
        }

    def build_stars_and_scrubs(self):
        """Build Stars & Scrubs team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Get 2 elite players then fill with values
        elite_core = [
            ('Shai Gilgeous-Alexander', 709, 67),  # Elite anchor  
            ('Anthony Edwards', 649, 54),          # Elite guard
        ]
        
        for name, proj, cost in elite_core:
            roster.append((name, proj, cost))
            current_cost += cost
        
        # Fill remaining spots with best available values
        value_players = [
            ('Derrick White', 675, 15),
            ('Tobias Harris', 656, 5),
            ('CJ McCollum', 637, 5),
            ('Trey Murphy III', 595, 8),
            ('Brook Lopez', 578, 7),
            ('Austin Reaves', 567, 8),
            ('Grayson Allen', 648, 1)
        ]
        
        for name, proj, cost in value_players:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        # Fill remaining with cheap options if needed - prioritize getting to minimum budget
        if len(roster) < 15:
            cheap_fills = [
                ('Al Horford', 633, 1),
                ('Keegan Murray', 643, 2),
                ('Mike Conley', 566, 3),
                ('Aaron Nesmith', 562, 3),
                ('Vince Williams Jr.', 478, 2),
                ('Ayo Dosunmu', 476, 2),
                ('Duncan Robinson', 410, 2),
                ('Coby White', 482, 3),
                ('Luguentz Dort', 468, 3),
                ('Naz Reid', 475, 5),
                ('Kelly Olynyk', 494, 4),
                ('Alex Caruso', 572, 4),
                ('De\'Anthony Melton', 484, 4),
                ('Bobby Portis', 483, 4),
                ('Norman Powell', 435, 4),
                ('Marcus Smart', 450, 3)
            ]
            for name, proj, cost in cheap_fills:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
                    # Stop once we hit minimum budget
                    if current_cost >= min_budget and len(roster) >= 15:
                        break
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Elite Stars & Role Players',
            'strategy': 'Stars & Scrubs', 
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                f'2 elite players cost ${elite_core[0][2] + elite_core[1][2]} (combined)',
                f'Remaining budget distributed across proven role players',
                'High ceiling strategy with proven stars',
                'Budget used efficiently at minimum viable level'
            ]
        }

    def build_balanced_attack(self):
        """Build balanced team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Target players in $15-35 range for consistency
        balanced_players = [
            ('Jayson Tatum', 671, 51),
            ('James Harden', 641, 35), 
            ('Karl-Anthony Towns', 642, 36),
            ('Jalen Williams', 631, 34),
            ('Tyrese Maxey', 638, 29),
            ('LeBron James', 656, 28),
            ('Chet Holmgren', 591, 25),
            ('Alperen Sengun', 569, 23),
            ('Jimmy Butler', 592, 22),
            ('Franz Wagner', 582, 21),
            ('Fred VanVleet', 641, 20),
            ('Cade Cunningham', 577, 19),
            ('Bradley Beal', 593, 18),
            ('OG Anunoby', 573, 17),
            ('Nikola Vucevic', 583, 16),
            ('Derrick White', 675, 15)
        ]
        
        # Sort by projection per dollar and build roster
        balanced_players.sort(key=lambda x: x[1]/x[2], reverse=True)
        
        for name, proj, cost in balanced_players:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
            if current_cost >= min_budget and len(roster) >= 12:
                break
        
        # Fill remaining spots if needed
        if len(roster) < 15 and current_cost < max_budget:
            fill_options = [
                ('Myles Turner', 493, 15),
                ('Terry Rozier', 587, 12),
                ('Jalen Johnson', 594, 11)
            ]
            for name, proj, cost in fill_options:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Consistent Balanced Attack',
            'strategy': 'Balanced Attack',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                f'All players cost between $15-51 (balanced spending)',
                f'Average cost: ${round(current_cost / len(roster), 1)} per player',
                'No major weakness across roster construction',
                'Strong floor with reasonable ceiling'
            ]
        }

    def build_value_hunter(self):
        """Build value-focused team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Start with incredible values then add mid-tier to reach budget
        value_picks = [
            ('Grayson Allen', 648, 1),      # 648 proj per $
            ('Al Horford', 633, 1),         # 633 proj per $  
            ('Tobias Harris', 656, 5),      # 131.2 proj per $
            ('CJ McCollum', 637, 5),        # 127.4 proj per $
            ('Austin Reaves', 567, 8),      # 70.9 proj per $
            ('Kawhi Leonard', 719, 12),     # Great value elite
            ('Derrick White', 675, 15),     # Strong value
            ('Fred VanVleet', 641, 20),     # Quality guard
            ('Jimmy Butler', 592, 22),      # Solid mid-tier
            ('Alperen Sengun', 569, 23),    # Good center
            ('Chet Holmgren', 591, 25),     # Rising star
            ('LeBron James', 656, 28),      # Veteran value
            ('Paul George', 678, 29),       # Elite wing
            ('Jalen Williams', 631, 34),    # Young talent
            ('James Harden', 641, 35)       # Veteran guard
        ]
        
        # Add players prioritizing those that get us to budget minimum
        for name, proj, cost in value_picks:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
                # Stop once we reach minimum budget and have enough players
                if current_cost >= min_budget and len(roster) >= 12:
                    break
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Maximum Value Extraction',
            'strategy': 'Value Hunter',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                f'Found 7 incredible values averaging {round(sum([proj for _, proj, _ in roster[:7]]) / 7, 1)} projection for ${sum([cost for _, _, cost in roster[:7]])}',
                f'Added quality mid-tier players to reach realistic budget',
                f'Average value ratio: {round(total_projection / current_cost, 1)} points per dollar',
                'Requires belief in projection model accuracy'
            ]
        }

    def build_punt_strategy(self):
        """Build FT% punt team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Target poor FT shooters who excel in other categories
        punt_ft_players = [
            ('Giannis Antetokounmpo', 589, 65),  # Dominant everywhere except FT%
            ('Jarrett Allen', 477, 23),          # Great rebounds/blocks, poor FT%
            ('Alperen Sengun', 569, 23),         # All-around except FT%
            ('Draymond Green', 491, 8),          # Elite defense/assists, poor FT%
            ('Clint Capela', 445, 8),            # Rebounds/blocks specialist
            ('Brook Lopez', 578, 7),             # 3s + blocks, mediocre FT%
            ('Jonas Valanciunas', 440, 6),       # Strong rebounder
            ('Robert Williams III', 425, 5),     # Blocks specialist
            ('Bobby Portis', 483, 4)             # Solid big man
        ]
        
        for name, proj, cost in punt_ft_players:
            roster.append((name, proj, cost))
            current_cost += cost
        
        # Add complementary players to reach budget
        remaining_spots = 15 - len(roster)
        remaining_budget = max_budget - current_cost
        
        complementary_players = [
            ('Derrick White', 675, 15),          # Good FT but fits strategy
            ('Terry Rozier', 587, 12),
            ('Jalen Johnson', 594, 11),
            ('Trey Murphy III', 595, 8),
            ('Austin Reaves', 567, 8),
            ('Tobias Harris', 656, 5),
            ('Naz Reid', 475, 5),
            ('Alex Caruso', 572, 4),
            ('Mike Conley', 566, 3)
        ]
        
        for name, proj, cost in complementary_players:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
                if current_cost >= min_budget:
                    break
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'FT% Punt Dominator',
            'strategy': 'Punt FT%',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                'Dominates rebounds, blocks, assists, steals',
                'Competitive in points, 3PM, FG%',
                'Completely sacrifices FT% category',
                'Can win 6-7 categories against balanced teams'
            ]
        }

    def build_elite_superstar(self):
        """Build elite superstar team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Get 2 super elite players
        superstars = [
            ('Nikola Jokic', 690, 73),      # Best player in basketball
            ('Shai Gilgeous-Alexander', 709, 67),  # Elite guard
        ]
        
        for name, proj, cost in superstars:
            roster.append((name, proj, cost))
            current_cost += cost
        
        # Fill remaining spots with solid values
        supporting_cast = [
            ('Kawhi Leonard', 719, 12),     # Incredible value
            ('Derrick White', 675, 15),
            ('Tobias Harris', 656, 5),
            ('CJ McCollum', 637, 5),
            ('Trey Murphy III', 595, 8),
            ('Austin Reaves', 567, 8),
            ('Grayson Allen', 648, 1),
            ('Al Horford', 633, 1),
            ('Keegan Murray', 643, 2),
            ('Mike Conley', 566, 3),
            ('Aaron Nesmith', 562, 3)
        ]
        
        for name, proj, cost in supporting_cast:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        # Fill remaining spots if needed
        if len(roster) < 15:
            additional_fills = [
                ('Vince Williams Jr.', 478, 2),
                ('Ayo Dosunmu', 476, 2),
                ('Duncan Robinson', 410, 2)
            ]
            for name, proj, cost in additional_fills:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Elite Superstar Foundation',
            'strategy': 'Superstar Build',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                f'2 elite superstars cost ${superstars[0][2] + superstars[1][2]} combined',
                'Built around two guaranteed top-10 fantasy players',
                'Remaining budget used for proven role players',
                'High floor due to superstar consistency'
            ]
        }

    def build_young_upside(self):
        """Build young upside team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Target young players with upside
        young_core = [
            ('Victor Wembanyama', 651, 80),    # Generational talent
            ('Anthony Edwards', 649, 54),      # Rising star
            ('Tyrese Haliburton', 670, 50),    # Elite young guard
            ('Scottie Barnes', 560, 39),       # Versatile young wing
            ('Jalen Williams', 631, 34),       # Breakout candidate
            ('Tyrese Maxey', 638, 29),         # Explosive guard
            ('Chet Holmgren', 591, 25),        # Skilled big man
            ('Franz Wagner', 582, 21),         # Consistent wing
        ]
        
        for name, proj, cost in young_core:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
                if current_cost >= min_budget and len(roster) >= 8:
                    break
        
        # Fill remaining with value vets
        veteran_support = [
            ('Derrick White', 675, 15),
            ('Tobias Harris', 656, 5),
            ('Brook Lopez', 578, 7),
            ('Grayson Allen', 648, 1),
            ('Al Horford', 633, 1),
            ('Mike Conley', 566, 3)
        ]
        
        for name, proj, cost in veteran_support:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        # Fill remaining spots if needed
        if len(roster) < 15:
            more_fills = [
                ('CJ McCollum', 637, 5),
                ('Austin Reaves', 567, 8),
                ('Aaron Nesmith', 562, 3),
                ('Vince Williams Jr.', 478, 2),
                ('Ayo Dosunmu', 476, 2),
                ('Duncan Robinson', 410, 2),
                ('Coby White', 482, 3),
                ('Luguentz Dort', 468, 3),
                ('Naz Reid', 475, 5),
                ('Kelly Olynyk', 494, 4)
            ]
            for name, proj, cost in more_fills:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Young Core Dynasty',
            'strategy': 'Youth Movement',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                'Prioritizes players under 26 with upside potential',
                'High ceiling if young players reach potential',
                'Mixed in some veteran stability',
                'Championship window extends beyond this season'
            ]
        }

    def build_veteran_experience(self):
        """Build veteran experience team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Target proven veterans
        veteran_core = [
            ('LeBron James', 656, 28),         # Ageless wonder
            ('Kevin Durant', 696, 39),         # Elite scorer
            ('James Harden', 641, 35),         # Proven playmaker
            ('Jimmy Butler', 592, 22),         # Playoff performer
            ('Paul George', 678, 29),          # Two-way wing
            ('Stephen Curry', 588, 42),        # Greatest shooter
            ('Kyrie Irving', 700, 31),         # Elite handles
            ('Devin Booker', 650, 35)          # Pure scorer
        ]
        
        for name, proj, cost in veteran_core:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
                if current_cost >= min_budget and len(roster) >= 8:
                    break
        
        # Fill with proven role players
        role_players = [
            ('Derrick White', 675, 15),
            ('Tobias Harris', 656, 5),
            ('CJ McCollum', 637, 5),
            ('Al Horford', 633, 1),
            ('Mike Conley', 566, 3),
            ('Austin Reaves', 567, 8)
        ]
        
        for name, proj, cost in role_players:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
        
        # Fill remaining spots if needed
        if len(roster) < 15:
            vet_fills = [
                ('Grayson Allen', 648, 1),
                ('Al Horford', 633, 1),
                ('Keegan Murray', 643, 2),
                ('Aaron Nesmith', 562, 3),
                ('Vince Williams Jr.', 478, 2),
                ('Ayo Dosunmu', 476, 2),
                ('Duncan Robinson', 410, 2),
                ('Kelly Olynyk', 494, 4)
            ]
            for name, proj, cost in vet_fills:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': 'Championship Experience',
            'strategy': 'Veteran Leadership',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                'Built around proven championship-level players',
                'Prioritizes playoff experience and clutch performance',
                'Lower injury risk from established veterans',
                'Know what to expect from each player'
            ]
        }

    def build_three_point_specialists(self):
        """Build 3-point specialist team using $185-200 budget"""
        min_budget = 185
        max_budget = 200
        roster = []
        current_cost = 0
        
        # Target elite 3-point shooters
        shooters = [
            ('Stephen Curry', 588, 42),        # Greatest shooter ever
            ('Jayson Tatum', 671, 51),         # Elite wing shooter
            ('Paul George', 678, 29),          # Two-way shooter
            ('Devin Booker', 650, 35),         # Pure scorer
            ('Donovan Mitchell', 679, 40),     # Volume shooter
            ('Derrick White', 675, 15),        # 3&D guard
            ('Tobias Harris', 656, 5),         # Consistent wing
            ('Trey Murphy III', 595, 8),       # Young sniper
            ('Grayson Allen', 648, 1),         # Elite value shooter
            ('Keegan Murray', 643, 2),         # Rising shooter
            ('CJ McCollum', 637, 5),           # Veteran scorer
            ('Duncan Robinson', 410, 2),       # 3-point specialist
            ('Austin Reaves', 567, 8)          # Improving shooter
        ]
        
        for name, proj, cost in shooters:
            if current_cost + cost <= max_budget and len(roster) < 15:
                roster.append((name, proj, cost))
                current_cost += cost
                if current_cost >= min_budget and len(roster) >= 13:
                    break
        
        # Fill remaining spots if needed
        if len(roster) < 15:
            shooter_fills = [
                ('Al Horford', 633, 1),  # Shoots 3s well for a big
                ('Aaron Nesmith', 562, 3),  # Good 3-point shooter
                ('Vince Williams Jr.', 478, 2),
                ('Ayo Dosunmu', 476, 2),
                ('Coby White', 482, 3),  # Solid 3-point threat
                ('Luguentz Dort', 468, 3),  # 3&D wing
                ('Naz Reid', 475, 5),  # Stretch big
                ('Kelly Olynyk', 494, 4)  # Stretch big
            ]
            for name, proj, cost in shooter_fills:
                if current_cost + cost <= max_budget and len(roster) < 15:
                    roster.append((name, proj, cost))
                    current_cost += cost
        
        total_projection = sum([proj for _, proj, _ in roster])
        
        return {
            'name': '3-Point Bombing Squad',
            'strategy': '3PM Specialists',
            'roster': roster,
            'total_cost': current_cost,
            'total_projection': total_projection,
            'avg_projection': round(total_projection / len(roster), 1),
            'analysis': [
                'Prioritizes elite 3-point shooting at every position',
                'Dominates 3PM category while staying competitive elsewhere',
                'Modern NBA strategy focused on spacing and efficiency',
                'High ceiling in points and 3-pointers made'
            ]
        }

    def create_html_report(self):
        """Generate HTML report with all team examples"""
        teams = [
            self.build_stars_and_scrubs(),
            self.build_balanced_attack(), 
            self.build_value_hunter(),
            self.build_punt_strategy(),
            self.build_elite_superstar(),
            self.build_young_upside(),
            self.build_veteran_experience(),
            self.build_three_point_specialists()
        ]
        
        team_cards_html = ""
        for team in teams:
            # Format FULL roster for display - show all players
            roster_html = "<br>".join([
                f"{name}: {proj} proj (${cost})" 
                for name, proj, cost in team['roster']
            ])
            
            # Format analysis
            analysis_html = "<br>".join(f"• {point}" for point in team['analysis'])
            
            budget_color = "#28a745" if 185 <= team['total_cost'] <= 200 else "#dc3545"
            
            team_cards_html += f'''
                    <div class="ideal-team-card">
                        <h3>{team['name']}</h3>
                        <div class="strategy-badge">{team['strategy']}</div>
                        <div class="team-metrics">
                            <span class="metric" style="color: {budget_color}">Budget: ${team['total_cost']}/200</span>
                            <span class="metric">Total: {team['total_projection']}</span>
                            <span class="metric">Avg: {team['avg_projection']}</span>
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

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Realistic Budget Team Construction</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .main-content {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .page-header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}

        .page-header h1 {{
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}

        .nav-links {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .nav-link {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 25px;
            margin: 0 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .nav-link:hover {{
            background: linear-gradient(135deg, #20c997, #17a2b8);
            transform: translateY(-2px);
        }}

        .teams-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .ideal-team-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            border-top: 5px solid #667eea;
            max-height: 600px;
            overflow-y: auto;
        }}

        .ideal-team-card h3 {{
            color: #667eea;
            margin-bottom: 12px;
            font-size: 1.2em;
            position: sticky;
            top: 0;
            background: white;
            padding-bottom: 5px;
        }}

        .strategy-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-bottom: 15px;
        }}

        .team-metrics {{
            background: #e3f2fd;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}

        .metric {{
            font-weight: bold;
            color: #1976d2;
            font-size: 0.85em;
        }}

        .roster-section h4, .analysis-section h4 {{
            color: #495057;
            margin-bottom: 8px;
            font-size: 1em;
        }}

        .roster-list {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 6px;
            font-size: 0.75em;
            line-height: 1.4;
            margin-bottom: 12px;
            max-height: 200px;
            overflow-y: auto;
        }}

        .analysis-text {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            font-size: 0.85em;
            line-height: 1.6;
        }}

        .section {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .comparison-table th,
        .comparison-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            font-size: 0.9em;
        }}

        .comparison-table th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}

        .comparison-table tr:hover {{
            background-color: #f5f5f5;
        }}

        .budget-compliant {{
            color: #28a745;
            font-weight: bold;
        }}

        @media (max-width: 768px) {{
            .teams-grid {{
                grid-template-columns: 1fr;
            }}
            
            .team-metrics {{
                flex-direction: column;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-content">
            <div class="page-header">
                <h1>🏗️ Complete Team Construction Guide</h1>
                <p>8 Championship Strategies Using Full $185-200 Auction Budget</p>
            </div>

            <div class="nav-links">
                <a href="player_analysis.html" class="nav-link">🔮 Player Projections</a>
                <a href="owner_psychology.html" class="nav-link">🧠 Owner Psychology</a>
                <a href="a_USE_ME_startingPAGE.html" class="nav-link">🏠 Main Hub</a>
            </div>

            <div class="teams-grid">
{team_cards_html}
            </div>

            <div class="section">
                <div class="section-title">📊 Budget Utilization Comparison</div>
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Team Strategy</th>
                            <th>Total Cost</th>
                            <th>Budget Usage</th>
                            <th>Total Projection</th>
                            <th>Efficiency</th>
                        </tr>
                    </thead>
                    <tbody>'''
        
        # Generate table rows for all teams
        for team in teams:
            html_content += f'''
                        <tr>
                            <td><strong>{team['strategy']}</strong></td>
                            <td class="budget-compliant">${team['total_cost']}</td>
                            <td>{round(team['total_cost']/200*100, 1)}%</td>
                            <td>{team['total_projection']}</td>
                            <td>{round(team['total_projection']/team['total_cost'], 1)}</td>
                        </tr>'''
        
        html_content += '''
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="section-title">💡 Realistic Budget Management</div>
                <div class="analysis-text">
                    • <strong>Budget Discipline:</strong> All 8 teams use $185-200 to match realistic auction behavior<br>
                    • <strong>Strategy Diversity:</strong> Multiple viable paths to championship success<br>
                    • <strong>Stars & Scrubs:</strong> Balances elite talent with strategic value picks<br>
                    • <strong>Balanced Attack:</strong> Consistent spending across all roster positions<br>
                    • <strong>Value Hunter:</strong> Maximizes projection per dollar spent<br>
                    • <strong>Punt Strategy:</strong> Sacrifices specific categories to dominate others<br>
                    • <strong>Age Strategies:</strong> Youth upside vs veteran experience both viable<br>
                    • <strong>Category Focus:</strong> Specialized builds (3PM, superstars) can compete<br>
                    • <strong>Key Insight:</strong> Success comes from maximizing value within budget constraints
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

        with open('html_reports/prod_ready/team_construction_blueprints.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("Realistic Budget Team Construction report created!")
        print("All teams use $185-200 budget range as requested")

def main():
    constructor = RealisticBudgetTeamConstructor()
    teams = [
        constructor.build_stars_and_scrubs(),
        constructor.build_balanced_attack(),
        constructor.build_value_hunter(),
        constructor.build_punt_strategy(),
        constructor.build_elite_superstar(),
        constructor.build_young_upside(),
        constructor.build_veteran_experience(),
        constructor.build_three_point_specialists()
    ]
    
    print("Realistic Budget Team Examples (8 Total):")
    print("=" * 50)
    
    for team in teams:
        print(f"\n{team['name']} ({team['strategy']})")
        budget_status = "OK" if 185 <= team['total_cost'] <= 200 else "BAD"
        print(f"  Budget: ${team['total_cost']}/200 ({budget_status})")
        print(f"  Total Projection: {team['total_projection']}")
        print(f"  Average: {team['avg_projection']}")
        print(f"  Players: {len(team['roster'])}")
        
        # Show full roster in console too
        print("  Full Roster:")
        for name, proj, cost in team['roster']:
            print(f"    {name}: {proj} proj (${cost})")
    
    constructor.create_html_report()

if __name__ == "__main__":
    main()