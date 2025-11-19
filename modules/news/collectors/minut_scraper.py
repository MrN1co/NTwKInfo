import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import time


def get_minut_news(limit=10):
    """
    Pobiera najnowsze informacje z 90minut.pl (prosta, defensywna implementacja).
    Zwraca listę słowników z kluczami: 'title', 'link', 'image', 'date', 'tags'.
    """
    url = 'http://www.90minut.pl'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.content, 'html.parser')
        news_list = []

        # Struktura strony 90minut może się zmieniać — szukamy linków z klasą 'new' (jak w poprzedniej wersji)
        anchors = soup.find_all('a', class_='new', href=True)

        for a in anchors:
            if len(news_list) >= limit:
                break

            title = a.get_text(strip=True)
            if not title:
                continue

            link = a['href']
            if link.startswith('/'):
                link = f'http://www.90minut.pl{link}'

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

            # Wejdź na stronę artykułu i pobierz datę z drugiego <p> w <blockquote>
            date = None
            timestamp = None
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Znajdź <blockquote> i weź drugi <p>
                    blockquote = article_soup.find('blockquote')
                    if blockquote:
                        p_tags = blockquote.find_all('p')
                        if len(p_tags) >= 2:
                            # Drugi p zawiera datę na początku: "8 listopada 2025, 19:43:35"
                            second_p_text = p_tags[1].get_text(strip=True)
                            
                            # Wyciągnij pierwszą linię (do pierwszego znaku nowej linii lub do ok. 50 znaków)
                            first_line = second_p_text.split('\n')[0].strip()
                            # Czasami data może być na początku bez nowej linii - weź tylko część z datą
                            date_match = first_line[:50]  # Data nie powinna być dłuższa
                            
                            # Parsuj polską datę: "8 listopada 2025, 19:43:35"
                            months = {
                                'stycznia': 1, 'lutego': 2, 'marca': 3, 'kwietnia': 4,
                                'maja': 5, 'czerwca': 6, 'lipca': 7, 'sierpnia': 8,
                                'września': 9, 'października': 10, 'listopada': 11, 'grudnia': 12
                            }
                            try:
                                # Usuń przecinek i podziel
                                parts = date_match.replace(',', '').split()
                                if len(parts) >= 4:
                                    day = int(parts[0])
                                    month_name = parts[1]
                                    year = int(parts[2])
                                    time_part = parts[3]  # HH:MM:SS
                                    time_parts = time_part.split(':')
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