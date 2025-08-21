"""
Extract data from remaining 10 years (2010-2019)
"""

from comprehensive_data_extractor import YahooDataExtractor

def main():
    print("Extracting Data from Remaining 10 Years (2010-2019)")
    print("=" * 70)
    
    extractor = YahooDataExtractor()
    
    # Extract from the remaining years
    summary = extractor.extract_all_years(start_year='2010', end_year='2019')
    
    # Save the log
    extractor.save_extraction_log()
    
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY (2010-2019):")
    print("=" * 70)
    print(f"Total years processed: {summary['total_years']}")
    print(f"Successful extractions: {summary['successful_extractions']}")
    print(f"Failed extractions: {summary['failed_extractions']}")
    
    print(f"\nDetailed Results:")
    for year in ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']:
        if year in summary['year_results']:
            result = summary['year_results'][year]
            status = "SUCCESS" if result['success'] else "FAILED"
            teams = result.get('num_teams', 0)
            picks = result.get('num_draft_picks', 0)
            print(f"  {year}: {status} - {teams} teams, {picks} picks")
            
            if not result['success'] and result.get('errors'):
                print(f"        Errors: {result['errors'][:2]}")  # Show first 2 errors
    
    print(f"\n📊 FINAL TOTALS:")
    
    # Calculate totals from all years now
    total_extracted = summary['successful_extractions']
    
    # Add the 5 we already have
    total_with_previous = total_extracted + 5
    
    print(f"   Previously extracted: 5 years (2020-2024)")
    print(f"   Just extracted: {total_extracted} years (2010-2019)")
    print(f"   TOTAL AVAILABLE: {total_with_previous} years")
    
    if total_with_previous >= 10:
        print(f"\n🎉 EXCELLENT! {total_with_previous}/15 years successfully extracted!")
        print(f"📁 Ready for comprehensive 15-year analysis")
    else:
        print(f"\n⚠️  Only {total_with_previous}/15 years available")
        print(f"   May need to investigate failed extractions")

if __name__ == "__main__":
    main()