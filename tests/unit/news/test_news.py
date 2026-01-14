"""
Główny plik testowy dla modułu news
Agreguje wszystkie testy dla scraperów i funkcjonalności modułu news
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from tests.unit.news.test_kryminalki_scraper import TestKryminalekScraper
from tests.unit.news.test_policja_scraper import TestPolicjaScraper
from tests.unit.news.test_ekstraklasa_scraper import TestEkstraklasaScraper

def news_run_all_tests():
    """
    Funkcja uruchamiająca wszystkie testy modułu news
    """
    test_dir = os.path.dirname(__file__)
    pytest.main([test_dir, '-v', '--tb=short']) # -v to verbose, --tb=short to traceback short