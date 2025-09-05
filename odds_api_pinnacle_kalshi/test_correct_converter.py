#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'kalshi_converter'))

from converter import kalshi_cents_to_american_odds

# Test the key WSU/SDSU values
print("Testing WSU/SDSU values with correct converter:")
print("=" * 50)

wsu_cents = 53
sdsu_cents = 48

wsu_odds = kalshi_cents_to_american_odds(wsu_cents)
sdsu_odds = kalshi_cents_to_american_odds(sdsu_cents)

print(f"Washington St. {wsu_cents} cents -> {wsu_odds}")
print(f"San Diego St. {sdsu_cents} cents -> {sdsu_odds}")

# Test some edge cases
print("\nTesting edge cases:")
print("50 cents ->", kalshi_cents_to_american_odds(50))  # Even odds
print("49 cents ->", kalshi_cents_to_american_odds(49))  # Just under even
print("51 cents ->", kalshi_cents_to_american_odds(51))  # Just over even

# Test the return type
print(f"\nReturn types:")
print(f"53 cents returns: {type(wsu_odds)} = {repr(wsu_odds)}")
print(f"48 cents returns: {type(sdsu_odds)} = {repr(sdsu_odds)}")