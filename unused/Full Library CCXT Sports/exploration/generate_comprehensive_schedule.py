#!/usr/bin/env python3
"""
Generate comprehensive NFL schedule data for 2024 season
Creates a realistic schedule with multiple weeks of games and varied dates.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# NFL teams by division for realistic matchups
AFC_EAST = ['BUF', 'MIA', 'NE', 'NYJ']
AFC_NORTH = ['BAL', 'CIN', 'CLE', 'PIT']
AFC_SOUTH = ['HOU', 'IND', 'JAX', 'TEN']
AFC_WEST = ['DEN', 'KC', 'LV', 'LAC']

NFC_EAST = ['DAL', 'NYG', 'PHI', 'WAS']
NFC_NORTH = ['CHI', 'DET', 'GB', 'MIN']
NFC_SOUTH = ['ATL', 'CAR', 'NO', 'TB']
NFC_WEST = ['ARI', 'LAR', 'SF', 'SEA']

ALL_TEAMS = AFC_EAST + AFC_NORTH + AFC_SOUTH + AFC_WEST + NFC_EAST + NFC_NORTH + NFC_SOUTH + NFC_WEST

def generate_week_games(week_num, start_date):
    """Generate games for a specific week"""
    games = []
    
    # Week 1 - Season opener patterns
    if week_num == 1:
        matchups = [
            ('BAL', 'KC'),  # Thursday night opener
            ('GB', 'PHI'),  # Friday night international
            ('ATL', 'PIT'), ('ARI', 'BUF'), ('CHI', 'TEN'), ('CIN', 'NE'),
            ('CLE', 'DAL'), ('HOU', 'IND'), ('JAX', 'MIA'), ('LAC', 'LV'),
            ('MIN', 'NYG'), ('NO', 'CAR'), ('SEA', 'DEN'), ('TB', 'WAS'),
            ('SF', 'NYJ'),  # Monday night
            ('DET', 'LAR')  # Sunday night
        ]
        game_times = {
            0: ('2024-09-05', '20:20', 'NBC', True),   # Thursday
            1: ('2024-09-06', '20:15', 'NBC', True),   # Friday
            2: ('2024-09-08', '13:00', 'CBS', False),  # Sunday 1pm slot
            3: ('2024-09-08', '13:00', 'FOX', False),
            4: ('2024-09-08', '13:00', 'CBS', False),
            5: ('2024-09-08', '13:00', 'FOX', False),
            6: ('2024-09-08', '13:00', 'CBS', False),
            7: ('2024-09-08', '16:25', 'CBS', False),  # Sunday 4pm slot
            8: ('2024-09-08', '16:25', 'FOX', False),
            9: ('2024-09-08', '16:25', 'CBS', False),
            10: ('2024-09-08', '16:25', 'FOX', False),
            11: ('2024-09-08', '16:25', 'CBS', False),
            12: ('2024-09-08', '16:25', 'FOX', False),
            13: ('2024-09-08', '20:20', 'NBC', True),  # Sunday night
            14: ('2024-09-09', '20:15', 'ESPN', True), # Monday night
            15: ('2024-09-09', '20:15', 'ABC', True)   # Monday double-header
        }
    
    # Week 2 - Regular patterns
    elif week_num == 2:
        matchups = [
            ('BUF', 'MIA'),  # Thursday night
            ('PHI', 'WAS'), ('DAL', 'NO'), ('LAC', 'CAR'), ('NYG', 'ARI'),
            ('IND', 'GB'), ('SF', 'MIN'), ('SEA', 'NE'), ('DEN', 'PIT'),
            ('LV', 'BAL'), ('TB', 'DET'), ('CLE', 'JAX'), ('TEN', 'NYJ'),
            ('KC', 'CIN'),  # Sunday night
            ('CHI', 'HOU'), ('ATL', 'LAR')  # Monday double-header
        ]
        game_times = {
            0: ('2024-09-12', '20:15', 'Prime', True),   # Thursday
            1: ('2024-09-15', '13:00', 'FOX', False),     # Sunday 1pm
            2: ('2024-09-15', '13:00', 'CBS', False),
            3: ('2024-09-15', '13:00', 'FOX', False),
            4: ('2024-09-15', '13:00', 'CBS', False),
            5: ('2024-09-15', '13:00', 'FOX', False),
            6: ('2024-09-15', '16:05', 'CBS', False),     # Sunday 4pm
            7: ('2024-09-15', '16:05', 'FOX', False),
            8: ('2024-09-15', '16:25', 'CBS', False),
            9: ('2024-09-15', '16:25', 'FOX', False),
            10: ('2024-09-15', '16:25', 'CBS', False),
            11: ('2024-09-15', '16:25', 'FOX', False),
            12: ('2024-09-15', '16:25', 'CBS', False),
            13: ('2024-09-15', '20:20', 'NBC', True),     # Sunday night
            14: ('2024-09-16', '20:15', 'ESPN', True),    # Monday night
            15: ('2024-09-16', '20:30', 'ABC', True)      # Monday late
        }
    
    # Week 3
    elif week_num == 3:
        matchups = [
            ('NYJ', 'NE'),   # Thursday divisional
            ('LAR', 'SF'), ('MIA', 'SEA'), ('DEN', 'TB'), ('HOU', 'MIN'),
            ('NO', 'PHI'), ('CAR', 'LV'), ('CHI', 'IND'), ('GB', 'TEN'),
            ('CLE', 'NYG'), ('WAS', 'CIN'), ('ATL', 'KC'), ('PIT', 'LAC'),
            ('DAL', 'BAL'),  # Sunday night
            ('ARI', 'DET'), ('JAX', 'BUF')  # Monday
        ]
        game_times = {
            0: ('2024-09-19', '20:15', 'Prime', True),
            1: ('2024-09-22', '13:00', 'FOX', False),
            2: ('2024-09-22', '13:00', 'CBS', False),
            3: ('2024-09-22', '13:00', 'FOX', False),
            4: ('2024-09-22', '13:00', 'CBS', False),
            5: ('2024-09-22', '13:00', 'FOX', False),
            6: ('2024-09-22', '16:05', 'CBS', False),
            7: ('2024-09-22', '16:05', 'FOX', False),
            8: ('2024-09-22', '16:25', 'CBS', False),
            9: ('2024-09-22', '16:25', 'FOX', False),
            10: ('2024-09-22', '16:25', 'CBS', False),
            11: ('2024-09-22', '16:25', 'FOX', False),
            12: ('2024-09-22', '16:25', 'CBS', False),
            13: ('2024-09-22', '20:20', 'NBC', True),
            14: ('2024-09-23', '20:15', 'ESPN', True),
            15: ('2024-09-23', '20:30', 'ABC', True)
        }
    
    # Week 4 
    elif week_num == 4:
        matchups = [
            ('DAL', 'NYG'),  # Thursday divisional rivalry
            ('MIN', 'GB'), ('ATL', 'NO'), ('BUF', 'BAL'), ('CIN', 'CAR'),
            ('IND', 'PIT'), ('LAR', 'CHI'), ('NE', 'SF'), ('TEN', 'MIA'),
            ('DEN', 'NYJ'), ('JAX', 'HOU'), ('WAS', 'ARI'), ('TB', 'PHI'),
            ('KC', 'LAC'),   # Sunday night
            ('SEA', 'DET'), ('CLE', 'LV')  # Monday
        ]
        game_times = {
            0: ('2024-09-26', '20:15', 'Prime', True),
            1: ('2024-09-29', '13:00', 'FOX', False),
            2: ('2024-09-29', '13:00', 'CBS', False),
            3: ('2024-09-29', '13:00', 'FOX', False),
            4: ('2024-09-29', '13:00', 'CBS', False),
            5: ('2024-09-29', '13:00', 'FOX', False),
            6: ('2024-09-29', '16:05', 'CBS', False),
            7: ('2024-09-29', '16:05', 'FOX', False),
            8: ('2024-09-29', '16:25', 'CBS', False),
            9: ('2024-09-29', '16:25', 'FOX', False),
            10: ('2024-09-29', '16:25', 'CBS', False),
            11: ('2024-09-29', '16:25', 'FOX', False),
            12: ('2024-09-29', '16:25', 'CBS', False),
            13: ('2024-09-29', '20:20', 'NBC', True),
            14: ('2024-09-30', '20:15', 'ESPN', True),
            15: ('2024-09-30', '20:30', 'ABC', True)
        }
    
    # Week 5 with some bye weeks (reduced games)
    elif week_num == 5:
        matchups = [
            ('TB', 'ATL'),   # Thursday divisional
            ('JAX', 'IND'), ('CAR', 'CHI'), ('BAL', 'CIN'), ('BUF', 'HOU'),
            ('MIA', 'NE'), ('CLE', 'WAS'), ('LAR', 'GB'), ('ARI', 'SF'),
            ('DEN', 'LV'), ('MIN', 'NYJ'), ('DAL', 'PIT'),
            ('KC', 'NO'),    # Monday night
        # Some teams on bye: NYG, PHI, TEN, SEA, DET, LAC
        ]
        game_times = {
            0: ('2024-10-03', '20:15', 'Prime', True),
            1: ('2024-10-06', '13:00', 'CBS', False),
            2: ('2024-10-06', '13:00', 'FOX', False),
            3: ('2024-10-06', '13:00', 'CBS', False),
            4: ('2024-10-06', '13:00', 'FOX', False),
            5: ('2024-10-06', '13:00', 'CBS', False),
            6: ('2024-10-06', '16:05', 'FOX', False),
            7: ('2024-10-06', '16:25', 'CBS', False),
            8: ('2024-10-06', '16:25', 'FOX', False),
            9: ('2024-10-06', '16:25', 'CBS', False),
            10: ('2024-10-06', '20:20', 'NBC', True),
            11: ('2024-10-07', '20:15', 'ESPN', True),
            12: ('2024-10-07', '20:30', 'ABC', True),
        }
    
    else:
        # Default pattern for other weeks
        matchups = [
            ('KC', 'BAL'), ('SF', 'DAL'), ('BUF', 'MIA'), ('GB', 'CHI'),
        ]
        game_times = {
            0: (f'2024-{9 + week_num//4}-{5 + (week_num * 7) % 25:02d}', '13:00', 'CBS', False),
            1: (f'2024-{9 + week_num//4}-{5 + (week_num * 7) % 25:02d}', '16:25', 'FOX', False),
            2: (f'2024-{9 + week_num//4}-{6 + (week_num * 7) % 25:02d}', '13:00', 'CBS', False),
            3: (f'2024-{9 + week_num//4}-{6 + (week_num * 7) % 25:02d}', '20:20', 'NBC', True),
        }
    
    # Create game objects
    for i, (away, home) in enumerate(matchups):
        if i in game_times:
            game_date, game_time, network, is_prime = game_times[i]
            
            # Determine venue (simplified - using team city mapping)
            venue_map = {
                'KC': 'Arrowhead Stadium', 'BAL': 'M&T Bank Stadium', 'BUF': 'Highmark Stadium',
                'MIA': 'Hard Rock Stadium', 'NE': 'Gillette Stadium', 'NYJ': 'MetLife Stadium',
                'CIN': 'Paycor Stadium', 'CLE': 'Cleveland Browns Stadium', 'PIT': 'Heinz Field',
                'HOU': 'NRG Stadium', 'IND': 'Lucas Oil Stadium', 'JAX': 'TIAA Bank Field',
                'TEN': 'Nissan Stadium', 'DEN': 'Empower Field', 'LV': 'Allegiant Stadium',
                'LAC': 'SoFi Stadium', 'DAL': 'AT&T Stadium', 'NYG': 'MetLife Stadium',
                'PHI': 'Lincoln Financial Field', 'WAS': 'FedExField', 'CHI': 'Soldier Field',
                'DET': 'Ford Field', 'GB': 'Lambeau Field', 'MIN': 'U.S. Bank Stadium',
                'ATL': 'Mercedes-Benz Stadium', 'CAR': 'Bank of America Stadium',
                'NO': 'Caesars Superdome', 'TB': 'Raymond James Stadium',
                'ARI': 'State Farm Stadium', 'LAR': 'SoFi Stadium', 'SF': 'Levi\'s Stadium',
                'SEA': 'Lumen Field'
            }
            
            game = {
                'game_id': f'2024_week{week_num}_{away.lower()}_{home.lower()}',
                'week': week_num,
                'season': 2024,
                'game_date': f'{game_date}T{game_time}:00',
                'home_team': home,
                'away_team': away,
                'game_time': game_time,
                'status': 'scheduled' if week_num >= 1 else 'final',
                'tv_network': network,
                'is_playoff': False,
                'is_prime_time': is_prime,
                'venue': venue_map.get(home, f'{home} Stadium')
            }
            games.append(game)
    
    return games

def main():
    """Generate comprehensive NFL schedule"""
    print("Generating comprehensive NFL 2024 schedule...")
    
    all_games = []
    weeks_to_generate = [1, 2, 3, 4, 5]  # First 5 weeks
    
    for week in weeks_to_generate:
        week_games = generate_week_games(week, None)
        all_games.extend(week_games)
        print(f"Week {week}: {len(week_games)} games")
    
    # Create comprehensive schedule data
    schedule_data = {
        'season': '2024',
        'last_updated': datetime.now().isoformat(),
        'total_weeks': len(weeks_to_generate),
        'total_games': len(all_games),
        'games': all_games
    }
    
    # Save to file
    output_path = Path(__file__).parent / 'nfl_schedule_2024_comprehensive.json'
    with open(output_path, 'w') as f:
        json.dump(schedule_data, f, indent=2)
    
    print(f"\nComprehensive schedule generated!")
    print(f"Total games: {len(all_games)}")
    print(f"Weeks covered: {weeks_to_generate}")
    
    # Analyze date coverage
    dates = set(game['game_date'][:10] for game in all_games)
    print(f"Unique dates: {len(dates)}")
    print(f"Date range: {min(dates)} to {max(dates)}")
    
    # Show sample games
    print(f"\nSample games:")
    for game in all_games[:5]:
        print(f"  Week {game['week']}: {game['away_team']} @ {game['home_team']} - {game['game_date']}")
    
    print(f"\nSaved to: {output_path}")

if __name__ == '__main__':
    main()