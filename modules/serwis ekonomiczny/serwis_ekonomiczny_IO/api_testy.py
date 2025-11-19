import requests

# === USTAWIENIA PODSTAWOWE ===
BASE_URL = "https://api.nbp.pl/api"

def get_json(url, params=None):
    """Wysyła zapytanie GET i zwraca dane JSON (z obsługą błędów)."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Błąd HTTP: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Błąd połączenia: {e}")
    except ValueError:
        print("❌ Nie udało się sparsować odpowiedzi JSON.")
    return None


# === 1️⃣ AKTUALNY KURS POJEDYNCZEJ WALUTY ===
def get_current_rate(table: str, code: str):
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/"
    return get_json(url, {"format": "json"})


# === 2️⃣ KURS WALUTY Z OKREŚLONEJ DATY ===
def get_rate_by_date(table: str, code: str, date: str):
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/{date}/"
    return get_json(url, {"format": "json"})


# === 3️⃣ SERIA KURSÓW WALUTY (ostatnie N notowań) ===
def get_last_rates(table: str, code: str, count: int):
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/last/{count}/"
    return get_json(url, {"format": "json"})


# === 4️⃣ KOMPLETNA TABELA KURSÓW TYPU A/B/C ===
def get_current_table(table: str):
    url = f"{BASE_URL}/exchangerates/tables/{table}/"
    return get_json(url, {"format": "json"})


# === 5️⃣ TABELA Z KONKRETNEJ DATY ===
def get_table_by_date(table: str, date: str):
    url = f"{BASE_URL}/exchangerates/tables/{table}/{date}/"
    return get_json(url, {"format": "json"})


# === 6️⃣ TABELA Z ZAKRESU DAT ===
def get_tables_range(table: str, start_date: str, end_date: str):
    url = f"{BASE_URL}/exchangerates/tables/{table}/{start_date}/{end_date}/"
    return get_json(url, {"format": "json"})


# === 7️⃣ CENA ZŁOTA (aktualna) ===
def get_gold_price():
    url = f"{BASE_URL}/cenyzlota/"
    return get_json(url, {"format": "json"})


# === 8️⃣ CENA ZŁOTA Z DATY ===
def get_gold_price_by_date(date: str):
    url = f"{BASE_URL}/cenyzlota/{date}/"
    return get_json(url, {"format": "json"})


# === 9️⃣ CENY ZŁOTA Z ZAKRESU DAT ===
def get_gold_prices_range(start_date: str, end_date: str):
    url = f"{BASE_URL}/cenyzlota/{start_date}/{end_date}/"
    return get_json(url, {"format": "json"})


# === 🔟 FUNKCJA TESTUJĄCA WSZYSTKO ===
def test_nbp_api():
    print("=== 🔹 Test: aktualny kurs USD (tabela A) ===")
    data = get_current_rate("a", "usd")
    if data:
        rate = data["rates"][0]
        print(f"{data['currency']} ({data['code']}) = {rate['mid']} PLN")

    print("\n=== 🔹 Test: ostatnie 5 kursów EUR ===")
    data = get_last_rates("a", "eur", 5)
    if data:
        for r in data["rates"]:
            print(f"{r['effectiveDate']}: {r['mid']} PLN")

    print("\n=== 🔹 Test: aktualna tabela typu A ===")
    data = get_current_table("a")
    if data:
        print(f"Numer tabeli: {data[0]['no']}, Data: {data[0]['effectiveDate']}")
        print(f"Ilość walut: {len(data[0]['rates'])}")

    print("\n=== 🔹 Test: aktualna cena złota ===")
    data = get_gold_price()
    if data:
        print(f"Data: {data[0]['data']}, Cena: {data[0]['cena']} PLN/g")


# === URUCHOMIENIE TESTU ===
if __name__ == "__main__":
    test_nbp_api()
