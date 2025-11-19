from klasy_api_obsluga.APIClient import APIClient

class CurrencyRates:
    def __init__(self, client: APIClient, tables=["a", "b"]):
        self.client = client
        self.tables = []
        self.set_tables(tables)

    def set_tables(self, tables):
        """
        Zmienia listę tabel używanych do pobierania kursów.
        Sprawdza, czy wszystkie wpisane tabele są poprawne (a, b, c).
        """
        valid_tables = ["a", "b", "c"]
        self.tables = [t for t in tables if t in valid_tables]

    def get_current_rates(self):
        """Aktualne kursy walut z tabel wybranych w self.tables"""
        rates = {}
        for table in self.tables:
            url = f"{self.client.base_url}/exchangerates/tables/{table}/"
            data = self.client.get_json(url, {"format": "json"})
            if data and len(data) > 0:
                for r in data[0]["rates"]:
                    rates[r["code"].lower()] = r["mid"]
        return rates

    def get_currency_list(self):
        """Lista walut z tabel wybranych w self.tables"""
        currencies = []
        for table in self.tables:
            url = f"{self.client.base_url}/exchangerates/tables/{table}/"
            data = self.client.get_json(url, {"format": "json"})
            if data and len(data) > 0:
                for r in data[0]["rates"]:
                    currencies.append({"code": r["code"], "table": table})
        return currencies
    
    def update(self):
        """Aktualizuje słownik aktualnych kursów walut w self.rates"""
        self.rates = self.get_current_rates()
        return self.rates