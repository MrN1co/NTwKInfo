"""
Blueprint Flask - trasy dla tabel sportowych
WAŻNE: Ten moduł TYLKO CZYTA dane z JSON.
NIGDY nie wywołuje scraperów bezpośrednio - to zadanie daemonów!
"""

from flask import Blueprint, render_template, request
import json
import os
from collections import defaultdict
from datetime import datetime
import pytz
from modules.news.collectors import get_kryminalki_news
from modules.news.collectors import get_przegladsportowy_news

# Tworzymy Blueprint
tables_bp = Blueprint('tables', __name__, template_folder='templates')


@tables_bp.route('/sport')
def sport_demo():
    """Demo endpoint dla tabel sportowych w iframe"""
    return render_template('news/news_demo.html', iframe_src='/news/tables?competition=PL&season=2025')


@tables_bp.route('/news-page')
def news_page_demo():
    """Demo endpoint dla wiadomości w iframe"""
    return render_template('news/news_demo.html', iframe_src='/news/news')

# Mapowanie nazw lig na polskie
LEAGUE_NAME_TRANSLATIONS = {
    'UEFA Champions League': 'Liga Mistrzów',
    'Primeira Liga': 'Primeira Liga',
    'Premier League': 'Premier League',
    'Eredivisie': 'Eredivisie',
    'Bundesliga': 'Bundesliga',
    'Ligue 1': 'Ligue 1',
    'Serie A': 'Serie A',
    'Primera Division': 'Primera División',
    'Championship': 'Championship',
    'Campeonato Brasileiro Série A': 'Campeonato Brasileiro Série A',
}

# Mapowanie krajów/regionów na polskie
AREA_TRANSLATIONS = {
    'Europe': 'Europa',
    'Portugal': 'Portugalia',
    'England': 'Anglia',
    'Netherlands': 'Holandia',
    'Germany': 'Niemcy',
    'France': 'Francja',
    'Italy': 'Włochy',
    'Spain': 'Hiszpania',
    'Brazil': 'Brazylia',
    'USA': 'USA',
}

def localize_competition_name(name, area):
    """
    Tłumaczy nazwę ligi i region na polski
    
    Args:
        name (str): Oryginalna nazwa ligi
        area (str): Region/kraj (JUŻ PRZETŁUMACZONY w COMPETITIONS_config.JSON)
        
    Returns:
        str: Zlokalizowana nazwa w formacie "Nazwa (Region)"
    """
    translated_name = LEAGUE_NAME_TRANSLATIONS.get(name, name)
    
    if f"({area})" in translated_name:
        return translated_name
    
    return f"{translated_name}" if area else translated_name


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


def load_config():
    """Wczytuje konfigurację"""
    return load_from_json('config.json', {})


