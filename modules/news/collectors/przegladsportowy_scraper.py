import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import locale


# Mapa kategorii na polskie nazwy tagów
CATEGORY_TAG_MAP = {
    'pilka-nozna': 'piłka-nożna',
    'tenis': 'tenis',
    'siatkowka': 'siatkówka',
    'zuzel': 'żużel',
    'lekkoatletyka': 'lekkoatletyka'
}


def _parse_polish_date(date_raw):
    """Parsuje polską datę w formacie '19 listopada 2025, 15:34' na timestamp i sformatowaną datę."""
    months = {
        'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4,
        'maja': 5, 'czerwca': 6, 'lipca': 7, 'sierpnia': 8,
        'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12
    }
    try:
        # Parsuj: "19 listopada 2025, 15:34"
        parts = date_raw.replace(',', '').split()
        if len(parts) >= 4:
            day = int(parts[0])
            month_name = parts[1]
            year = int(parts[2])
            time_parts = parts[3].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            month = months.get(month_name.lower())
            if month:
                dt = datetime(year, month, day, hour, minute)
                timestamp = int(dt.timestamp())
                date = dt.strftime('%d.%m.%Y %H:%M')
                return date, timestamp
    except Exception:
        pass
    return None, None


def _fetch_news_from_category(category_slug, limit=30, headers=None):
    """
    Pobiera wiadomości z konkretnej kategorii na przegladsportowy.pl.
    
    Args:
        category_slug: ścieżka kategorii (np. 'pilka-nozna', 'tenis', 'siatkowka')
        limit: maksymalna liczba wiadomości
        headers: nagłówki HTTP
        
    Returns:
        Lista słowników z wiadomościami
    """
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    url = f'https://przegladsportowy.onet.pl/{category_slug}'
    news_list = []

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        anchors = soup.find_all('a', class_='text-left flex w-full mb-6 last:mb-0 h-30', href=True)

        for a in anchors:
            if len(news_list) >= limit:
                break
            
            # Pobierz tytuł z <h3 class="title ...">
            h3 = a.find('h3', class_=lambda c: c and 'title' in c)
            if h3:
                title = h3.get_text(strip=True)
            else:
                title = a.get_text(strip=True)
            if not title:
                continue

            link = a['href']
            if link.startswith('/'):
                link = f'https://przegladsportowy.onet.pl/{category_slug}{link}'

            # Pobierz obrazek
            img = a.find('img')
            if not img:
                parent = a.parent
                if parent:
                    img = parent.find('img')

            image_url = None
            if img and img.has_attr('src'):
                image_url = img['src']

            # Spróbuj pobrać datę z artykułu
            date = None
            timestamp = None
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    mr2_divs = article_soup.find_all('div', class_='mr-2')
                    
                    for div in mr2_divs:
                        text = div.get_text(strip=True)
                        if any(month in text.lower() for month in ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']):
                            date_raw = div.get_text(strip=True)
                            date, timestamp = _parse_polish_date(date_raw)
                            break
            except Exception:
                pass

            news_list.append({
                'title': title,
                'link': link,
                'image': image_url,
                'date': date,
                'timestamp': timestamp,
                'tags': ['sport', CATEGORY_TAG_MAP.get(category_slug, category_slug)]
            })

        return news_list

    except requests.RequestException:
        return []
    except Exception:
        return []


def get_przegladsportowy_news(limit=30):
    """
    Pobiera najnowsze informacje z przegladsportowy.pl z wielu kategorii.
    Zwraca listę słowników z kluczami: 'title', 'link', 'image', 'date', 'tags'.
    """
    # Kategorie do scrapowania
    categories = [
        'pilka-nozna',
        'tenis',
        'siatkowka',
        'zuzel',
        'lekkoatletyka'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    all_news = []

    # Pobierz wiadomości z każdej kategorii
    for category in categories:
        try:
            news = _fetch_news_from_category(category, limit=5, headers=headers) 
            all_news.extend(news)
        except Exception:
            pass

    # Posortuj po timestamp (najnowsze na górze)
    all_news.sort(key=lambda x: x.get('timestamp') or 0, reverse=True)

    # Ogranicz do żądanej liczby
    return all_news[:limit]