#!/usr/bin/env python3

"""
Test the cents to American odds conversion
"""

def kalshi_cents_to_american(cents: int) -> int:
    """Convert Kalshi ask price cents (0-100) to American odds - simple direct conversion"""
    if cents <= 0:
        cents = 1
    elif cents >= 100:
        cents = 99
    
    # Kalshi pricing: You pay 'cents', win (100-cents) if correct
    # Direct conversion to American odds without fee adjustments
    
    win_amount = 100 - cents
    
    if cents >= 50:
        # Favorite: negative odds
        # American odds = -(amount_to_win / amount_to_bet) * 100
        american_odds = -int((cents / win_amount) * 100)
    else:
        # Underdog: positive odds  
        # American odds = (amount_to_win / amount_to_bet) * 100
        american_odds = int((win_amount / cents) * 100)
    
    return american_odds

def test_conversions():
    """Test specific conversions"""
    
    test_cases = [
        (53, "Washington St. (expected ~-113)"),
        (48, "San Diego St. (expected ~+108)"),
        (50, "Even odds (expected -100)"),
        (75, "Heavy favorite"),
        (25, "Heavy underdog")
    ]
    
    print("KALSHI CENTS TO AMERICAN ODDS CONVERSION:")
    print("=" * 50)
    
    for cents, description in test_cases:
        odds = kalshi_cents_to_american(cents)
        win_amount = 100 - cents
        
        print(f"{cents}¢ -> {odds:+4d} ({description})")
        print(f"    Pay {cents}¢, win {win_amount}¢ if correct")
        
        # Verify the math
        if cents >= 50:
            expected = -int((cents / win_amount) * 100)
        else:
            expected = int((win_amount / cents) * 100)
        
        print(f"    Math check: {expected} {'✓' if odds == expected else '✗'}")
        print()

if __name__ == "__main__":
    test_conversions()