import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def get_przegladsportowy_news(limit=10):
    """
    Pobiera najnowsze informacje ze strony krakowskiej policji
    Zwraca listę słowników z kluczami: 'title', 'link', 'image', 'date', 'tags'.
    """
    url = 'https://krakow.policja.gov.pl/kr1/aktualnosci'
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

            # Wejdź na stronę artykułu i pobierz timestamp
            date = None
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Szukaj daty - może być w <time> lub meta tagach
                    date_elem = article_soup.find('time')
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        if not date_text and date_elem.has_attr('datetime'):
                            date_text = date_elem['datetime']
                        
                        if date_text:
                            # Obsługa "dzisiaj" i "wczoraj"
                            if 'dzisiaj' in date_text.lower():
                                today = datetime.now()
                                time_part = re.search(r'\d{1,2}:\d{2}', date_text)
                                if time_part:
                                    date = f"{today.strftime('%d.%m.%Y')} {time_part.group()}"
                                else:
                                    date = today.strftime('%d.%m.%Y %H:%M')
                            elif 'wczoraj' in date_text.lower():
                                yesterday = datetime.now() - timedelta(days=1)
                                time_part = re.search(r'\d{1,2}:\d{2}', date_text)
                                if time_part:
                                    date = f"{yesterday.strftime('%d.%m.%Y')} {time_part.group()}"
                                else:
                                    date = yesterday.strftime('%d.%m.%Y %H:%M')
                            else:
                                date = date_text
                    
                    # Jeśli nie ma <time>, szukaj w meta
                    if not date:
                        date_meta = article_soup.find('meta', property='article:published_time')
                        if not date_meta:
                            date_meta = article_soup.find('meta', attrs={'name': 'pubdate'})
                        if date_meta:
                            date = date_meta.get('content', '')
            except Exception as e:
                pass
            
            # Jeśli nie udało się pobrać daty, użyj aktualnego czasu
            if not date:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            news_list.append({
                'title': title,
                'link': link,
                'image': image_url,
                'date': date,
                'tags': ['sport']
            })

        return news_list

    except requests.RequestException:
        return []
    except Exception:
        return []