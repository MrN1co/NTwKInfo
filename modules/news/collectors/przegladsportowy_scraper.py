import requests
from bs4 import BeautifulSoup
from datetime import datetime


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

            # Używamy aktualnego czasu jako daty - przegladsportowy nie udostępnia dat na liście
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