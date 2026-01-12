import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
from modules.main.helpers import select_featured_article, summarize, format_published_date


class TestHelpers:
    def test_select_featured_with_items(self):
        items = [{'title': 'A'}, {'title': 'B'}]
        assert select_featured_article(items) == items[0]

    def test_select_featured_empty(self):
        assert select_featured_article([]) is None

    def test_summarize_short(self):
        s = 'short text'
        assert summarize(s, max_len=20) == s

    def test_summarize_trim(self):
        s = 'x' * 50
        out = summarize(s, max_len=10)
        assert len(out) <= 10 and out.endswith('...')

    def test_format_published_iso(self):
        assert format_published_date('2024-12-05T14:30:00') == '05 Dec 2024'

    def test_format_published_simple(self):
        assert format_published_date('2023-01-02') == '02 Jan 2023'

    def test_format_published_invalid(self):
        assert format_published_date('not a date') == ''
