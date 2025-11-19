import requests
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://api.nbp.pl/api"

def get_response_json(url, params=None):
    """Wysyła odpowiednie zapytanie GET i zwraca dane JSON (z obsługą błędów)"""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Błąd: {e}")
    return None

def get_current_gold_price():
    """
    Zwraca aktualną cenę złota w PLN/g jako liczbę zmiennoprzecinkową
    """
    url = f"{BASE_URL}/cenyzlota/"
    data = get_response_json(url, params={"format": "json"})
    
    if data and len(data) > 0:
        return data[0]["cena"]  # cena w PLN/g
    else:
        print("Brak danych o złocie.")
        return None
    
def get_all_current_rates():
    """
    Zwraca słownik z aktualnymi kursami wszystkich walut z tabel A i B.
    Format: {kod_waluty: kurs_PLN}
    """
    rates_dict = {}

    # Pętla po tabelach A i B
    for table in ["a", "b"]:
        url = f"{BASE_URL}/exchangerates/tables/{table}/"
        data = get_response_json(url, params={"format": "json"})
        
        if data and len(data) > 0:
            for rate in data[0]["rates"]:
                rates_dict[rate["code"].lower()] = rate["mid"]  # kod -> kurs PLN
    
    return rates_dict

def get_all_current_rates_list():
    """Pobiera listę wszystkich walut z tabel A i B"""
    currencies = []
    for table in ["a", "b"]:
        url = f"{BASE_URL}/exchangerates/tables/{table}/"
        data = get_response_json(url, params={"format": "json"})
        if data and len(data) > 0:
            for rate in data[0]["rates"]:
                currencies.append({"code": rate["code"], "table": table})
    return currencies

def get_historical_rates_df(years: int = 3):
    """
    Pobiera historyczne kursy wszystkich walut z tabel A i B z ostatnich 'years' lat.
    Zwraca pandas DataFrame z kolumnami: date, code, rate, table
    """
    currencies = get_all_current_rates_list()
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years*365)
    delta = timedelta(days=93)  # maks zakres API

    records = [] 

    for cur in currencies:
        code = cur["code"]
        table = cur["table"]
        current_start = start_date

        while current_start < end_date:
            current_end = min(current_start + delta, end_date)
            print(f"Pobieranie danych dla {code} od {current_start.strftime('%Y-%m-%d')} do {current_end.strftime('%Y-%m-%d')}")
            url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/{current_start.strftime('%Y-%m-%d')}/{current_end.strftime('%Y-%m-%d')}/"
            data = get_response_json(url, params={"format": "json"})
            
            if data and "rates" in data:
                for rate in data["rates"]:
                    records.append({
                        "date": rate["effectiveDate"],
                        "code": code.upper(),
                        "rate": rate.get("mid"),
                        "table": table
                    })

            current_start = current_end + timedelta(days=1)

    # Tworzymy DataFrame z listy wierszy
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df

def get_historical_gold_prices(years: int = 3):
    """
    Pobiera historyczne ceny złota z ostatnich 'years' lat.
    Zwraca słownik: {data: cena_PLN}
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years*365)
    delta = timedelta(days=93)  # maks zakres API
    gold_dict = {}

    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + delta, end_date)
        url = f"{BASE_URL}/cenyzlota/{current_start.strftime('%Y-%m-%d')}/{current_end.strftime('%Y-%m-%d')}/"
        data = get_response_json(url, params={"format": "json"})
        
        if data:
            for entry in data:
                gold_dict[entry["data"]] = entry["cena"]

        current_start = current_end + timedelta(days=1)

    return gold_dict

if __name__ == "__main__":
    #print("Aktualna cena złota (PLN/g):", get_current_gold_price())
    #print("Aktualne kursy walut:", get_all_current_rates())
    print("Pobieranie historycznych kursów walut...")
    df_rates = get_historical_rates_df(years=1)
    print(df_rates.head())
    #print("Pobieranie historycznych cen złota...")
    #gold_prices = get_historical_gold_prices(years=1)
    #print(list(gold_prices.items())[:5])