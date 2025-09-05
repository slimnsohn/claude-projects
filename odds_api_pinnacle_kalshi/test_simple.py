#!/usr/bin/env python3

def kalshi_cents_to_american(cents: int) -> int:
    if cents <= 0:
        cents = 1
    elif cents >= 100:
        cents = 99
    
    win_amount = 100 - cents
    
    if cents >= 50:
        american_odds = -int((cents / win_amount) * 100)
    else:
        american_odds = int((win_amount / cents) * 100)
    
    return american_odds

# Test the key values
print("53 cents ->", kalshi_cents_to_american(53))  # Should be ~-113
print("48 cents ->", kalshi_cents_to_american(48))  # Should be ~+108