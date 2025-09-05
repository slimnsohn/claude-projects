"""
Fixed odds extractor for Polymarket
Based on finding the 52% pattern in the HTML structure
"""

import requests
import json
import re
from typing import List, Dict, Optional

def extract_real_odds_from_polymarket(url: str) -> Optional[Dict]:
    """Extract the actual displayed odds from Polymarket page"""
    print(f"Extracting real odds from: {url}")
    
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        content = response.text
        
        # Method 1: Look for percentages in HTML elements (like the 52% we found)
        # Pattern: >XX%< or >XX.X%< where XX is the percentage
        html_percent_pattern = r'>(\d{1,2}(?:\.\d)?)\%<'
        html_percentages = re.findall(html_percent_pattern, content)
        
        print(f"HTML percentages found: {html_percentages}")
        
        # Method 2: Look for percentages in specific CSS classes (based on the pattern we saw)
        # The pattern was: class="...">52%</p>
        class_percent_pattern = r'class="[^"]*">\s*(\d{1,2}(?:\.\d)?)\%\s*</[^>]*>'
        class_percentages = re.findall(class_percent_pattern, content)
        
        print(f"CSS class percentages found: {class_percentages}")
        
        # Method 3: Look for the specific pattern we saw: css">XX%</p>
        specific_pattern = r'css">\s*(\d{1,2}(?:\.\d)?)\%\s*</p>'
        specific_percentages = re.findall(specific_pattern, content)
        
        print(f"Specific pattern percentages found: {specific_percentages}")
        
        # Method 4: Broader search for any percentage followed by closing tags
        broad_pattern = r'(\d{1,2}(?:\.\d)?)\%\s*</(?:p|span|div)'
        broad_percentages = re.findall(broad_pattern, content)
        
        print(f"Broad pattern percentages found: {broad_percentages}")
        
        # Combine all findings and filter for reasonable game odds (30-70%)
        all_percentages = []
        all_percentages.extend(html_percentages)
        all_percentages.extend(class_percentages)
        all_percentages.extend(specific_percentages)
        all_percentages.extend(broad_percentages)
        
        # Convert to floats and filter
        valid_percentages = []
        for p in all_percentages:
            try:
                val = float(p)
                if 30 <= val <= 70:  # Reasonable game odds range
                    valid_percentages.append(val)
            except:
                continue
        
        # Remove duplicates and sort
        unique_percentages = sorted(list(set(valid_percentages)))
        print(f"Valid unique percentages: {unique_percentages}")
        
        # Try to find the two main odds (should be complementary)
        if len(unique_percentages) >= 2:
            # Look for pairs that are reasonably close to adding up to 100%
            best_pair = None
            best_score = 0
            
            for i in range(len(unique_percentages)):
                for j in range(i+1, len(unique_percentages)):
                    p1, p2 = unique_percentages[i], unique_percentages[j]
                    total = p1 + p2
                    
                    # Score based on how close to 100% and how reasonable the individual odds are
                    if 90 <= total <= 110:  # Allow some margin for fees/vig
                        score = 100 - abs(100 - total)  # Higher score for closer to 100%
                        
                        if score > best_score:
                            best_score = score
                            best_pair = (p1, p2)
            
            if best_pair:
                p1, p2 = best_pair
                print(f"Best odds pair: {p1}% and {p2}% (total: {p1+p2}%)")
                
                return {
                    'url': url,
                    'odds_percentages': best_pair,
                    'total': p1 + p2,
                    'all_found': unique_percentages
                }
        
        # If no good pair found, return what we have
        return {
            'url': url,
            'odds_percentages': unique_percentages[:2] if len(unique_percentages) >= 2 else unique_percentages,
            'all_found': unique_percentages
        }
        
    except Exception as e:
        print(f"Error extracting odds: {e}")
        return None

def test_multiple_games_real_odds():
    """Test the fixed odds extraction on multiple games"""
    test_games = [
        {
            'url': 'https://polymarket.com/event/nfl-bal-buf-2025-09-07',
            'expected': 'Ravens 52%, Bills 49%'
        },
        {
            'url': 'https://polymarket.com/event/nfl-kc-lac-2025-09-05', 
            'expected': 'Should be closer to even than -400/+400'
        },
        {
            'url': 'https://polymarket.com/event/nfl-dal-phi-2025-09-04',
            'expected': 'Should be reasonable game odds'
        }
    ]
    
    print("TESTING FIXED ODDS EXTRACTION")
    print("=" * 80)
    
    results = []
    
    for game in test_games:
        print(f"\nTesting: {game['url']}")
        print(f"Expected: {game['expected']}")
        print("-" * 60)
        
        result = extract_real_odds_from_polymarket(game['url'])
        
        if result:
            odds = result.get('odds_percentages', [])
            if len(odds) == 2:
                p1, p2 = odds
                # Convert to American odds for comparison
                
                def percent_to_american_odds(percent):
                    decimal = percent / 100
                    if decimal >= 0.5:
                        return int(-decimal / (1 - decimal) * 100)
                    else:
                        return int((1 - decimal) / decimal * 100)
                
                odds1_american = percent_to_american_odds(p1)
                odds2_american = percent_to_american_odds(p2)
                
                print(f"FOUND: {p1}% ({odds1_american:+d}) vs {p2}% ({odds2_american:+d})")
                results.append(result)
            else:
                print(f"Found percentages but couldn't pair them: {odds}")
        else:
            print("Failed to extract odds")
    
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Successfully extracted odds from {len(results)}/{len(test_games)} games")
    
    return results

if __name__ == "__main__":
    test_multiple_games_real_odds()