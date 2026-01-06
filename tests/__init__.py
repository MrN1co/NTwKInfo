"""
Uruchamianie testów przy starcie aplikacji
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


def run_tests():
    """
    Uruchamia testy
    """
    #wiadomości
    from modules.news.tests.test_news import news_run_all_tests
    news_run_all_tests()
    #ekonomia
    # ...
    #pogoda
    # ...
    #inne
    # ...

