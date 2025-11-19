from datetime import date
from flask import Flask, render_template
from klasy_api_obsluga.Manager import Manager
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import api_testy
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus
# Add DB imports
try:
    from dotenv import load_dotenv
    load_dotenv()  # optional: will load .env file if present
except Exception:
    pass

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CHANGED: database configuration and initialization ---
# Prefer DATABASE_URL if set (e.g. full URI), otherwise build from parts:
# Set these environment variables (or put them in .env):
# DATABASE_URL (optional; jeśli ustawione, jest używane bez zmian)
# LUB
# DB_TYPE (np. postgresql), DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
#
# Example .env:
# DB_TYPE=postgresql
# DB_USER=youruser
# DB_PASS=yourpass
# DB_HOST=db.example.com
# DB_PORT=5432
# DB_NAME=yourdb
db_url = os.getenv('DATABASE_URL')
if not db_url:
    db_type = os.getenv('DB_TYPE', 'postgresql')
    user = os.getenv('DB_USER', '')
    pwd = os.getenv('DB_PASS', '')
    host = os.getenv('DB_HOST', '')
    port = os.getenv('DB_PORT', '5432')
    dbname = os.getenv('DB_NAME', '')

    if all([db_type, user, pwd, host, dbname]):
        # safely quote user/password (escape special chars)
        uq = quote_plus(user)
        pq = quote_plus(pwd)
        db_url = f"{db_type}://{uq}:{pq}@{host}:{port}/{dbname}"
    else:
        # fallback to local sqlite if not enough data provided
        db_url = 'sqlite:///d:/programowanie/serwis ekonomiczny/serwis_ekonomiczny_IO/data.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    value = db.Column(db.Float, nullable=True)

# Create tables and insert a sample row if table empty
with app.app_context():
    db.create_all()
    if Item.query.first() is None:
        sample = Item(name='Przykladowy rekord', value=123.45)
        db.session.add(sample)
        db.session.commit()

# Funkcja pomocnicza do generowania wykresów
def generate_plot(color='#c2c9b6', title='Widok w skali roku'):
    x = np.linspace(0, 20, 100)
    y = 4.2 + 0.1 * np.sin(x) + 0.05 * np.random.randn(100)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#c2c9b6')
    ax.plot(x, y, color=color, linewidth=2)
    ax.set_facecolor('#c2c9b6')
    ax.set_title(title, color= '#2B370A')
    ax.tick_params(colors='#2B370A')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

@app.route('/')
def index():
    kurs_walut = {
        'EUR': 4.24,
        'CHF': 4.57,
        'USD': 3.64
    }
    wykres_waluty = generate_plot('#6c7c40', 'Widok w skali roku')

    # Pobierz historyczne ceny złota za ostatni miesiąc i wygeneruj wykres
    mgr = Manager()
    # Pobierz historyczne ceny złota za ostatni miesiąc (1 miesiąc)
    gold_df = mgr.history.get_historical_gold_prices(months=1)
    wykres_zlota = mgr.create_plot_image(gold_df, x_col='date', y_col='price', color='#6c7c40')

    cena_zlota = api_testy.get_gold_price()[0]['cena']

    # Pobierz listę walut z Managera i przekaż do szablonu — progressive enhancement
    mgr = Manager()
    currency_codes = mgr.list_currencies()
    # Pobierz aktualne kursy z Managera (słownik kod->kurs w PLN)
    raw_rates = mgr.currencies.get_current_rates()
    # Normalizuj klucze do wielkich liter i dodaj PLN=1
    currency_rates = {k.upper(): v for k, v in raw_rates.items()}
    currency_rates['PLN'] = 1.0

    return render_template('index.html',
                           kurs_walut=kurs_walut,
                           wykres_waluty=wykres_waluty,
                           wykres_zlota=wykres_zlota,
                           cena_zlota=cena_zlota,
                           currency_codes=currency_codes,
                           currency_rates=currency_rates)

# --- NEW: simple route to fetch DB items as JSON ---
@app.route('/db-test')
def db_test():
    items = Item.query.all()
    data = [{'id': it.id, 'name': it.name, 'value': it.value} for it in items]
    return {'items': data}

if __name__ == '__main__':
    app.run(debug=True)
