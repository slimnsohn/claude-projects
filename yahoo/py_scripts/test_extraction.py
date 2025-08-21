"""
Test extraction for a few years first
"""

from comprehensive_data_extractor import YahooDataExtractor

def main():
    print("Testing Data Extraction with 3 years")
    print("=" * 50)
    
    extractor = YahooDataExtractor()
    
    # Test with just 3 years first
    summary = extractor.extract_all_years(start_year='2020', end_year='2022')
    
    # Save the log
    extractor.save_extraction_log()
    
    print("\n" + "=" * 50)
    print("TEST EXTRACTION SUMMARY:")
    print("=" * 50)
    print(f"Total years processed: {summary['total_years']}")
    print(f"Successful extractions: {summary['successful_extractions']}")
    print(f"Failed extractions: {summary['failed_extractions']}")
    
    if summary['successful_extractions'] > 0:
        print("\nSuccessful years:")
        for year, result in summary['year_results'].items():
            if result['success']:
                print(f"  {year}: {result.get('num_teams', 0)} teams, {result.get('num_draft_picks', 0)} picks")

if __name__ == "__main__":
    main()