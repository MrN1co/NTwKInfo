"""Helpers for homepage logic that are pure Python and easy to unit-test.
These functions do not depend on Flask, HTTP, or DB and are suitable for unit tests.
"""
from datetime import datetime
from typing import List, Optional, Dict


def select_featured_article(news_list: List[Dict]) -> Optional[Dict]:
    """Return first article in the list or None when empty."""
    if not news_list:
        return None
    return news_list[0]


def summarize(text: Optional[str], max_len: int = 120) -> str:
    """Shorten text to max_len characters, add ellipsis when trimmed.
    Handles None gracefully.
    """
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def format_published_date(date_str: Optional[str]) -> str:
    """Try to parse common date formats (ISO or YYYY-MM-DD) and return "DD Mon YYYY".
    Returns empty string on failure.
    Not dependent on Flask or DB - unit-testable.
    """
    if not date_str:
        return ""
    try:
        # Try ISO first
        dt = datetime.fromisoformat(date_str)
    except Exception:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return ""
    return dt.strftime("%d %b %Y")
