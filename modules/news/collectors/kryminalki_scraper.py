"""
Scraper dla wiadomości z kryminalki.pl
Pobiera najnowsze artykuły ze strony głównej
"""

import requests
from bs4 import BeautifulSoup


def get_kryminalki_news(limit=10):
    """
    Pobiera najnowsze wiadomości z kryminalki.pl
    
    Args:
        limit (int): Maksymalna liczba wiadomości do pobrania
    
    Returns:
        list: Lista słowników z wiadomościami zawierających:
            - title: tytuł artykułu
            - link: link do artykułu
            - image: URL do obrazka (jeśli dostępny)
    """
    url = 'https://www.kryminalki.pl'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Błąd pobierania strony: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news_list = []
        
        # Znajdujemy sekcję main
        main_section = soup.find('main')
        
        if not main_section:
            print("Nie znaleziono sekcji main na stronie")
            return []
        
        # Znajdujemy wszystkie artykuły
        articles = main_section.find_all('a', href=True, limit=limit * 3)
        
        for article in articles:
            if len(news_list) >= limit:
                break
            
            # Pobieramy link
            link = article.get('href', '')
            if not link or not link.startswith('/artykul/'):
                continue
            
            # Konwertujemy relatywny link na absolutny
            link = f'https://www.kryminalki.pl{link}'
            
            # Pobieramy obrazek
            img = article.find('img')
            image_url = img.get('src', '') if img else ''
            
            # Pobieramy tytuł - szukamy w tekście wewnątrz linka
            title_text = article.get_text(strip=True)
            
            # Pomijamy bardzo krótkie teksty (prawdopodobnie nie są tytułami)
            if not title_text or len(title_text) < 10:
                continue
            
            # Wyciągamy datę jeśli jest
            date = None
            if 'Data dodania artykułu:' in title_text:
                parts = title_text.split('Data dodania artykułu:')
                title = parts[0].strip()
                if len(parts) > 1:
                    # Wyciągamy tylko datę i godzinę (przed "Liczba komentarzy")
                    date_part = parts[1]
                    if 'Liczba komentarzy' in date_part:
                        date = date_part.split('Liczba komentarzy')[0].strip()
                    else:
                        date = date_part.strip()
            else:
                title = title_text
            
            # Pomijamy duplikaty
            if any(n['link'] == link for n in news_list):
                continue
            
            news_list.append({
                'title': title,
                'link': link,
                'image': image_url if image_url else None,
                'date': date,
                'tags': ['kryminalne']
            })
        
        return news_list
        
    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
        return []
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return []
