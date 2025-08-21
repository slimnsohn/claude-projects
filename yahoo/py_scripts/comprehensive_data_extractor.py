"""
Comprehensive Yahoo Fantasy Data Extractor
==========================================

Extracts and organizes 15 years of Yahoo Fantasy League data
into our structured format for analysis.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from yahoo_oauth import OAuth2
import yahoo_fantasy_api

# League configuration
LEAGUE_KEYS = {
    '2010': '249.l.40919',
    '2011': '265.l.40720', 
    '2012': '304.l.62665',
    '2013': '322.l.90972',
    '2014': '342.l.129190',
    '2015': '353.l.93240',
    '2016': '364.l.90263',
    '2017': '375.l.111279',
    '2018': '385.l.42210',
    '2019': '395.l.98368',
    '2020': '402.l.121244',
    '2021': '410.l.124782',
    '2022': '418.l.104779',
    '2023': '428.l.32747',
    '2024': '454.l.44006'
}

class YahooDataExtractor:
    def __init__(self, base_path="C:/Users/sammy/Desktop/development/git/claude-projects/yahoo"):
        self.base_path = Path(base_path)
        self.league_data_path = self.base_path / "league_data"
        self.oauth = OAuth2(None, None, from_file='jsons/oauth2.json')
        self.extraction_log = []
        
    def log_message(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.extraction_log.append(log_entry)
    
    def extract_raw_data_for_year(self, year, league_key):
        """Extract all raw data from Yahoo API for a specific year"""
        self.log_message(f"Starting extraction for {year} ({league_key})")
        
        year_path = self.league_data_path / year
        raw_data_path = year_path / "raw_data"
        
        extracted_data = {
            'year': year,
            'league_key': league_key,
            'extraction_timestamp': datetime.now().isoformat(),
            'success': False,
            'errors': []
        }
        
        try:
            # Initialize league object
            league = yahoo_fantasy_api.league.League(self.oauth, league_key)
            
            # 1. League Settings
            try:
                settings = league.settings()
                with open(raw_data_path / "league_settings.json", 'w') as f:
                    json.dump(settings, f, indent=2, default=str)
                self.log_message(f"  SUCCESS: League settings extracted")
                extracted_data['league_name'] = settings.get('name', 'Unknown')
            except Exception as e:
                error_msg = f"Settings extraction failed: {str(e)}"
                self.log_message(f"  ERROR: {error_msg}")
                extracted_data['errors'].append(error_msg)
            
            # 2. Teams
            try:
                teams = league.teams()
                with open(raw_data_path / "teams.json", 'w') as f:
                    json.dump(teams, f, indent=2, default=str)
                self.log_message(f"  SUCCESS: Teams extracted ({len(teams)} teams)")
                extracted_data['num_teams'] = len(teams)
            except Exception as e:
                error_msg = f"Teams extraction failed: {str(e)}"
                self.log_message(f"  ERROR: {error_msg}")
                extracted_data['errors'].append(error_msg)
            
            # 3. Draft Results
            try:
                draft_results = league.draft_results()
                with open(raw_data_path / "draft_results.json", 'w') as f:
                    json.dump(draft_results, f, indent=2, default=str)
                self.log_message(f"  SUCCESS: Draft results extracted ({len(draft_results)} picks)")
                extracted_data['num_draft_picks'] = len(draft_results)
            except Exception as e:
                error_msg = f"Draft results extraction failed: {str(e)}"
                self.log_message(f"  ERROR: {error_msg}")
                extracted_data['errors'].append(error_msg)
            
            # 4. Standings
            try:
                standings = league.standings()
                with open(raw_data_path / "standings.json", 'w') as f:
                    json.dump(standings, f, indent=2, default=str)
                self.log_message(f"  SUCCESS: Standings extracted")
            except Exception as e:
                error_msg = f"Standings extraction failed: {str(e)}"
                self.log_message(f"  ERROR: {error_msg}")
                extracted_data['errors'].append(error_msg)
            
            # 5. Stat Categories
            try:
                stat_categories = league.stat_categories()
                with open(raw_data_path / "stat_categories.json", 'w') as f:
                    json.dump(stat_categories, f, indent=2, default=str)
                self.log_message(f"  SUCCESS: Stat categories extracted")
            except Exception as e:
                error_msg = f"Stat categories extraction failed: {str(e)}"
                self.log_message(f"  ERROR: {error_msg}")
                extracted_data['errors'].append(error_msg)
            
            # Mark as successful if we got core data
            if extracted_data['num_teams'] and extracted_data['num_draft_picks']:
                extracted_data['success'] = True
                self.log_message(f"  SUCCESS: {year} extraction completed successfully")
            else:
                self.log_message(f"  WARNING: {year} extraction incomplete")
            
        except Exception as e:
            error_msg = f"League initialization failed: {str(e)}"
            self.log_message(f"  ERROR: {error_msg}")
            extracted_data['errors'].append(error_msg)
        
        # Save extraction metadata
        with open(raw_data_path / "extraction_metadata.json", 'w') as f:
            json.dump(extracted_data, f, indent=2, default=str)
        
        return extracted_data
    
    def process_draft_data_for_year(self, year):
        """Process raw draft data into normalized format"""
        self.log_message(f"Processing draft data for {year}")
        
        year_path = self.league_data_path / year
        raw_data_path = year_path / "raw_data"
        processed_data_path = year_path / "processed_data"
        
        try:
            # Load raw data
            with open(raw_data_path / "draft_results.json", 'r') as f:
                draft_results = json.load(f)
            
            with open(raw_data_path / "teams.json", 'r') as f:
                teams = json.load(f)
            
            # Process draft picks
            processed_picks = []
            total_spending = 0
            
            for pick in draft_results:
                pick_number = pick.get('pick', 0)
                round_num = pick.get('round', 0)
                cost = pick.get('cost', 0)
                team_key = pick.get('team_key', '')
                player_id = pick.get('player_id', '')
                
                # Get team info
                team_info = teams.get(team_key, {})
                team_name = team_info.get('name', 'Unknown Team')
                
                # Create processed pick
                processed_pick = {
                    'pick_number': pick_number,
                    'round': round_num,
                    'player_id': str(player_id),
                    'team_key': team_key,
                    'fantasy_team': team_name,
                    'draft_cost': cost,
                    'raw_data': pick
                }
                
                processed_picks.append(processed_pick)
                total_spending += cost
            
            # Create processed draft analysis
            draft_analysis = {
                'season': year,
                'league_key': LEAGUE_KEYS[year],
                'total_picks': len(processed_picks),
                'total_spending': total_spending,
                'average_pick_cost': total_spending / len(processed_picks) if processed_picks else 0,
                'picks': processed_picks,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Save processed data
            with open(processed_data_path / "draft_analysis.json", 'w') as f:
                json.dump(draft_analysis, f, indent=2, default=str)
            
            self.log_message(f"  SUCCESS: Draft data processed for {year}")
            return True
            
        except Exception as e:
            self.log_message(f"  ERROR: Draft processing failed for {year}: {str(e)}")
            return False
    
    def process_owners_for_year(self, year):
        """Process owner data for a specific year"""
        self.log_message(f"Processing owner data for {year}")
        
        year_path = self.league_data_path / year
        raw_data_path = year_path / "raw_data"
        processed_data_path = year_path / "processed_data"
        
        try:
            # Load raw data
            with open(raw_data_path / "teams.json", 'r') as f:
                teams = json.load(f)
            
            with open(raw_data_path / "standings.json", 'r') as f:
                standings = json.load(f)
            
            # Process owners
            processed_owners = {}
            
            for team_key, team_data in teams.items():
                team_name = team_data.get('name', 'Unknown')
                
                # Extract manager info if available
                managers = team_data.get('managers', [])
                manager_info = None
                if managers:
                    manager_info = managers[0].get('manager', {})
                
                # Find standings info for this team
                team_standings = None
                for standing in standings:
                    if standing.get('team_key') == team_key:
                        team_standings = standing
                        break
                
                # Create owner record
                owner_record = {
                    'team_key': team_key,
                    'team_name': team_name,
                    'manager_info': manager_info,
                    'standings': team_standings,
                    'raw_team_data': team_data
                }
                
                # Use manager email as owner ID if available, otherwise team key
                owner_id = manager_info.get('email', team_key) if manager_info else team_key
                processed_owners[owner_id] = owner_record
            
            # Create processed owners file
            owners_data = {
                'season': year,
                'total_owners': len(processed_owners),
                'owners': processed_owners,
                'processing_timestamp': datetime.now().isoformat()
            }
            
            with open(processed_data_path / "owners.json", 'w') as f:
                json.dump(owners_data, f, indent=2, default=str)
            
            self.log_message(f"  SUCCESS: Owner data processed for {year}")
            return True
            
        except Exception as e:
            self.log_message(f"  ERROR: Owner processing failed for {year}: {str(e)}")
            return False
    
    def extract_all_years(self, start_year=None, end_year=None):
        """Extract data for all years (or specified range)"""
        self.log_message("Starting comprehensive data extraction")
        
        years_to_extract = list(LEAGUE_KEYS.keys())
        if start_year:
            years_to_extract = [y for y in years_to_extract if int(y) >= int(start_year)]
        if end_year:
            years_to_extract = [y for y in years_to_extract if int(y) <= int(end_year)]
        
        self.log_message(f"Extracting {len(years_to_extract)} years: {years_to_extract}")
        
        extraction_summary = {
            'total_years': len(years_to_extract),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'year_results': {}
        }
        
        for i, year in enumerate(years_to_extract):
            league_key = LEAGUE_KEYS[year]
            
            self.log_message(f"Processing year {i+1}/{len(years_to_extract)}: {year}")
            
            # Extract raw data
            extraction_result = self.extract_raw_data_for_year(year, league_key)
            
            if extraction_result['success']:
                extraction_summary['successful_extractions'] += 1
                
                # Process the data
                draft_success = self.process_draft_data_for_year(year)
                owner_success = self.process_owners_for_year(year)
                
                extraction_result['processing'] = {
                    'draft_processed': draft_success,
                    'owners_processed': owner_success
                }
            else:
                extraction_summary['failed_extractions'] += 1
            
            extraction_summary['year_results'][year] = extraction_result
            
            # Add delay between API calls to avoid rate limiting
            if i < len(years_to_extract) - 1:  # Don't delay after last iteration
                self.log_message("  Waiting 3 seconds before next extraction...")
                time.sleep(3)
        
        # Save extraction summary
        summary_path = self.league_data_path / "extraction_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(extraction_summary, f, indent=2, default=str)
        
        self.log_message(f"Extraction complete! {extraction_summary['successful_extractions']}/{extraction_summary['total_years']} years successful")
        
        return extraction_summary
    
    def save_extraction_log(self):
        """Save the extraction log"""
        log_path = self.league_data_path / "extraction_log.txt"
        with open(log_path, 'w') as f:
            f.write('\n'.join(self.extraction_log))
        print(f"Extraction log saved to: {log_path}")

def main():
    """Main execution function"""
    print("Yahoo Fantasy Data Extraction")
    print("=" * 50)
    
    extractor = YahooDataExtractor()
    
    # Extract all years (or specify range for testing)
    # For testing, you might want to start with just a few years:
    # summary = extractor.extract_all_years(start_year='2020', end_year='2024')
    
    # For full extraction:
    summary = extractor.extract_all_years()
    
    # Save the log
    extractor.save_extraction_log()
    
    print("\n" + "=" * 50)
    print("EXTRACTION SUMMARY:")
    print("=" * 50)
    print(f"Total years processed: {summary['total_years']}")
    print(f"Successful extractions: {summary['successful_extractions']}")
    print(f"Failed extractions: {summary['failed_extractions']}")
    
    if summary['failed_extractions'] > 0:
        print("\nFailed years:")
        for year, result in summary['year_results'].items():
            if not result['success']:
                print(f"  {year}: {result['errors']}")
    
    print(f"\nNext steps:")
    print(f"1. Review extraction results")
    print(f"2. Get external NBA player statistics")
    print(f"3. Build master owner tracking")
    print(f"4. Create analysis functions")

if __name__ == "__main__":
    main()