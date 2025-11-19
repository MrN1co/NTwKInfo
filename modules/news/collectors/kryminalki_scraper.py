"""
Scraper dla wiadomości z kryminalki.pl
Pobiera najnowsze artykuły ze strony głównej
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time


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
            
            # Wyciągamy tytuł z miniaturki
            date = None
            if 'Data dodania artykułu:' in title_text:
                parts = title_text.split('Data dodania artykułu:')
                title = parts[0].strip()
            else:
                title = title_text
            
            # ZAWSZE wejdź na stronę artykułu aby pobrać datę
            try:
                article_response = requests.get(link, headers=headers, timeout=10)
                if article_response.status_code == 200:
                    article_soup = BeautifulSoup(article_response.content, 'html.parser')
                    
                    # Szukamy daty w <span class="fal fa-calendar-alt">
                    date_span = article_soup.find('span', class_='fal fa-calendar-alt')
                    if date_span and date_span.parent:
                        date_text = date_span.parent.get_text(strip=True)
                        
                        # Obsługa "dzisiaj" i "wczoraj"
                        if 'dzisiaj' in date_text.lower():
                            today = datetime.now()
                            time_part = date_text.split('dzisiaj')[-1].strip()
                            if time_part:
                                date = f"{today.strftime('%d.%m.%Y')} {time_part}"
                            else:
                                date = today.strftime('%d.%m.%Y %H:%M')
                        elif 'wczoraj' in date_text.lower():
                            yesterday = datetime.now() - timedelta(days=1)
                            time_part = date_text.split('wczoraj')[-1].strip()
                            if time_part:
                                date = f"{yesterday.strftime('%d.%m.%Y')} {time_part}"
                            else:
                                date = yesterday.strftime('%d.%m.%Y %H:%M')
                        else:
                            date = date_text
            except Exception as e:
                pass
            
            # Pomijamy duplikaty
            if any(n['link'] == link for n in news_list):
                continue
            
            # Konwertuj datę na timestamp
            timestamp = None
            display_date = date  # Data do wyświetlenia
            
            if date:
                # Usuń "dzisiaj" i "wczoraj" z wyświetlanej daty
                if date and ('dzisiaj' in date.lower() or 'wczoraj' in date.lower()):
                    # Jeśli data nadal zawiera te słowa, to coś poszło nie tak w parsowaniu
                    # Spróbuj naprawić
                    if 'dzisiaj' in date.lower():
                        today = datetime.now()
                        time_part = date.lower().split('dzisiaj')[-1].strip()
                        date = f"{today.strftime('%d.%m.%Y')} {time_part}"
                    elif 'wczoraj' in date.lower():
                        yesterday = datetime.now() - timedelta(days=1)
                        time_part = date.lower().split('wczoraj')[-1].strip()
                        date = f"{yesterday.strftime('%d.%m.%Y')} {time_part}"
                
                # Normalizuj datę - usuń przecinki i dodatkowe spacje
                # '19.11.2025 , 16:32' -> '19.11.2025 16:32'
                date = date.replace(',', '').replace('  ', ' ').strip()
                display_date = date
                
                try:
                    # Format: DD.MM.YYYY HH:MM
                    dt = datetime.strptime(date, '%d.%m.%Y %H:%M')
                    timestamp = int(dt.timestamp())
                except Exception:
                    timestamp = int(time.time())
            
            # Jeśli nadal nie ma timestampa, użyj aktualnego czasu
            if not timestamp:
                timestamp = int(time.time())
                if not display_date:
                    display_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            
            news_list.append({
                'title': title,
                'link': link,
                'image': image_url if image_url else None,
                'date': display_date,
                'timestamp': timestamp,
                'tags': ['kryminalne']
            })
        
        return news_list
        
    except requests.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
        return []
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return []
