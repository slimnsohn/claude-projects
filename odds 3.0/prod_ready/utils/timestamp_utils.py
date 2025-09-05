"""
Timestamp Utilities for Simplified Time Handling
Converts complex timestamps to simple HH:MM format
"""

from datetime import datetime, timezone
from typing import Optional

def simplify_timestamp(timestamp_str: str) -> Optional[str]:
    """
    Convert any timestamp format to simple HH:MM format
    
    Examples:
        2025-08-20T19:27:33.21516+00:00 -> "19:27"
        2025-08-20T14:30:00Z -> "14:30"
        2025-08-21T09:15:45-05:00 -> "09:15"
    
    Args:
        timestamp_str: Timestamp string in any ISO format
        
    Returns:
        Simple HH:MM string or None if parsing fails
    """
    if not timestamp_str:
        return None
    
    try:
        # Handle common timestamp formats
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        # Parse the datetime
        dt = datetime.fromisoformat(timestamp_str)
        
        # Convert to simple HH:MM format
        return dt.strftime('%H:%M')
        
    except Exception:
        # If parsing fails, try to extract time manually
        try:
            # Look for pattern like "T19:27" in the string
            if 'T' in timestamp_str:
                time_part = timestamp_str.split('T')[1]
                if ':' in time_part:
                    # Extract HH:MM
                    time_components = time_part.split(':')
                    if len(time_components) >= 2:
                        hour = time_components[0].zfill(2)
                        minute = time_components[1].zfill(2)
                        return f"{hour}:{minute}"
        except Exception:
            pass
        
        return None

def simplify_date(timestamp_str: str) -> Optional[str]:
    """
    Extract simple date (YYYY-MM-DD) from timestamp
    
    Args:
        timestamp_str: Timestamp string in any ISO format
        
    Returns:
        Simple YYYY-MM-DD string or None if parsing fails
    """
    if not timestamp_str:
        return None
    
    try:
        # Handle common timestamp formats
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        # Parse the datetime
        dt = datetime.fromisoformat(timestamp_str)
        
        # Convert to simple YYYY-MM-DD format
        return dt.strftime('%Y-%m-%d')
        
    except Exception:
        # If parsing fails, try to extract date manually
        try:
            # Look for pattern like "2025-08-20T" in the string
            if 'T' in timestamp_str:
                date_part = timestamp_str.split('T')[0]
                # Validate it looks like a date
                if len(date_part) == 10 and date_part.count('-') == 2:
                    return date_part
        except Exception:
            pass
        
        return None

def parse_game_time_safe(timestamp_str: str, min_buffer_minutes: int = 15) -> bool:
    """
    Safely check if a game is in the future with minimum buffer
    Uses simplified parsing to avoid timezone issues
    
    Args:
        timestamp_str: Game time string
        min_buffer_minutes: Minimum minutes before game starts
        
    Returns:
        True if game is far enough in the future, False otherwise
    """
    if not timestamp_str:
        return False
    
    try:
        # Handle common timestamp formats
        clean_timestamp = timestamp_str
        if clean_timestamp.endswith('Z'):
            clean_timestamp = clean_timestamp[:-1] + '+00:00'
        
        # Parse the datetime
        game_time = datetime.fromisoformat(clean_timestamp)
        if game_time.tzinfo is None:
            game_time = game_time.replace(tzinfo=timezone.utc)
        
        # Check if game is at least min_buffer_minutes in the future
        now = datetime.now(timezone.utc)
        time_until_game = game_time - now
        
        return time_until_game.total_seconds() > (min_buffer_minutes * 60)
        
    except Exception:
        # If parsing fails, assume it's live for safety
        return False

def format_display_time(timestamp_str: str) -> str:
    """
    Format timestamp for user display - simple and clean
    
    Args:
        timestamp_str: Any timestamp string
        
    Returns:
        Clean display format like "Aug 21, 19:27" or original string if parsing fails
    """
    if not timestamp_str:
        return "Unknown time"
    
    try:
        # Handle common timestamp formats
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        # Parse the datetime
        dt = datetime.fromisoformat(timestamp_str)
        
        # Format for display: "Aug 21, 19:27"
        return dt.strftime('%b %d, %H:%M')
        
    except Exception:
        # Extract what we can manually
        simple_time = simplify_timestamp(timestamp_str)
        simple_date = simplify_date(timestamp_str)
        
        if simple_date and simple_time:
            try:
                # Try to make date prettier
                date_obj = datetime.strptime(simple_date, '%Y-%m-%d')
                pretty_date = date_obj.strftime('%b %d')
                return f"{pretty_date}, {simple_time}"
            except:
                return f"{simple_date} {simple_time}"
        elif simple_time:
            return simple_time
        else:
            return timestamp_str

# Test the functions
if __name__ == "__main__":
    test_timestamps = [
        "2025-08-20T19:27:33.21516+00:00",
        "2025-08-20T14:30:00Z", 
        "2025-08-21T09:15:45-05:00",
        "2025-08-21T17:11:00Z"
    ]
    
    print("TIMESTAMP UTILITY TESTS:")
    print("=" * 50)
    
    for ts in test_timestamps:
        simple_time = simplify_timestamp(ts)
        simple_date = simplify_date(ts)
        display_time = format_display_time(ts)
        is_future = parse_game_time_safe(ts, 15)
        
        print(f"Original: {ts}")
        print(f"  Time: {simple_time}")
        print(f"  Date: {simple_date}")
        print(f"  Display: {display_time}")
        print(f"  Future (15min): {is_future}")
        print()