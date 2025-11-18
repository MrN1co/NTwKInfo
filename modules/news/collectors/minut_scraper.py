import requests
from bs4 import BeautifulSoup


def get_minut_news(limit=10):
    """
    Pobiera najnowsze informacje z 90minut.pl (prosta, defensywna implementacja).
    Zwraca listę słowników z kluczami: 'title', 'link', 'image' (może być None).
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

            news_list.append({
                'title': title,
                'link': link,
                'image': image_url
            })

        return news_list

    except requests.RequestException:
        return []
    except Exception:
        return []