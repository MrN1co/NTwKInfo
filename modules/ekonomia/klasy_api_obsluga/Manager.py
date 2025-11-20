from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient
from modules.ekonomia.klasy_api_obsluga.CurrencyRates import CurrencyRates
from modules.ekonomia.klasy_api_obsluga.GoldPrices import GoldPrices
from modules.ekonomia.klasy_api_obsluga.HistoricalData import HistoricalData
import matplotlib.pyplot as plt
import pandas as pd

class Manager:
    def __init__(self):
        self.client = APIClient()
        self.currencies = CurrencyRates(self.client)
        self.gold = GoldPrices(self.client)
        self.history = HistoricalData(self.client)

    def update_all(self):
        """Aktualizacja danych walut i złota"""
        print("Pobieranie aktualnych kursów walut...")
        rates = self.currencies.get_current_rates()
        print("Pobieranie aktualnej ceny złota...")
        gold_price = self.gold.get_current_price()
        return rates, gold_price

    def export_to_csv(self, df, filename):
        df.to_csv(filename, index=False)
        print(f"Zapisano do {filename}")

    def plot_rates(self, df, code):
        df_code = df[df["code"] == code.upper()]
        if df_code.empty:
            print(f"Brak danych dla waluty {code}")
            return
        df_code.plot(x="date", y="rate", title=f"Kurs {code.upper()} w czasie")
        plt.xlabel("Data")
        plt.ylabel("Kurs PLN")
        plt.show()

    def list_currencies(self, table: str = 'a'):
        """
        Zwraca listę kodów walut dostępnych w zadanej tabeli (domyślnie 'a').
        Nie modyfikuje stanu obiektu `self.currencies` — tworzy krótkotrwały
        obiekt `CurrencyRates` dla podanej tabeli i pobiera listę.

        Zwracana wartość: posortowana lista unikalnych kodów walut (np. ['EUR','USD']).
        """
        # Tworzymy tymczasowy obiekt CurrencyRates, by nie zmieniać self.currencies
        temp = CurrencyRates(self.client, tables=[table])
        entries = temp.get_currency_list()
        # entries to lista słowników {'code': 'EUR', 'table': 'a'}
        codes = sorted({e['code'].upper() for e in entries})
        return codes

    def create_plot_image(self, df, x_col='date', y_col='price', title=None, color='#fbc531', y_label=None):
        """
        Tworzy wykres z podanego DataFrame (kolumny x_col i y_col) i zwraca obraz PNG
        zakodowany base64 (bez nagłówka).

        Przydatne do tworzenia wykresów historycznych (np. cen złota) z danych pobranych
        z API lub bazy danych.
        """
        import io, base64
        if df is None or df.empty:
            # Zwróć pusty obrazek (można też zwrócić None)
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#c2c9b6')
            ax.set_facecolor('#c2c9b6')
            ax.text(0.5, 0.5, 'Brak danych', ha='center', va='center', color='#2B370A')
            ax.tick_params(colors='#2B370A')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return encoded

        fig, ax = plt.subplots( figsize=(16, 7), facecolor='#c2c9b6')
        ax.set_facecolor('#c2c9b6')
        # Ensure x_col is datetime for plotting
        try:
            x = pd.to_datetime(df[x_col])
        except Exception:
            x = df[x_col]
        y = df[y_col]

        ax.plot(x, y, color=color, linewidth=2)
        # Styling similar to generate_plot
        ax.tick_params(colors='#2B370A')
        # Do not set a title (user requested no title)
        ax.set_xlabel('Data', color='#2B370A')
        # Determine y-label: if provided use it, otherwise for price use gold label
        if y_label:
            ax.set_ylabel(y_label, color='#2B370A')
        else:
            ax.set_ylabel('Cena złota [t oz]' if y_col == 'price' else y_col, color='#2B370A')
        fig.autofmt_xdate()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return encoded