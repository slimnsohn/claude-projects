def kalshi_cents_to_american_odds(cents):
    """
    Convert Kalshi cents (1-99) to American-style odds using flat lookup table.
    
    Parameters:
    -----------
    cents : int or float
        The Kalshi contract price in cents (1-99)
    
    Returns:
    --------
    str
        American odds in the format '+XXX' or '-XXX'
    """
    
    # Input validation
    if not isinstance(cents, (int, float)):
        raise TypeError("Cents must be a number")
    
    if cents < 1 or cents > 99:
        raise ValueError("Cents must be between 1 and 99")
    
    # Convert to integer if float
    cents = int(round(cents))
    
    # Flat lookup table from provided data
    CENTS_TO_ODDS = {
        1: "+9253", 2: "+4573", 3: "+3015", 4: "+2243", 5: "+1773",
        6: "+1463", 7: "+1241", 8: "+1074", 9: "+945", 10: "+841",
        11: "+756", 12: "+685", 13: "+625", 14: "+574", 15: "+529",
        16: "+490", 17: "+456", 18: "+425", 19: "+398", 20: "+373",
        21: "+351", 22: "+331", 23: "+312", 24: "+295", 25: "+280",
        26: "+265", 27: "+252", 28: "+240", 29: "+228", 30: "+217",
        31: "+207", 32: "+198", 33: "+189", 34: "+181", 35: "+173",
        36: "+166", 37: "+159", 38: "+152", 39: "+146", 40: "+140",
        41: "+134", 42: "+129", 43: "+123", 44: "+119", 45: "+114",
        46: "+109", 47: "+105", 48: "+101", 49: "-103", 50: "-107",
        51: "-112", 52: "-116", 53: "-121", 54: "-126", 55: "-131",
        56: "-137", 57: "-142", 58: "-148", 59: "-154", 60: "-161",
        61: "-168", 62: "-175", 63: "-182", 64: "-191", 65: "-199",
        66: "-208", 67: "-218", 68: "-228", 69: "-238", 70: "-250",
        71: "-262", 72: "-276", 73: "-290", 74: "-305", 75: "-321",
        76: "-339", 77: "-358", 78: "-379", 79: "-402", 80: "-427",
        81: "-456", 82: "-487", 83: "-522", 84: "-561", 85: "-606",
        86: "-658", 87: "-719", 88: "-792", 89: "-881", 90: "-991",
        91: "-1133", 92: "-1316", 93: "-1559", 94: "-1898", 95: "-2396",
        96: "-3169", 97: "-4279", 98: "-5151", 99: "-9901"
    }
    
    return CENTS_TO_ODDS[cents]


def create_conversion_table():
    """
    Generate a complete conversion table from Kalshi cents to American odds.
    
    Returns:
    --------
    dict
        Dictionary mapping cents (1-99) to American odds
    """
    conversion_table = {}
    
    for cents in range(1, 100):
        conversion_table[cents] = kalshi_cents_to_american_odds(cents)
    
    return conversion_table


def display_conversion_table(start=1, end=99):
    """
    Display a formatted conversion table for a range of cent values.
    
    Parameters:
    -----------
    start : int
        Starting cent value (default: 1)
    end : int
        Ending cent value (default: 99)
    """
    print(f"{'Cents':<8}{'American Odds':<15}{'Implied Prob':<15}")
    print("-" * 38)
    
    for cents in range(start, min(end + 1, 100)):
        american_odds = kalshi_cents_to_american_odds(cents)
        implied_prob = f"{cents}%"
        print(f"{cents}¢{' '*(6-len(str(cents)))}{american_odds:<15}{implied_prob:<15}")


# Example usage and verification
if __name__ == "__main__":
    # Test some key values from your table
    test_values = {
        1: "+9900",
        5: "+1900", 
        10: "+900",
        20: "+300",
        25: "+300",  # Note: This should be +300, not +280 as in your table
        33: "+203",  # Should be +203, not +189
        40: "+150",
        49: "+104",
        50: "-100",  # Even odds
        51: "-104",
        60: "-150",
        75: "-300",
        80: "-400",
        90: "-900",
        95: "-1900",
        99: "-9900"
    }
    
    print("Verification of key conversions:")
    print("=" * 40)
    for cents, expected in test_values.items():
        calculated = kalshi_cents_to_american_odds(cents)
        status = "✓" if calculated == expected else "✗"
        print(f"{cents}¢ → {calculated} (expected: {expected}) {status}")
    
    print("\n" + "=" * 40)
    print("Sample conversion table (1-20 cents):")
    print("=" * 40)
    display_conversion_table(1, 20)
    
    print("\n" + "=" * 40)
    print("Sample conversion table (45-55 cents):")
    print("=" * 40)
    display_conversion_table(45, 55)
    
    print("\n" + "=" * 40)
    print("Sample conversion table (80-99 cents):")
    print("=" * 40)
    display_conversion_table(80, 99)