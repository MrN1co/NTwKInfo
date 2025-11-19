import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import locale


def get_przegladsportowy_news(limit=10):
    """
    Pobiera najnowsze informacje z przegladsportowy.pl (prosta, defensywna implementacja).
    Zwraca listę słowników z kluczami: 'title', 'link', 'image', 'date', 'tags'.
    """
    url = 'https://przegladsportowy.onet.pl/pilka-nozna'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        news_list = []

        
        anchors = soup.find_all('a', class_='text-left flex w-full mb-6 last:mb-0 h-30', href=True)

        for a in anchors:
            if len(news_list) >= limit:
                break
            # Najpierw spróbuj pobrać tytuł z <h3 class="title ..."> wewnątrz linku
            h3 = a.find('h3', class_=lambda c: c and 'title' in c)
            if h3:
                title = h3.get_text(strip=True)
            else:
                title = a.get_text(strip=True)
            if not title:
                continue

            link = a['href']
            if link.startswith('/'):
                link = f'https://przegladsportowy.onet.pl/pilka-nozna{link}'

            # Spróbuj znaleźć obrazek związany z linkiem
            img = a.find('img')
            if not img:
                # czasami obrazek jest w sąsiednim elemencie
                parent = a.parent
                if parent:
                    img = parent.find('img')

            image_url = None
            if img and img.has_attr('src'):
                image_url = img['src']

            # Wejdź na stronę artykułu i pobierz datę z div class="mr-2"
            date = None
            timestamp = None
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Znajdź wszystkie div-y z klasą "mr-2"
                    mr2_divs = article_soup.find_all('div', class_='mr-2')
                    date_div = None
                    
                    # Szukaj tego, który zawiera datę (polską nazwę miesiąca)
                    for div in mr2_divs:
                        text = div.get_text(strip=True)
                        if any(month in text.lower() for month in ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']):
                            date_div = div
                            break
                    
                    if date_div:
                        date_raw = date_div.get_text(strip=True)
                        # Format: "19 listopada 2025, 15:34"
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
                        except Exception:
                            pass
            except Exception:
                pass
            
            # Jeśli nie udało się pobrać, użyj aktualnego czasu
            if not timestamp:
                timestamp = int(time.time())
                date = datetime.now().strftime('%d.%m.%Y %H:%M')

            news_list.append({
                'title': title,
                'link': link,
                'image': image_url,
                'date': date,
                'timestamp': timestamp,
                'tags': ['sport']
            })

        return news_list

    except requests.RequestException:
        return []
    except Exception:
        return []