import requests
from bs4 import BeautifulSoup


def scrape_policja_news(url, tags, limit=10):
    """
    Uniwersalny scraper dla stron policji (Kraków i Małopolska).
    Scrapuje z div#content -> ul -> li.news tylko: strong, img, span.data
    
    Args:
        url: URL strony do scrapowania
        tags: lista tagów do przypisania (np. ['kryminalne', 'Kraków'])
        limit: maksymalna liczba artykułów
    
    Returns:
        Lista słowników z wiadomościami
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Szukamy div#content
        content = soup.find('div', id='content')
        if not content:
            return []
        
        # Znajdź wszystkie <ul> i wybierz to z artykułami (li.news)
        all_uls = content.find_all('ul')
        items = []
        for ul in all_uls:
            items = ul.find_all('li', class_='news')
            if items:
                break
        
        if not items:
            return []

        news_list = []
        for li in items:
            if len(news_list) >= limit:
                break
            
            # Scrapujemy strong (tytuł)
            strong = li.find('strong')
            if not strong:
                continue
            
            title = strong.get_text(strip=True)
            if not title:
                continue
            
            # Link z <a> wewnątrz <li>
            a = li.find('a', href=True)
            if not a:
                continue
            
            href = a['href']
            # Normalizacja URL
            if href.startswith('/'):
                base_url = url.split('/')[0] + '//' + url.split('/')[2]
                link = base_url + href
            elif not href.startswith('http'):
                link = url.rstrip('/') + '/' + href
            else:
                link = href
            
            # Scrapujemy img
            img = li.find('img')
            image_url = None
            if img and img.has_attr('src'):
                src = img['src']
                # Normalizacja URL obrazka
                if src.startswith('/'):
                    base_url = url.split('/')[0] + '//' + url.split('/')[2]
                    image_url = base_url + src
                elif not src.startswith('http'):
                    image_url = url.rstrip('/') + '/' + src
                else:
                    image_url = src
            
            # Scrapujemy span.data (tylko data, bez godziny)
            span_date = li.find('span', class_='data')
            date_str = None
            if span_date:
                # Wyciągamy tylko datę po "Dodano: "
                date_text = span_date.get_text(strip=True)
                if 'Dodano:' in date_text:
                    date_str = date_text.replace('Dodano:', '').strip()
                else:
                    date_str = date_text

            news_list.append({
                'title': title,
                'link': link,
                'image': image_url,
                'date': date_str,
                'timestamp': None,
                'tags': tags
            })

        return news_list
    except Exception:
        return []


def get_policja_krakow_news(limit=10):
    """Pobiera wiadomości z Krakowskiej Policji."""
    url = 'https://krakow.policja.gov.pl/kr1/aktualnosci'
    tags = ['kryminalne', 'Kraków']
    return scrape_policja_news(url, tags, limit)


def get_policja_malopolska_news(limit=10):
    """Pobiera wiadomości z Małopolskiej Policji."""
    url = 'https://malopolska.policja.gov.pl/krk/aktualnosci/aktualnosci'
    tags = ['kryminalne', 'Małopolska']
    return scrape_policja_news(url, tags, limit)
