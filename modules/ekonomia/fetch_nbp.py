import os
import json
from datetime import datetime, timedelta
import requests

## ustawienia
# folder do zapisywania JSON-ów
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', '..', 'data', 'economics')
os.makedirs(DATA_DIR, exist_ok=True)

YEAR = datetime.today().year
end_date = datetime.today()
start_date = end_date - timedelta(days=365)


def get_daily_currencies():
    url = "https://api.nbp.pl/api/exchangerates/tables/a/?format=json"
    res = requests.get(url)
    if res.status_code != 200:
        print("Nie udało się pobrać tabeli A")
        return []
    data = res.json()
    # data[0]['rates'] to lista słowników z 'code' i 'currency'
    codes = [r['code'] for r in data[0]['rates']]
    return codes

ALL_CODES = get_daily_currencies()  # pobierz wszystkie waluty z tabeli A
# wybierz tylko top 10 najważniejszych, które są w tabeli
TOP10_CODES = ['EUR', 'USD', 'CHF', 'GBP', 'JPY', 'AUD', 'CAD', 'NOK', 'SEK', 'DKK']
CURRENCY_CODES = [c for c in TOP10_CODES if c in ALL_CODES]

def fetch_nbprates(currency_code):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    # NBP API pozwala max 93 dni na jedno żądanie, więc dzielimy na okresy
    periods = []
    current_start = start_date
    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=92), end_date)
        periods.append( (current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d')) )
        current_start = current_end + timedelta(days=1)
    
    all_rates = []
    for start, end in periods:
        url = f'https://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/{start}/{end}/?format=json'
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            all_rates.extend(data.get('rates', []))
        else:
            print(f'Błąd pobrania {currency_code}: {res.status_code}')
    
    # filtrowanie powtarzających się dat i rekordów spoza ostatniego roku
    one_year_ago = datetime.today() - timedelta(days=365)
    unique_rates = []
    seen_dates = set()
    for rate in all_rates:
        d = datetime.strptime(rate['effectiveDate'], '%Y-%m-%d')
        if d >= one_year_ago and rate['effectiveDate'] not in seen_dates:
            seen_dates.add(rate['effectiveDate'])
            unique_rates.append(rate)
    
    return unique_rates


def fetch_gold():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    url = f"https://api.nbp.pl/api/cenyzlota/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
    res = requests.get(url)
    if res.status_code != 200:
        print("Nie udało się pobrać cen złota")
        return []
    data = res.json()
    
    gold_data = [ {'date': r['data'], 'price': r['cena']} for r in data ]
    return gold_data

def update_json(file_path, new_data, key_date):
    """Łączy nowe dane z istniejącym JSON-em, usuwa powtarzające się daty"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    else:
        existing = []

    # dodaj tylko brakujące rekordy
    existing_dates = {r[key_date] for r in existing}
    for record in new_data:
        if record[key_date] not in existing_dates:
            existing.append(record)

    # posortuj po dacie
    existing.sort(key=lambda x: x[key_date])

# usuń rekordy starsze niż 1 rok od dziś
    one_year_ago = datetime.today() - timedelta(days=365)
    existing = [r for r in existing if datetime.strptime(r[key_date], '%Y-%m-%d') >= one_year_ago]


    # zapisz z powrotem
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)

def run_update():
    # waluty
    for code in CURRENCY_CODES:
        rates = fetch_nbprates(code)
        path = os.path.join(DATA_DIR, f'{code}.json')
        update_json(path, rates, key_date='effectiveDate')
        print(f'{code} zaktualizowane w {path}')

    # złoto
    gold = fetch_gold()
    path_gold = os.path.join(DATA_DIR, f'gold.json')
    update_json(path_gold, gold, key_date='date')
    print(f'Złoto zaktualizowane w {path_gold}')

if __name__ == '__main__':
    run_update()
