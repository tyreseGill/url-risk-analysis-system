from datetime import datetime as dt
from datetime import timezone as tz
from functools import lru_cache

import whois


@lru_cache(maxsize=100)
def query_url(url: str) -> dict:
    """
    Performs a WHOIS lookup on the provided URL.

    Returns:
        dict: Collection of details associated with the URL.
    """
    try:
        query = whois.whois(url)
    except Exception:
        return None
    return query


def normalize_expiration_date (exp: dt) -> dt:
    """
    Ensures a single expiration date is obtained whether a domain has one or multiple such dates.

    Returns:
        Datetime object representing earliest expiration date.
    """
    # Gets earliest expiration date if multiple exist
    if isinstance(exp, list):
        exp = min(exp)
    
    # Converts expiration date to standard timezone for comparison
    exp = exp.astimezone(tz.utc)

    return exp


def query_exists(url: str, query: dict) -> bool:
    """
    Verifies if a Whois query for a URL was successful.

    Args:
        url: The URL that was queried.
        query: Dictionary object representing Whois data.

    Returns:
        bool: False, if all query attributes are null. Otherwise, True.
    """
    if not query or not isinstance(query, dict) or all(attr is None for attr in query.values()):
        print(f'\nERROR: No matches were found for "{url}". '
            'Make sure you have a stable internet connection and that any VPNs are off before you try again.\n')
        return False
    return True
