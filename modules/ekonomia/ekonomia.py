from datetime import date
from flask import Flask, render_template
from modules.ekonomia.klasy_api_obsluga.Manager import Manager
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import modules.ekonomia.api_testy as api_testy
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus

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

def ekonomia():
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

    # Przygotuj wszystkie waluty oprócz tych które są już na górze (EUR, CHF, USD)
    excluded_currencies = {'EUR', 'CHF', 'USD'}
    all_currencies_for_tiles = {}
    for code in currency_codes:
        if code.upper() not in excluded_currencies:
            rate = currency_rates.get(code.upper())
            if rate:
                all_currencies_for_tiles[code.upper()] = rate

    return render_template('ekonomia/index.html',
                           kurs_walut=kurs_walut,
                           wykres_waluty=wykres_waluty,
                           wykres_zlota=wykres_zlota,
                           cena_zlota=cena_zlota,
                           currency_codes=currency_codes,
                           currency_rates=currency_rates,
                           all_currencies_for_tiles=all_currencies_for_tiles)