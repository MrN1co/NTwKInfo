import requests

# === BASIC SETTINGS ===
BASE_URL = "https://api.nbp.pl/api"

def get_json(url, params=None):
    """Send GET request and return JSON data with error handling"""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except ValueError:
        print("❌ Failed to parse JSON response.")
    return None


# === CURRENCY RATE FUNCTIONS ===
def get_current_rate(table: str, code: str):
    """Get current exchange rate for single currency"""
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/"
    return get_json(url, {"format": "json"})


def get_rate_by_date(table: str, code: str, date: str):
    """Get currency rate from specific date"""
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/{date}/"
    return get_json(url, {"format": "json"})


def get_last_rates(table: str, code: str, count: int):
    """Get last N currency rates"""
    url = f"{BASE_URL}/exchangerates/rates/{table}/{code}/last/{count}/"
    return get_json(url, {"format": "json"})


def get_current_table(table: str):
    """Get complete currency table (A/B/C)"""
    url = f"{BASE_URL}/exchangerates/tables/{table}/"
    return get_json(url, {"format": "json"})


def get_table_by_date(table: str, date: str):
    """Get currency table from specific date"""
    url = f"{BASE_URL}/exchangerates/tables/{table}/{date}/"
    return get_json(url, {"format": "json"})


def get_tables_range(table: str, start_date: str, end_date: str):
    """Get currency tables from date range"""
    url = f"{BASE_URL}/exchangerates/tables/{table}/{start_date}/{end_date}/"
    return get_json(url, {"format": "json"})


# === GOLD PRICE FUNCTIONS ===
def get_gold_price():
    """Get current gold price"""
    url = f"{BASE_URL}/cenyzlota/"
    return get_json(url, {"format": "json"})


def get_gold_price_by_date(date: str):
    """Get gold price from specific date"""
    url = f"{BASE_URL}/cenyzlota/{date}/"
    return get_json(url, {"format": "json"})


def get_gold_prices_range(start_date: str, end_date: str):
    """Get gold prices from date range"""
    url = f"{BASE_URL}/cenyzlota/{start_date}/{end_date}/"
    return get_json(url, {"format": "json"})


# === TEST FUNCTION ===
def test_nbp_api():
    """Test all NBP API functions"""
    print("=== 🔹 Test: current USD rate (table A) ===")
    data = get_current_rate("a", "usd")
    if data:
        rate = data["rates"][0]
        print(f"{data['currency']} ({data['code']}) = {rate['mid']} PLN")

    print("\n=== 🔹 Test: last 5 EUR rates ===")
    data = get_last_rates("a", "eur", 5)
    if data:
        for r in data["rates"]:
            print(f"{r['effectiveDate']}: {r['mid']} PLN")

    print("\n=== 🔹 Test: current table A ===")
    data = get_current_table("a")
    if data:
        print(f"Table number: {data[0]['no']}, Date: {data[0]['effectiveDate']}")
        print(f"Currency count: {len(data[0]['rates'])}")

    print("\n=== 🔹 Test: current gold price ===")
    data = get_gold_price()
    if data:
        print(f"Date: {data[0]['data']}, Price: {data[0]['cena']} t oz")


# === RUN TESTS ===
if __name__ == "__main__":
    test_nbp_api()
