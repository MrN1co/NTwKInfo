"""
Scraper dla polskich lig z 90minut.pl
Pobiera aktualną tabelę Ekstraklasy, I Ligi i II Ligi poprzez scraping
"""

import requests
from bs4 import BeautifulSoup


def get_90minut_table(url):
    """
    Pobiera tabelę ligową ze strony 90minut.pl
    
    Args:
        url (str): URL do tabeli ligowej
    
    Returns:
        dict: Słownik zawierający:
            - standings: lista drużyn z danymi (pozycja, nazwa, mecze, punkty, etc.)
            - error: komunikat błędu (jeśli wystąpił)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        dane_ligi = []
        
        # Szukamy tabeli z nagłówkami ligowymi (M, Pkt, etc.)
        all_tables = soup.find_all('table')
        
        for table in all_tables:
            header_row = table.find('tr')
            
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                
                if 'M' in headers or 'Pkt' in headers or any('Pkt' in h for h in headers):
                    rows = table.find_all('tr')[1:]
                    
                    for row in rows:
                        cols = row.find_all('td')
                        
                        if len(cols) >= 7:
                            try:
                                nazwa_idx = 1
                                nazwa_cell = cols[nazwa_idx]
                                team_link = nazwa_cell.find('a')
                                nazwa = team_link.text.strip() if team_link else nazwa_cell.text.strip()
                                
                                mecze = cols[2].text.strip()
                                punkty = cols[3].text.strip()
                                zwyciestwa = cols[4].text.strip()
                                remisy = cols[5].text.strip()
                                porazki = cols[6].text.strip()
                                bramki = cols[7].text.strip() if len(cols) > 7 else ''
                                
                                if nazwa and mecze.isdigit():
                                    dane_ligi.append({
                                        'position': str(len(dane_ligi) + 1),
                                        'team_name': nazwa,
                                        'played_games': mecze,
                                        'points': punkty,
                                        'won': zwyciestwa,
                                        'draw': remisy,
                                        'lost': porazki,
                                        'goals': bramki
                                    })
                            except:
                                continue
                    
                    if dane_ligi:
                        break
        
        if dane_ligi:
            return {
                'standings': dane_ligi,
                'error': None
            }
        else:
            return {
                'standings': [],
                'error': 'Nie udało się znaleźć tabeli ligowej na stronie'
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'standings': [],
            'error': f'Błąd połączenia ze stroną: {str(e)}'
        }
    except Exception as e:
        return {
            'standings': [],
            'error': f'Błąd podczas przetwarzania danych: {str(e)}'
        }


def get_ekstraklasa_table():
    """
    Pobiera tabelę Ekstraklasy ze strony 90minut.pl
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14072.html")


def get_first_league_table():
    """
    Pobiera tabelę I Ligi ze strony 90minut.pl
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14073.html")


def get_second_league_table():
    """
    Pobiera tabelę II Ligi ze strony 90minut.pl
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14074.html")
