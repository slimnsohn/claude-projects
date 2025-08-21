"""
Extract data from the 5 confirmed working years (2020-2024)
"""

from comprehensive_data_extractor import YahooDataExtractor

def main():
    print("Extracting Data from 5 Confirmed Working Years")
    print("=" * 60)
    
    extractor = YahooDataExtractor()
    
    # Extract from the 5 confirmed working years
    summary = extractor.extract_all_years(start_year='2020', end_year='2024')
    
    # Save the log
    extractor.save_extraction_log()
    
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY (2020-2024):")
    print("=" * 60)
    print(f"Total years processed: {summary['total_years']}")
    print(f"Successful extractions: {summary['successful_extractions']}")
    print(f"Failed extractions: {summary['failed_extractions']}")
    
    print(f"\nDetailed Results:")
    for year in ['2020', '2021', '2022', '2023', '2024']:
        if year in summary['year_results']:
            result = summary['year_results'][year]
            status = "SUCCESS" if result['success'] else "FAILED"
            teams = result.get('num_teams', 0)
            picks = result.get('num_draft_picks', 0)
            print(f"  {year}: {status} - {teams} teams, {picks} picks")
            
            if result.get('processing'):
                proc = result['processing']
                draft_ok = "✓" if proc['draft_processed'] else "✗"
                owner_ok = "✓" if proc['owners_processed'] else "✗"
                print(f"        Processing: Draft {draft_ok}, Owners {owner_ok}")
    
    if summary['successful_extractions'] >= 3:
        print(f"\n🎉 SUCCESS! {summary['successful_extractions']} years extracted successfully.")
        print(f"📁 Check the league_data folder for organized data.")
        print(f"📊 Ready to proceed with:")
        print(f"   1. External NBA stats integration")
        print(f"   2. Master owner tracking")
        print(f"   3. Analysis and HTML reports")
        
        print(f"\n📋 Next step: Expand to remaining years (2010-2019)")
    else:
        print(f"\n⚠️  Only {summary['successful_extractions']} years successful.")
        print(f"   Review errors and retry if needed.")

if __name__ == "__main__":
    main()