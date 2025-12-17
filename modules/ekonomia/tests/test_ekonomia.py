"""
Główny plik testowy dla modułu ekonomia
Agreguje wszystkie testy dla klas API i funkcjonalności modułu ekonomia
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


def ekonomia_run_all_tests():
    """
    Funkcja uruchamiająca wszystkie testy modułu ekonomia
    """
    test_dir = os.path.dirname(__file__)
    pytest.main([test_dir, '-v', '--tb=short'])  # -v to verbose, --tb=short to traceback short


if __name__ == '__main__':
    ekonomia_run_all_tests()
