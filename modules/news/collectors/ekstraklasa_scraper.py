"""
Scraper dla polskich lig z 90minut.pl
Pobiera aktualną tabelę Ekstraklasy, I Ligi i II Ligi poprzez scraping
"""

import requests
from bs4 import BeautifulSoup


def get_emblems_map(id_rozgrywki):
    """
    Pobiera mapę emblematów drużyn z 90minut.pl
    
    Args:
        id_rozgrywki (str): ID rozgrywek (14072 dla Ekstraklasy, 14073 dla I Ligi, 14074 dla II Ligi)
    
    Returns:
        dict: Słownik {nazwa_drużyny: url_emblemu}
    """
    try:
        url = f"http://www.90minut.pl/skarb.php?id_rozgrywki={id_rozgrywki}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        emblems_map = {}
        
        # Szukamy wszystkich obrazków na stronie
        all_imgs = soup.find_all('img')
        
        for img in all_imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Logo drużyn są w katalogu /logo/dobazy/
            if '/logo/dobazy/' in src and alt:
                emblems_map[alt] = src
        
        return emblems_map
    except Exception as e:
        print(f"Błąd pobierania emblematów: {e}")
        return {}


def get_90minut_table(url, id_rozgrywki):
    """
    Pobiera tabelę ligową ze strony 90minut.pl wraz z emblemami
    
    Args:
        url (str): URL do tabeli ligowej
        id_rozgrywki (str): ID rozgrywek dla emblematów
    
    Returns:
        dict: Słownik zawierający:
            - standings: lista drużyn z danymi (pozycja, nazwa, mecze, punkty, etc.)
            - error: komunikat błędu (jeśli wystąpił)
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pobierz mapę emblematów
        emblems_map = get_emblems_map(id_rozgrywki)
        
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
                                    # Format zgodny z europejskimi ligami (z polem team.crest)
                                    team_data = {
                                        'position': str(len(dane_ligi) + 1),
                                        'team': {
                                            'name': nazwa,
                                            'crest': emblems_map.get(nazwa, '')
                                        },
                                        'played_games': mecze,
                                        'points': punkty,
                                        'won': zwyciestwa,
                                        'draw': remisy,
                                        'lost': porazki,
                                        'goals': bramki
                                    }
                                    dane_ligi.append(team_data)
                            except Exception as e:
                                print(f"[Błąd parsowania wiersza: {e}]")
                    
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
    Pobiera tabelę Ekstraklasy ze strony 90minut.pl z emblemami
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14072.html", "14072")


def get_first_league_table():
    """
    Pobiera tabelę I Ligi ze strony 90minut.pl z emblemami
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14073.html", "14073")


def get_second_league_table():
    """
    Pobiera tabelę II Ligi ze strony 90minut.pl z emblemami
    
    Returns:
        dict: Słownik zawierający standings i error
    """
    return get_90minut_table("http://www.90minut.pl/liga/1/liga14074.html", "14074")
