"""
Daemony scrapujące - działają w tle i pobierają dane regularnie
Zapisują dane do plików JSON
"""

import threading
import time
import json
import os
from collections import defaultdict
from datetime import datetime
import pytz

# Katalog główny projektu (2 poziomy w górę od tego pliku)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.news.collectors import (
    get_football_standings,
    get_atp_rankings,
    get_wta_rankings,
    get_ekstraklasa_table,
    get_first_league_table,
    get_second_league_table,
    get_nba_standings,
    get_mls_standings,
    get_kryminalki_news,
    get_minut_news,
    get_przegladsportowy_news,
    get_policja_krakow_news,
    get_policja_malopolska_news
)


# Strefa czasowa Polska
WARSAW_TZ = pytz.timezone('Europe/Warsaw')


def get_warsaw_time():
    """Zwraca aktualny czas w formacie DD.MM.RRRR   HH:MM:SS (Warszawa)"""
    return datetime.now(WARSAW_TZ).strftime('%d.%m.%Y   %H:%M:%S')


def load_football_config():
    """Wczytuje konfigurację football-data"""
    config_path = os.path.join(BASE_DIR, 'data', 'news', 'football-data', 'football_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_football_competitions():
    """Wczytuje konfigurację rozgrywek piłkarskich"""
    competitions_path = os.path.join(BASE_DIR, 'data', 'news', 'football-data', 'COMPETITIONS_config.JSON')
    with open(competitions_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('competitions', [])


def load_tennis_config():
    """Wczytuje konfigurację tenisa"""
    config_path = os.path.join(BASE_DIR, 'data', 'news', 'tennis-API', 'tennis_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_ekstraklasa_config():
    """Wczytuje konfigurację ekstraklasy"""
    config_path = os.path.join(BASE_DIR, 'data', 'news', '90minut', 'ekstraklasa_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_espn_config():
    """Wczytuje konfigurację ESPN (NBA, MLS)"""
    config_path = os.path.join(BASE_DIR, 'data', 'news', 'ESPN-API', 'espn_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_to_json(filepath, data):
    """Zapisuje dane do pliku JSON - NIE nadpisuje przy błędzie BEZ danych"""
    # Sprawdź czy są jakieś dane do zapisania
    has_data = bool(data.get('standings') or data.get('rankings') or data.get('data'))
    
    # Jeśli są dane, zapisuj (nawet jeśli jest też error)
    # Jeśli NIE MA danych I jest błąd, NIE nadpisuj
    if not has_data and data.get('error'):
        return  # Nie nadpisuj pustego pliku z samym błędem
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_from_json(filepath, default=None):
    """Wczytuje dane z pliku JSON"""
    if not os.path.exists(filepath):
        return default if default is not None else {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Błąd wczytywania {filepath}: {e}")
        return default if default is not None else {}


def determine_interval(entries, code, default_interval):
    """Zwraca interwał dla danego kodu z konfiguracji z uwzględnieniem minimum"""
    for entry in entries:
        if entry.get('code') == code:
            interval = entry.get('scraping_interval', default_interval)
            min_interval = entry.get('min_scraping_interval')
            if min_interval is not None:
                interval = max(interval, min_interval)
            return interval
    return default_interval


def update_tennis_rankings(section_key, fetch_func, limit=20):
    """Aktualizuje rankingi tenisowe, zachowując poprzednie dane przy błędzie"""
    section_key = section_key.lower()
    tennis_path = os.path.join(BASE_DIR, 'data', 'news', 'tennis-API', 'tennis_rankings.json')
    tennis_data = load_from_json(tennis_path, {})
    entry = tennis_data.get(section_key, {}).copy()
    error_reason = None

    try:
        rankings = fetch_func(limit=limit)
    except TypeError:
        rankings = fetch_func()
    except Exception as exc:
        error_reason = str(exc)
        rankings = []
        print(f"[{get_warsaw_time()}] Wyjątek podczas aktualizacji {section_key.upper()}: {error_reason}")

    success = bool(rankings)

    if success:
        entry.update({
            'type': section_key.upper(),
            'rankings': rankings,
            'updated_at': get_warsaw_time()
        })
        entry.pop('error', None)
    else:
        entry.setdefault('type', section_key.upper())
        entry.setdefault('rankings', entry.get('rankings', []))
        entry['error'] = error_reason or f"Brak nowych danych dla {section_key.upper()}"

    tennis_data[section_key] = entry
    save_to_json(tennis_path, tennis_data)
    return success


def update_polish_league(league_config):
    """Aktualizuje dane lig 90minut.pl i zachowuje poprzednie dane przy błędzie"""
    league_code = league_config['code']
    league_name = league_config['name']
    polish_data_path = os.path.join(BASE_DIR, 'data', 'news', '90minut', 'ekstraklasa.json')
    polish_data = load_from_json(polish_data_path, {})
    existing = polish_data.get(league_code, {}).copy()

    scrapers = {
        'EKS': get_ekstraklasa_table,
        'PL1': get_first_league_table,
        'PL2': get_second_league_table
    }

    scraper_func = scrapers.get(league_code)
    if not scraper_func:
        print(f"[{get_warsaw_time()}] Brak zdefiniowanego scrapera dla ligi {league_code}")
        return False

    try:
        table_data = scraper_func()
    except Exception as exc:
        print(f"[{get_warsaw_time()}] Wyjątek scrapera {league_code}: {exc}")
        table_data = {'standings': [], 'error': str(exc)}

    standings = table_data.get('standings') or []
    success = bool(standings)

    if success:
        payload = {
            'type': league_code,
            'competition_name': league_name,
            'area': league_config.get('area', 'Polska'),
            'updated_at': get_warsaw_time(),
            'standings': standings,
            'error': None
        }
    else:
        payload = existing if existing else {
            'type': league_code,
            'competition_name': league_name,
            'area': league_config.get('area', 'Polska'),
            'standings': []
        }
        if existing.get('standings'):
            payload['standings'] = existing['standings']
        payload.setdefault('updated_at', existing.get('updated_at'))
        payload['error'] = table_data.get('error') or payload.get('error') or 'Brak danych z 90minut.pl'

    polish_data[league_code] = payload
    save_to_json(polish_data_path, polish_data)
    return success


def update_football_league(league_code, season='current'):
    """Aktualizuje dane dla lig football-data.org, zachowując poprzednie dane przy błędzie"""
    # KAŻDA LIGA MA OSOBNY JSON aby nie nadpisywały się nawzajem!
    league_json_path = os.path.join(BASE_DIR, 'data', 'news', 'football-data', f'{league_code}_standings.json')
    existing = load_from_json(league_json_path, {})

    try:
        football_data = get_football_standings(league_code, season, skip_competition_info=True)
    except Exception as exc:
        print(f"[{get_warsaw_time()}] Wyjątek football-data {league_code}: {exc}")
        football_data = {
            'standings': [],
            'competition_name': league_code,
            'error': str(exc)
        }

    standings = football_data.get('standings') or []
    success = bool(standings)

    if success:
        football_data['updated_at'] = get_warsaw_time()
        football_data['error'] = football_data.get('error')
        save_to_json(league_json_path, football_data)
    else:
        merged = existing if existing else {}
        merged['competition_name'] = football_data.get('competition_name', merged.get('competition_name', league_code))
        merged['competition_emblem'] = football_data.get('competition_emblem', merged.get('competition_emblem'))
        merged['available_seasons'] = football_data.get('available_seasons', merged.get('available_seasons', []))
        merged['season_info'] = football_data.get('season_info', merged.get('season_info'))
        if existing.get('standings'):
            merged['standings'] = existing['standings']
            merged.setdefault('updated_at', existing.get('updated_at'))
        else:
            merged.setdefault('standings', [])
        merged['error'] = football_data.get('error') or merged.get('error') or 'Brak danych z football-data.org'
        save_to_json(league_json_path, merged)
    
    return success


def update_espn_league(code, fetch_func, filepath):
    """Aktualizuje dane z ESPN (NBA / MLS)"""
    existing = load_from_json(filepath, {})

    try:
        result = fetch_func()
    except Exception as exc:
        print(f"[{get_warsaw_time()}] Wyjątek ESPN {code}: {exc}")
        result = {'data': {}, 'error': str(exc)}

    if result.get('error'):
        existing.setdefault('type', code)
        existing.setdefault('data', existing.get('data', {}))
        existing.setdefault('updated_at', existing.get('updated_at'))
        existing['error'] = result['error']
        save_to_json(filepath, existing)
        return False

    payload = {
        'type': code,
        'updated_at': get_warsaw_time(),
        'data': result.get('data', {}),
        'error': None
    }
    save_to_json(filepath, payload)
    return True


# ============================================================================
# DAEMON DLA ATP
# ============================================================================
def atp_daemon(interval):
    """
    Daemon scrapujący ranking ATP
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    
    while True:
        success = update_tennis_rankings('atp', get_atp_rankings)
        if not success:
            print(f"[{get_warsaw_time()}] Ostrzeżenie: utrzymano poprzedni ranking ATP")
        time.sleep(interval)


def wta_daemon(interval):
    """
    Daemon scrapujący ranking WTA
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    
    while True:
        success = update_tennis_rankings('wta', get_wta_rankings)
        if not success:
            print(f"[{get_warsaw_time()}] Ostrzeżenie: utrzymano poprzedni ranking WTA")
        time.sleep(interval)


# ============================================================================
# DAEMON DLA POLSKICH LIG (90minut.pl)
# ============================================================================
def polish_leagues_daemon():
    """
    Daemon scrapujący polskie ligi (Ekstraklasa, I Liga, II Liga)
    Scrapuje rotacyjnie według konfiguracji
    """

    ekstraklasa_config = load_ekstraklasa_config()
    leagues = ekstraklasa_config.get('leagues', [])
    if not leagues:
        print(f"[{get_warsaw_time()}] Brak lig w konfiguracji 90minut.pl")
        return

    def compute_interval(league):
        value = league.get('scraping_interval', 60)
        min_value = league.get('min_scraping_interval')
        if min_value is not None:
            value = max(value, min_value)
        return value

    interval = compute_interval(leagues[0])

    league_index = 0

    while True:
        try:
            league = leagues[league_index]
            league_name = league['name']

            success = update_polish_league(league)
            if not success:
                print(f"[{get_warsaw_time()}] Ostrzeżenie: utrzymano poprzednie dane {league_name}")

            league_index = (league_index + 1) % len(leagues)
            time.sleep(interval)

        except Exception as e:
            print(f"[{get_warsaw_time()}] Błąd daemona polskich lig: {e}")
            time.sleep(10)


# ============================================================================
# DAEMON DLA LIG PIŁKARSKICH (Football-data.org)
# ============================================================================
def football_leagues_daemon():
    """
    Daemon scrapujący 10 lig piłkarskich (rotacyjnie)
    ZWIĘKSZONY interwał: co 15 sekund (każda liga co 150s = 2.5min) aby nie wyczerpać API
    """

    # 9 najważniejszych lig europejskich + Brazylia
    LEAGUES = [
        'PL',   # Premier League (Anglia)
        'PD',   # La Liga (Hiszpania)
        'SA',   # Serie A (Włochy)
        'BL1',  # Bundesliga (Niemcy)
        'FL1',  # Ligue 1 (Francja)
        'DED',  # Eredivisie (Holandia)
        'PPL',  # Primeira Liga (Portugalia)
        'BSA',  # Brasileirão (Brazylia)
        'CL',   # Liga Mistrzów
        'ELC'   # Championship (Anglia)
    ]
    
    # ZWIĘKSZONY interwał z 7s na 15s (każda liga co 150s zamiast 70s)
    interval = 15

    league_index = 0

    while True:
        try:
            league_code = LEAGUES[league_index]

            success = update_football_league(league_code)

            league_index = (league_index + 1) % len(LEAGUES)
            time.sleep(interval)

        except Exception as e:
            league_index = (league_index + 1) % len(LEAGUES)
            time.sleep(interval)


# ============================================================================
# DAEMON DLA NBA
# ============================================================================
def nba_daemon(interval):
    """
    Daemon scrapujący tabelę NBA
    Args:
        interval: interwał w sekundach między scrapowaniem
    """

    nba_path = os.path.join(BASE_DIR, 'data', 'news', 'ESPN-API', 'nba_standings.json')
    
    while True:
        update_espn_league('NBA', get_nba_standings, nba_path)
        time.sleep(interval)


# ============================================================================
# DAEMON DLA MLS
# ============================================================================
def mls_daemon(interval):
    """
    Daemon scrapujący tabelę MLS
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    mls_path = os.path.join(BASE_DIR, 'data', 'news', 'ESPN-API', 'mls_standings.json')
    
    while True:
        update_espn_league('MLS', get_mls_standings, mls_path)
        time.sleep(interval)


# ============================================================================
# DAEMON DLA WIADOMOŚCI KRYMINALKI.PL
# ============================================================================
def kryminalki_news_daemon(interval):
    """
    Daemon scrapujący wiadomości z kryminalki.pl
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    news_path = os.path.join(BASE_DIR, 'data', 'news', 'kryminalki', 'kryminalki.json')
    archive_path = os.path.join(BASE_DIR, 'data', 'news', 'kryminalki', 'kryminalki_archiwum.json')
    
    while True:
        try:
            news_list = get_kryminalki_news(limit=15)
            
            if news_list:
                # Wczytaj stare dane do archiwum (na przyszłość)
                old_data = load_from_json(news_path, {})
                if old_data.get('news'):
                    # Zapisz stare wiadomości do archiwum
                    archive_data = load_from_json(archive_path, {'archived_news': []})
                    # Dodaj stare wiadomości na początek archiwum (najnowsze najpierw)
                    archive_data.setdefault('archived_news', [])
                    archive_data['archived_news'] = old_data['news'] + archive_data['archived_news']
                    # Ogranicz archiwum do 100 wiadomości
                    archive_data['archived_news'] = archive_data['archived_news'][:100]
                    save_to_json(archive_path, archive_data)
                
                # Zapisz nowe wiadomości
                news_data = {
                    'news': news_list,
                    'updated_at': get_warsaw_time()
                }
                save_to_json(news_path, news_data)
        except Exception as e:
            pass
        
        time.sleep(interval)
# ============================================================================
# DAEMON DLA WIADOMOŚCI 90minut.PL
# ============================================================================
def minut_news_daemon(interval):
    """
    Daemon scrapujący wiadomości z 90minut.pl
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    news_path = os.path.join(BASE_DIR, 'data', 'news', 'minut', 'minut.json')
    archive_path = os.path.join(BASE_DIR, 'data', 'news', 'minut', 'minut_archiwum.json')
    
    while True:
        try:
            news_list = get_minut_news(limit=15)
            
            if news_list:
                # Wczytaj stare dane do archiwum (na przyszłość)
                old_data = load_from_json(news_path, {})
                if old_data.get('news'):
                    # Zapisz stare wiadomości do archiwum
                    archive_data = load_from_json(archive_path, {'archived_news': []})
                    # Dodaj stare wiadomości na początek archiwum (najnowsze najpierw)
                    archive_data.setdefault('archived_news', [])
                    archive_data['archived_news'] = old_data['news'] + archive_data['archived_news']
                    # Ogranicz archiwum do 100 wiadomości
                    archive_data['archived_news'] = archive_data['archived_news'][:100]
                    save_to_json(archive_path, archive_data)
                
                # Zapisz nowe wiadomości
                news_data = {
                    'news': news_list,
                    'updated_at': get_warsaw_time()
                }
                save_to_json(news_path, news_data)
        except Exception as e:
            print(f"[{get_warsaw_time()}] Błąd daemon wiadomości: {e}")
        
        time.sleep(interval)

# ============================================================================
# DAEMON DLA WIADOMOŚCI przegladsportowy.onet.PL
# ============================================================================
def przegladsportowy_news_daemon(interval):
    """
    Daemon scrapujący wiadomości z przegladsportowy.onet.pl
    Args:
        interval: interwał w sekundach między scrapowaniem
    """
    news_path = os.path.join(BASE_DIR, 'data', 'news', 'przegladsportowy', 'przegladsportowy.json')
    archive_path = os.path.join(BASE_DIR, 'data', 'news', 'przegladsportowy', 'przegladsportowy.json')
    
    while True:
        try:
            news_list = get_przegladsportowy_news(limit=15)
            
            if news_list:
                # Wczytaj stare dane do archiwum (na przyszłość)
                old_data = load_from_json(news_path, {})
                if old_data.get('news'):
                    # Zapisz stare wiadomości do archiwum
                    archive_data = load_from_json(archive_path, {'archived_news': []})
                    # Dodaj stare wiadomości na początek archiwum (najnowsze najpierw)
                    archive_data.setdefault('archived_news', [])
                    archive_data['archived_news'] = old_data['news'] + archive_data['archived_news']
                    # Ogranicz archiwum do 100 wiadomości
                    archive_data['archived_news'] = archive_data['archived_news'][:100]
                    save_to_json(archive_path, archive_data)
                
                # Zapisz nowe wiadomości
                news_data = {
                    'news': news_list,
                    'updated_at': get_warsaw_time()
                }
                save_to_json(news_path, news_data)
        except Exception as e:
            pass
        
        time.sleep(interval)

# ============================================================================
# DAEMONY DLA WIADOMOŚCI POLICJI (Kraków / Małopolska)
# ============================================================================
def policja_krakow_news_daemon(interval):
    """
    Daemon scrapujący wiadomości z krakowskiej policji
    """
    news_path = os.path.join(BASE_DIR, 'data', 'news', 'policja', 'krakow.json')
    archive_path = os.path.join(BASE_DIR, 'data', 'news', 'policja', 'krakow_archiwum.json')

    while True:
        try:
            news_list = get_policja_krakow_news(limit=10)

            if news_list:
                old_data = load_from_json(news_path, {})
                if old_data.get('news'):
                    archive_data = load_from_json(archive_path, {'archived_news': []})
                    archive_data.setdefault('archived_news', [])
                    archive_data['archived_news'] = old_data['news'] + archive_data['archived_news']
                    archive_data['archived_news'] = archive_data['archived_news'][:100]
                    save_to_json(archive_path, archive_data)

                news_data = {
                    'news': news_list,
                    'updated_at': get_warsaw_time()
                }
                save_to_json(news_path, news_data)
            else:
                print(f"[{get_warsaw_time()}] Brak wiadomości z Policji Kraków")
        except Exception as e:
            print(f"[{get_warsaw_time()}] Błąd w Policja Kraków daemon: {e}")

        time.sleep(interval)


def policja_malopolska_news_daemon(interval):
    """
    Daemon scrapujący wiadomości z małopolskiej policji
    """
    news_path = os.path.join(BASE_DIR, 'data', 'news', 'policja', 'malopolska.json')
    archive_path = os.path.join(BASE_DIR, 'data', 'news', 'policja', 'malopolska_archiwum.json')


    while True:
        try:
            news_list = get_policja_malopolska_news(limit=10)

            if news_list:
                old_data = load_from_json(news_path, {})
                if old_data.get('news'):
                    archive_data = load_from_json(archive_path, {'archived_news': []})
                    archive_data.setdefault('archived_news', [])
                    archive_data['archived_news'] = old_data['news'] + archive_data['archived_news']
                    archive_data['archived_news'] = archive_data['archived_news'][:100]
                    save_to_json(archive_path, archive_data)

                news_data = {
                    'news': news_list,
                    'updated_at': get_warsaw_time()
                }
                save_to_json(news_path, news_data)
            else:
                print(f"[{get_warsaw_time()}] Brak wiadomości z Policji Małopolska")
        except Exception as e:
            print(f"[{get_warsaw_time()}] Błąd w Policja Małopolska daemon: {e}")

        time.sleep(interval)
# ============================================================================
# FUNKCJA STARTOWA - URUCHAMIA WSZYSTKIE DAEMONY
# ============================================================================
def start_all_daemons():
    """Uruchamia wszystkie daemony w osobnych wątkach"""
    tennis_config = load_tennis_config()
    espn_config = load_espn_config()

    tennis_entries = tennis_config.get('rankings', [])
    atp_interval = determine_interval(tennis_entries, 'ATP', 3600)
    wta_interval = determine_interval(tennis_entries, 'WTA', 3600)

    espn_entries = espn_config.get('leagues', [])
    nba_interval = determine_interval(espn_entries, 'NBA', 3600)
    mls_interval = determine_interval(espn_entries, 'MLS', 3600)

    # Interwał dla wiadomości - 5 minut (300s)
    news_interval = 300
    
    print(f"[{get_warsaw_time()}] Uruchamianie daemonów scrapujących...")
    
    threads = [
        threading.Thread(target=atp_daemon, args=(atp_interval,), daemon=True, name="ATP-Daemon"),
        threading.Thread(target=wta_daemon, args=(wta_interval,), daemon=True, name="WTA-Daemon"),
        threading.Thread(target=polish_leagues_daemon, daemon=True, name="Polish-Leagues-Daemon"),
        threading.Thread(target=football_leagues_daemon, daemon=True, name="Football-Daemon"),
        threading.Thread(target=nba_daemon, args=(nba_interval,), daemon=True, name="NBA-Daemon"),
        threading.Thread(target=mls_daemon, args=(mls_interval,), daemon=True, name="MLS-Daemon"),
        threading.Thread(target=kryminalki_news_daemon, args=(news_interval,), daemon=True, name="Kryminalki-News-Daemon"),
        threading.Thread(target=minut_news_daemon, args=(news_interval,), daemon=True, name="Minut-News-Daemon"),
        threading.Thread(target=przegladsportowy_news_daemon, args=(news_interval,), daemon=True, name="PrzegladSportowy-News-Daemon")
        ,threading.Thread(target=policja_krakow_news_daemon, args=(news_interval,), daemon=True, name="Policja-Krakow-News-Daemon")
        ,threading.Thread(target=policja_malopolska_news_daemon, args=(news_interval,), daemon=True, name="Policja-Malopolska-News-Daemon")
    ]

    for thread in threads:
        thread.start()
    return threads

