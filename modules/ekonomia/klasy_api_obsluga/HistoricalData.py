from datetime import datetime, timedelta
from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient
import pandas as pd

class HistoricalData:
    def __init__(self, client: APIClient):
        self.client = client

    def get_historical_rates_df(self, tables=["a", "b"], years=3):
        """Pobiera historyczne kursy walut z tabel w DataFrame"""
        currencies = []
        for table in tables:
            url = f"{self.client.base_url}/exchangerates/tables/{table}/"
            data = self.client.get_json(url, {"format": "json"})
            if data and len(data) > 0:
                for r in data[0]["rates"]:
                    currencies.append({"code": r["code"], "table": table})

        end_date = datetime.today()
        start_date = end_date - timedelta(days=years*365)
        delta = timedelta(days=93)

        records = []
        for cur in currencies:
            code = cur["code"]
            table = cur["table"]
            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + delta, end_date)
                url = f"{self.client.base_url}/exchangerates/rates/{table}/{code}/{current_start.strftime('%Y-%m-%d')}/{current_end.strftime('%Y-%m-%d')}/"
                data = self.client.get_json(url, {"format": "json"})
                if data and "rates" in data:
                    for rate in data["rates"]:
                        records.append({
                            "date": rate["effectiveDate"],
                            "code": code.upper(),
                            "rate": rate.get("mid"),
                            "table": table
                        })
                current_start = current_end + timedelta(days=1)

        df = pd.DataFrame(records)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def get_historical_gold_prices(self, months=36):
        """Historyczne ceny złota za ostatnich 'months' miesięcy.

        API NBP ma limit zakresu ~93 dni, dlatego pobieramy dane w kawałkach
        (delta = 93 dni) i łączymy je w jeden DataFrame.
        Parametr `months` przyjmujemy jako przybliżenie (liczymy 30 dni na miesiąc).
        """
        end_date = datetime.today()
        start_date = end_date - timedelta(days=months * 30)
        delta = timedelta(days=93)
        records = []

        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + delta, end_date)
            url = f"{self.client.base_url}/cenyzlota/{current_start.strftime('%Y-%m-%d')}/{current_end.strftime('%Y-%m-%d')}/"
            data = self.client.get_json(url, {"format": "json"})
            if data:
                for entry in data:
                    records.append({"date": entry["data"], "price": entry["cena"]})
            current_start = current_end + timedelta(days=1)

        df = pd.DataFrame(records)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df

    # Note: get_historical_gold_prices now supports months-based ranges; explicit
    # range function removed to keep API simple (useful when switching to DB later).