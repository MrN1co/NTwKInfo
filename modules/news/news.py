"""
Główny plik modułu wiadomości i sportu
"""
from modules.news.routes import tables_bp
from modules.news.scrapers_daemon import start_all_daemons
import sys

def init_news_module():
    print("MODUŁ SPORTOWY - Uruchamianie")
    print("🚀 Uruchamianie scraperów...")
    daemon_threads = start_all_daemons()
    