def get_available_competitions():
    """Pobiera listę dostępnych rozgrywek z pliku"""
    try:
        with open('data/news/football-data/COMPETITIONS_config.JSON', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('competitions', [])
    except Exception as e:
        print(f"Błąd wczytywania COMPETITIONS_config.JSON: {e}")
        return []


WARSAW_TZ = pytz.timezone('Europe/Warsaw')


def get_warsaw_time():
    """Zwraca aktualny czas warszawski"""
    return datetime.now(WARSAW_TZ).strftime('%d.%m.%Y   %H:%M:%S')


def save_to_json(filepath, data):
    """Zapisuje słownik do pliku JSON"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)





def safe_float(value, default=0.0):
    """Konwertuje wartość na float, zwraca default przy błędzie"""
    try:
        if value is None:
            return default
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return default
            value = stripped.replace(',', '.')
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    """Konwertuje wartość na int, zwraca default przy błędzie"""
    try:
        return int(round(safe_float(value, default)))
    except (TypeError, ValueError):
        return default


def find_stat(stats, name, attr='value', default=None):
    """Znajduje konkretną statystykę w liście slowników"""
    for stat in stats:
        if stat.get('name') == name:
            return stat.get(attr, default)
    return default


@tables_bp.route('/news')
def news():
    """
    Trasa wyświetlająca połączone wiadomości z wszystkich źródeł (kryminalki, 90minut, przegladsportowy)
    Obsługuje filtrowanie po tagach przez query parameter ?tags=sport,kryminalne
    """
    # Pobierz tagi z query parameters
    tags_param = request.args.get('tags', '')
    selected_tags = [t.strip() for t in tags_param.split(',') if t.strip()] if tags_param else []
    
    # Wczytaj wiadomości z wszystkich źródeł
    kryminalki_path = 'data/news/kryminalki/kryminalki.json'
    minut_path = 'data/news/minut/minut.json'
    przegladsportowy_path = 'data/news/przegladsportowy/przegladsportowy.json'
    
    kryminalki_data = load_from_json(kryminalki_path, {'news': []})
    minut_data = load_from_json(minut_path, {'news': []})
    przegladsportowy_data = load_from_json(przegladsportowy_path, {'news': []})
    
    # Połącz wszystkie wiadomości
    all_news = []
    all_news.extend(kryminalki_data.get('news', []))
    all_news.extend(minut_data.get('news', []))
    all_news.extend(przegladsportowy_data.get('news', []))
    
    # Filtruj po tagach jeśli są wybrane
    if selected_tags:
        filtered_news = []
        for news_item in all_news:
            item_tags = news_item.get('tags', [])
            # Sprawdź czy wiadomość ma przynajmniej jeden z wybranych tagów
            if any(tag in item_tags for tag in selected_tags):
                filtered_news.append(news_item)
        all_news = filtered_news
    
    # Sortuj po dacie malejąco (najnowsze pierwsze)
    all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('news/news.html', 
                         news_list=all_news,
                         selected_tags=selected_tags)


@tables_bp.route('/news_sport')
def news_sport():
    """
    Trasa wyświetlająca wiadomości z przegladsportowy.pl
    """
    # Wczytaj wiadomości z JSON
    news_path = 'data/news/przegladsportowy/przegladsportowy.json'
    news_data = load_from_json(news_path, {'news': [], 'updated_at': None})
    
    # Jeśli brak danych w JSON, pobierz świeże (fallback)
    if not news_data.get('news'):
        try:
            fresh_news = get_przegladsportowy_news(limit=15)
            if fresh_news:
                news_data = {
                    'news': fresh_news,
                    'updated_at': get_warsaw_time()
                }
                # Zapisz do JSON
                save_to_json(news_path, news_data)
        except Exception as e:
            print(f"Błąd pobierania wiadomości: {e}")
            news_data = {'news': [], 'updated_at': None}
    
    return render_template('news/news_sport.html', 
                         news_list=news_data.get('news', []),
                         updated_at=news_data.get('updated_at'))
@tables_bp.route('/tables')
def tables():
    """
    Trasa wyświetlająca tabele sportowe (blueprint)
    Parametry GET:
        - competition: kod ligi/sportu
        - season: sezon (rok np. '2025' lub 'current' dla kompatybilności)
    """
    selected_competition = request.args.get('competition', 'EKS')
    selected_season = request.args.get('season', '2025')
    
    football_competitions = get_available_competitions()
    
    # Lokalizuj nazwy lig piłkarskich
    localized_football = []
    for comp in football_competitions:
        localized_name = localize_competition_name(comp.get('name', ''), comp.get('area', ''))
        comp_copy = comp.copy()
        comp_copy['name'] = localized_name
        localized_football.append(comp_copy)
    
    polish_leagues_config = load_from_json('data/news/90minut/ekstraklasa_config.json', {})
    polish_leagues = polish_leagues_config.get('leagues', [])
    
    # Wyciągamy Ligę Mistrzów z localized_football
    champions_league = next((c for c in localized_football if c.get('code') == 'CL'), None)
    other_football = [c for c in localized_football if c.get('code') != 'CL']
    
    # Kolejność: Ekstraklasa, I Liga, II Liga, Liga Mistrzów, pozostałe
    all_competitions = polish_leagues + ([champions_league] if champions_league else []) + other_football + [
        {'code': 'ATP', 'name': 'ATP - Tenis Mężczyzn', 'area': 'Tenis', 'is_tennis': True},
        {'code': 'WTA', 'name': 'WTA - Tenis Kobiet', 'area': 'Tenis', 'is_tennis': True},
        {'code': 'NBA', 'name': 'NBA - Koszykówka', 'area': 'USA', 'is_nba': True},
        {'code': 'MLS', 'name': 'MLS - Major League Soccer', 'area': 'USA', 'is_mls': True}
    ]
    
    data = {
        'all_competitions': all_competitions,
        'selected_code': selected_competition,
        'selected_season': selected_season,
        'error': None
    }
    if selected_competition == 'ATP':
        # Ranking ATP z JSON
        tennis_path = 'data/news/tennis-API/tennis_rankings.json'
        tennis_data = load_from_json(tennis_path, {})
        atp_data = tennis_data.get('atp', {})

        atp_error = None if atp_data.get('rankings') else (
            atp_data.get('error') or 'Dane ATP będą wkrótce dostępne. Daemon scrapuje dane regularnie.'
        )

        data.update({
            'is_tennis': True,
            'competition_name': 'Ranking ATP - Mężczyźni',
            'tennis_rankings': atp_data.get('rankings', []),
            'updated_at': atp_data.get('updated_at'),
            'error': atp_error
        })
        
    elif selected_competition == 'WTA':
        # Ranking WTA z JSON
        tennis_path = 'data/news/tennis-API/tennis_rankings.json'
        tennis_data = load_from_json(tennis_path, {})
        wta_data = tennis_data.get('wta', {})

        #
        wta_error = None if wta_data.get('rankings') else (
            wta_data.get('error') or 'Dane WTA będą wkrótce dostępne. Daemon scrapuje dane regularnie.'
        )

        data.update({
            'is_tennis': True,
            'competition_name': 'Ranking WTA - Kobiety',
            'tennis_rankings': wta_data.get('rankings', []),
            'updated_at': wta_data.get('updated_at'),
            'error': wta_error
        })
        
    elif selected_competition in ['EKS', 'PL1', 'PL2']:
        # Polskie ligi z JSON
        polish_path = 'data/news/90minut/ekstraklasa.json'
        polish_data = load_from_json(polish_path, {})
        league_data = polish_data.get(selected_competition, {})

        league_name = league_data.get('competition_name', selected_competition)
        
        
        league_error = None if league_data.get('standings') else (
            league_data.get('error') or f'Dane dla {league_name} będą wkrótce dostępne. Daemon scrapuje dane regularnie.'
        )
        
        data.update({
            'is_football': True,
            'standings': league_data.get('standings', []),
            'competition_name': league_data.get('competition_name', selected_competition),
            'updated_at': league_data.get('updated_at'),
            'error': league_error
        })
        
    elif selected_competition == 'NBA':
        nba_json = load_from_json('data/news/ESPN-API/nba_standings.json', {})
        nba_data = nba_json.get('data', {})
        
        conferences_data = defaultdict(list)
        
        for conference in nba_data.get('children', []):
            entries = conference.get('standings', {}).get('entries', [])
            if not entries:
                continue
            conference_label = conference.get('shortName') or conference.get('abbreviation') or conference.get('name', 'Conference')
            conference_key = conference.get('abbreviation') or conference_label.split()[0]

            for entry in entries:
                team = entry.get('team', {})
                stats = entry.get('stats', [])
                wins = safe_int(find_stat(stats, 'wins', 'value', 0))
                losses = safe_int(find_stat(stats, 'losses', 'value', 0))
                win_percent = safe_float(find_stat(stats, 'winPercent', 'value', 0.0))
                gb_display = find_stat(stats, 'gamesBehind', 'displayValue', '-')
                if not gb_display:
                    gb_value = find_stat(stats, 'gamesBehind', 'value', 0)
                    gb_display = f"{safe_float(gb_value, 0.0):.1f}" if isinstance(gb_value, (int, float)) else str(gb_value)
                streak = find_stat(stats, 'streak', 'displayValue', '-') or '-'
                logo = next((logo_info.get('href') for logo_info in team.get('logos', []) if 'default' in logo_info.get('rel', [])), None)

                conferences_data[conference_key].append({
                    'team_name': team.get('displayName', team.get('name', 'Unknown Team')),
                    'team_logo': logo,
                    'wins': wins,
                    'losses': losses,
                    'win_percent': win_percent,
                    'games_behind': gb_display,
                    'streak': streak
                })
        
        for teams in conferences_data.values():
            teams.sort(key=lambda x: (-x['win_percent'], -x['wins'], x['losses']))
        
        nba_conferences = {name: teams for name, teams in sorted(conferences_data.items()) if teams}
        nba_error = nba_json.get('error') or (None if nba_conferences else 'Brak danych NBA')

        data.update({
            'is_nba': True,
            'competition_name': 'NBA - National Basketball Association',
            'nba_conferences': nba_conferences,
            'updated_at': nba_json.get('updated_at'),
            'error': nba_error
        })
        
    elif selected_competition == 'MLS':
        mls_json = load_from_json('data/news/ESPN-API/mls_standings.json', {})
        mls_data = mls_json.get('data', {})
        
        conferences_data = defaultdict(list)
        
        for conference in mls_data.get('children', []):
            entries = conference.get('standings', {}).get('entries', [])
            if not entries:
                continue
            conference_label = conference.get('shortName') or conference.get('abbreviation') or conference.get('name', 'Conference')
            conference_key = conference.get('abbreviation') or conference_label.split()[0]

            for entry in entries:
                team = entry.get('team', {})
                stats = entry.get('stats', [])
                points = safe_int(find_stat(stats, 'points', 'value', 0))
                wins = safe_int(find_stat(stats, 'wins', 'value', 0))
                losses = safe_int(find_stat(stats, 'losses', 'value', 0))
                ties = safe_int(find_stat(stats, 'ties', 'value', 0))
                logo = next((logo_info.get('href') for logo_info in team.get('logos', []) if 'default' in logo_info.get('rel', [])), None)

                conferences_data[conference_key].append({
                    'team_name': team.get('displayName', team.get('name', 'Unknown Team')),
                    'team_logo': logo,
                    'points': points,
                    'wins': wins,
                    'losses': losses,
                    'ties': ties
                })
        
        for teams in conferences_data.values():
            teams.sort(key=lambda x: (-x['points'], -x['wins'], x['losses']))
        
        mls_conferences = {name: teams for name, teams in sorted(conferences_data.items()) if teams}
        mls_error = mls_json.get('error') or (None if mls_conferences else 'Brak danych MLS')

        data.update({
            'is_mls': True,
            'competition_name': 'MLS - Major League Soccer',
            'mls_conferences': mls_conferences,
            'updated_at': mls_json.get('updated_at'),
            'error': mls_error
        })
        
    else:
        # Liga piłkarska z football-data API
        # KAŻDA LIGA MA TERAZ OSOBNY JSON!
        league_json_path = f'data/news/football-data/{selected_competition}_standings.json'
        current_league = load_from_json(league_json_path, {})
        
        historical_data = load_from_json('data/news/football-data/historical_seasons.json', {})
        
        # Pobierz info o lidze z COMPETITIONS_config.JSON aby uzyskać dostępne sezony
        competitions = get_available_competitions()
        comp_info = next((c for c in competitions if c.get('code') == selected_competition), None)
        
        # Przygotuj dostępne sezony z COMPETITIONS_config.JSON
        available_seasons = []
        if comp_info:
            max_seasons = comp_info.get('seasons', 3)
            start_year = int(comp_info.get('startDate', '2025')[:4])
            # Generuj listę sezonów wstecz
            for i in range(max_seasons):
                year = start_year - i
                available_seasons.append({
                    'year': str(year),
                    'label': f"{year}/{year+1}",
                    'winner': ''
                })
        
        current_season_year = None
        if current_league and current_league.get('season_info') and current_league['season_info']:
            current_season_year = current_league['season_info'].get('startDate', '')[:4]
        
        # Wybierz odpowiedni sezon
        if selected_season == 'current' or selected_season == current_season_year or not current_season_year:
            # Używamy danych z osobnego pliku ligi
            football_data = current_league
            
            # Fallback do danych historycznych jeśli brak aktualnych
            if not football_data.get('standings'):
                key = f"{selected_competition}_{selected_season}"
                historical_match = historical_data.get(key, {})
                if historical_match.get('standings'):
                    football_data = historical_match
        else:
            key = f"{selected_competition}_{selected_season}"
            football_data = historical_data.get(key, {})
        
        # Jeśli nadal brak danych, sprawdź czy liga w ogóle istnieje w konfigu
        if not football_data or not football_data.get('standings'):
            if comp_info:
                # Mamy informacje o lidze, ale brak danych z API
                football_data = {
                    'standings': [],
                    'competition_name': comp_info.get('name', selected_competition),
                    'competition_emblem': comp_info.get('emblem', ''),
                    'season_info': None,
                    'available_seasons': available_seasons,
                    'updated_at': None,
                    'error': football_data.get('error') if football_data else 'Dane dla tej ligi będą wkrótce dostępne. Daemon scrapuje ligi rotacyjnie.'
                }
            else:
                # Liga nie istnieje w konfigu
                football_data = {
                    'standings': [],
                    'competition_name': selected_competition,
                    'competition_emblem': '',
                    'season_info': None,
                    'available_seasons': [],
                    'updated_at': None,
                    'error': 'Liga nie została znaleziona w konfiguracji'
                }
        
        # Dodaj available_seasons jeśli brak w football_data
        if not football_data.get('available_seasons'):
            football_data['available_seasons'] = available_seasons
        
        data.update({
            'is_football': True,
            'standings': football_data.get('standings', []),
            'competition_name': football_data.get('competition_name', selected_competition),
            'competition_emblem': football_data.get('competition_emblem', ''),
            'season_info': football_data.get('season_info'),
            'available_seasons': football_data.get('available_seasons', []),
            'updated_at': football_data.get('updated_at'),
            'error': football_data.get('error')
        })
    
    return render_template('news/tables.html', **data)
