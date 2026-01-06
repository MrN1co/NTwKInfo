from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient
from modules.ekonomia.klasy_api_obsluga.CurrencyRates import CurrencyRates
from modules.ekonomia.klasy_api_obsluga.GoldPrices import GoldPrices
from modules.ekonomia.klasy_api_obsluga.HistoricalData import HistoricalData
import matplotlib
# Use non-interactive Agg backend for server-side rendering
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

class Manager:
    def __init__(self):
        self.client = APIClient()
        self.currencies = CurrencyRates(self.client)
        self.gold = GoldPrices(self.client)
        self.history = HistoricalData(self.client)

    def update_all(self):
        """Update currency rates and gold prices"""
        print("Fetching current exchange rates...")
        rates = self.currencies.get_current_rates()
        print("Fetching current gold price...")
        gold_price = self.gold.get_current_price()
        return rates, gold_price

    def export_to_csv(self, df, filename):
        """Export DataFrame to CSV file"""
        df.to_csv(filename, index=False)
        print(f"Saved to {filename}")

    def plot_rates(self, df, code):
        """Plot currency rates over time"""
        df_code = df[df["code"] == code.upper()]
        if df_code.empty:
            print(f"No data for currency {code}")
            return
        df_code.plot(x="date", y="rate", title=f"{code.upper()} exchange rate")
        plt.xlabel("Date")
        plt.ylabel("PLN Rate")
        plt.show()

    def list_currencies(self, table: str = 'a'):
        """
        Get list of available currency codes from specified table.
        Returns sorted list of unique currency codes (e.g. ['EUR','USD']).
        """
        # Create temporary CurrencyRates object to avoid modifying self.currencies
        temp = CurrencyRates(self.client, tables=[table])
        entries = temp.get_currency_list()
        # entries is list of dicts {'code': 'EUR', 'table': 'a'}
        codes = sorted({e['code'].upper() for e in entries})
        return codes

    def create_plot_image(self, df, x_col='date', y_col='price', title=None, color='#fbc531', y_label=None, x_label='Date'):
        """
        Create plot from DataFrame and return base64-encoded PNG image.
        Useful for creating historical charts (e.g. gold prices) from API data.
        """
        import io, base64
        if df is None or df.empty:
            # Return empty chart with "No data" message
            fig, ax = plt.subplots(figsize=(10, 5), facecolor='#c2c9b6')
            ax.set_facecolor('#c2c9b6')
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', color='#2B370A')
            ax.tick_params(colors='#2B370A')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return encoded

        fig, ax = plt.subplots( figsize=(16, 7), facecolor='#c2c9b6')
        ax.set_facecolor('#c2c9b6')
        # Convert x_col to datetime for proper plotting
        try:
            x = pd.to_datetime(df[x_col])
        except Exception:
            x = df[x_col]
        y = df[y_col]

        ax.plot(x, y, color=color, linewidth=2)
        # Apply consistent styling
        ax.tick_params(colors='#2B370A')
        ax.set_xlabel(x_label, color='#2B370A')
        # Set y-label based on column type
        if y_label:
            ax.set_ylabel(y_label, color='#2B370A')
        else:
            ax.set_ylabel('Gold price [t oz]' if y_col == 'price' else y_col, color='#2B370A')
        fig.autofmt_xdate()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return encoded