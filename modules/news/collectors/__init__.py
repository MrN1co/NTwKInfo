"""
Moduł collectors - zawiera wszystkie scrapery i collectory danych sportowych
"""

from .football_api_scraper import get_football_standings, get_available_competitions
from .tennis_api_scraper import get_atp_rankings, get_wta_rankings
from .ekstraklasa_scraper import get_ekstraklasa_table, get_first_league_table, get_second_league_table
from .espn_api_scraper import get_nba_standings, get_mls_standings
from .kryminalki_scraper import get_kryminalki_news
from .minut_scraper import get_minut_news
from .przegladsportowy_scraper import get_przegladsportowy_news

__all__ = [
    'get_football_standings',
    'get_available_competitions',
    'get_atp_rankings',
    'get_wta_rankings',
    'get_ekstraklasa_table',
    'get_first_league_table',
    'get_second_league_table',
    'get_nba_standings',
    'get_mls_standings',
    'get_kryminalki_news',
    'get_minut_news',
    'get_przegladsportowy_news',
]
