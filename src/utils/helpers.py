"""
Placeholder for utility functions
"""

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def get_human_readable_timedelta(days: int) -> str:
    """Convert days to human readable format"""
    if days < 0:
        return f"{abs(days)} days overdue"
    elif days == 0:
        return "Today"
    elif days == 1:
        return "Tomorrow"
    else:
        return f"In {days} days"
