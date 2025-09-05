"""
Test the specific Ravens-Bills game to understand the correct odds structure
URL: https://polymarket.com/event/nfl-bal-buf-2025-09-07 (should show 52%/49%)
"""

import requests
import json
import re

def test_ravens_bills():
    """Test the specific Ravens-Bills game"""
    url = "https://polymarket.com/event/nfl-bal-buf-2025-09-07"
    print(f"Testing Ravens-Bills game: {url}")
    print("Expected: Ravens 52%, Bills 49% (nearly even)")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to load page")
            return
        
        content = response.text
        print(f"Content length: {len(content)} characters")
        
        # Look for the specific percentages we expect (52% and 49%)
        print("\n1. Looking for expected percentages (52%, 49%)...")
        
        # Search for 52% and 49% specifically
        if "52%" in content and "49%" in content:
            print("SUCCESS: Found both 52% and 49% in content!")
        elif "52" in content and "49" in content:
            print("SUCCESS: Found both 52 and 49 numbers in content")
        else:
            print("ISSUE: Did not find expected percentages")
        
        # Extract all percentage-like patterns
        print("\n2. All percentage patterns found:")
        percent_patterns = [
            r'(\d{1,2}\.?\d?)%',  # Standard percentage
            r'(\d{1,2})\s*%',     # Percentage with space
            r'(\d{1,2}\.?\d?)\s*percent',  # Written out percent
        ]
        
        all_percentages = []
        for pattern in percent_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            all_percentages.extend(matches)
        
        # Convert to floats and show unique values
        unique_percentages = []
        for p in all_percentages:
            try:
                val = float(p)
                if 30 <= val <= 70:  # Reasonable game odds range
                    unique_percentages.append(val)
            except:
                continue
        
        unique_percentages = sorted(list(set(unique_percentages)))
        print(f"Reasonable percentages (30-70%): {unique_percentages}")
        
        # Look for team-specific odds
        print("\n3. Looking for team-specific odds patterns...")
        
        # Search for patterns like "Ravens 52%" or "BAL 52%"
        team_patterns = [
            r'(Ravens?|BAL)\s*:?\s*(\d{1,2}\.?\d?)%',
            r'(Bills?|BUF)\s*:?\s*(\d{1,2}\.?\d?)%',
            r'(\d{1,2}\.?\d?)%?\s*(Ravens?|BAL)',
            r'(\d{1,2}\.?\d?)%?\s*(Bills?|BUF)',
        ]
        
        team_odds = {}
        for pattern in team_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    team_or_num, num_or_team = match
                    try:
                        # Determine which is team and which is number
                        if any(name in team_or_num.upper() for name in ['RAVEN', 'BAL', 'BILL', 'BUF']):
                            team, num = team_or_num, float(num_or_team)
                        else:
                            num, team = float(team_or_num), num_or_team
                        
                        team_key = 'Ravens' if any(name in team.upper() for name in ['RAVEN', 'BAL']) else 'Bills'
                        if 30 <= num <= 70:
                            if team_key not in team_odds:
                                team_odds[team_key] = []
                            team_odds[team_key].append(num)
                    except:
                        continue
        
        print("Team-specific odds found:")
        for team, odds_list in team_odds.items():
            unique_odds = list(set(odds_list))
            print(f"  {team}: {unique_odds}")
        
        # Look for JSON data that might contain the odds
        print("\n4. Looking for JSON data with odds...")
        
        # Search for JSON objects that might contain market data
        json_patterns = [
            r'"price"\s*:\s*"?(\d+\.?\d*)"?',
            r'"percentage"\s*:\s*"?(\d+\.?\d*)"?',
            r'"probability"\s*:\s*"?(\d+\.?\d*)"?',
            r'"yes"\s*:\s*"?(\d+\.?\d*)"?',
            r'"no"\s*:\s*"?(\d+\.?\d*)"?',
        ]
        
        json_prices = []
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    val = float(match)
                    if 0.3 <= val <= 0.7:  # Decimal form
                        json_prices.append(val * 100)
                    elif 30 <= val <= 70:  # Percentage form
                        json_prices.append(val)
                except:
                    continue
        
        unique_json_prices = sorted(list(set(json_prices)))
        print(f"JSON prices found: {unique_json_prices}")
        
        # Look for specific context around 52 and 49
        print("\n5. Context around expected values...")
        
        for target in ['52', '49']:
            print(f"\nContext around '{target}':")
            # Find all occurrences and show surrounding text
            for match in re.finditer(rf'\b{target}\b', content):
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace('\n', ' ').replace('\t', ' ')
                # Clean up extra spaces
                context = re.sub(r'\s+', ' ', context)
                print(f"  ...{context}...")
        
        # Summary
        print(f"\n6. SUMMARY:")
        print(f"Expected: Ravens 52%, Bills 49%")
        print(f"Found percentages in range: {unique_percentages}")
        print(f"Team-specific odds: {team_odds}")
        
        if 52.0 in unique_percentages and 49.0 in unique_percentages:
            print("SUCCESS: Found both expected percentages!")
        elif any(abs(p - 52) < 2 for p in unique_percentages) and any(abs(p - 49) < 2 for p in unique_percentages):
            print("CLOSE: Found percentages close to expected values")
        else:
            print("ISSUE: Did not find expected percentages")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ravens_bills()