from datetime import date
from flask import Flask, render_template, jsonify
from modules.ekonomia.klasy_api_obsluga.Manager import Manager
import io
import base64
import matplotlib

# Use non-interactive Agg backend for server-side image generation
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import modules.ekonomia.api_testy as api_testy
from modules.ekonomia import fetch_nbp
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus
import json
import pandas as pd

def load_currency_json(currency_code):
    """Load historical currency data from JSON file
    
    Args:
        currency_code: Currency code (e.g., 'EUR', 'USD')
        
    Returns:
        DataFrame with columns [date, rate] or None if file not found
    """
    try:
        json_path = os.path.join('data', 'economics', f'{currency_code.upper()}.json')
        
        if not os.path.exists(json_path):
            return None
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse JSON into DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['effectiveDate'])
        df['rate'] = df['mid'].astype(float)
        
        # Keep only needed columns and sort by date
        df = df[['date', 'rate']].sort_values('date')
        
        return df
        
    except Exception as e:
        print(f"Error loading JSON for {currency_code}: {e}")
        return None

def load_gold_json():
    """Load historical gold price data from JSON file
    
    Returns:
        DataFrame with columns [date, price] or None if file not found
    """
    try:
        json_path = os.path.join('data', 'economics', 'gold.json')
        
        if not os.path.exists(json_path):
            return None
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse JSON into DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['price'] = df['price'].astype(float)
        
        # Sort by date
        df = df.sort_values('date')
        
        return df
        
    except Exception as e:
        print(f"Error loading gold JSON: {e}")
        return None

def generate_currency_plot(currency_code, color='#6c7c40'):
    """Generate currency chart from JSON data
    
    Args:
        currency_code: Currency code (e.g., 'EUR', 'USD')
        color: Line color for the plot
        
    Returns:
        Base64 encoded PNG image
    """
    df = load_currency_json(currency_code)
    
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#c2c9b6')
    ax.set_facecolor('#c2c9b6')
    
    if df is not None and not df.empty:
        ax.plot(df['date'], df['rate'], color=color, linewidth=2)
        ax.set_title(f'{currency_code.upper()} - Widok w skali roku', color='#2B370A')
        ax.set_ylabel('Kurs (PLN)', color='#2B370A')
    else:
        ax.text(0.5, 0.5, 'Brak danych', ha='center', va='center', 
                fontsize=20, color='#2B370A', transform=ax.transAxes)
        ax.set_title(f'{currency_code.upper()} - Brak danych', color='#2B370A')
    
    ax.set_xlabel('Data', color='#2B370A')
    ax.tick_params(colors='#2B370A')
    
    # Make axis labels white for visibility
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color('white')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def ekonomia():
    """Main economy module handler"""
    
    # aktualizacja JSON-ów przy starcie
    fetch_nbp.run_update()
    
    # Static exchange rates for main currencies
    kurs_walut = {
        'EUR': 4.24,
        'CHF': 4.57,
        'USD': 3.64
    }
    
    # Generate default currency chart (EUR)
    wykres_waluty = generate_currency_plot('EUR', '#6c7c40')

    # Load gold prices from JSON and generate chart
    gold_df = load_gold_json()
    mgr = Manager()
    wykres_zlota = mgr.create_plot_image(gold_df, x_col='date', y_col='price', color='#6c7c40', y_label='Cena (PLN)', x_label='Data')

    # Get gold price and convert from PLN per gram to PLN per troy ounce
    # 1 troy ounce = 31.1034768 grams
    cena_zlota_za_gram = api_testy.get_gold_price()[0]['cena']
    cena_zlota = round(cena_zlota_za_gram * 31.1034768, 2)

    # Get currency list and rates for calculator
    mgr = Manager()
    currency_codes = mgr.list_currencies()
    raw_rates = mgr.currencies.get_current_rates()
    # Normalize to uppercase and add PLN=1
    currency_rates = {k.upper(): v for k, v in raw_rates.items()}
    currency_rates['PLN'] = 1.0

    # Prepare currencies for table (exclude main ones)
    excluded_currencies = {'EUR', 'CHF', 'USD'}
    all_currencies_for_tiles = {}
    for code in currency_codes:
        if code.upper() not in excluded_currencies:
            rate = currency_rates.get(code.upper())
            if rate:
                all_currencies_for_tiles[code.upper()] = rate

    return render_template('ekonomia/exchange.html',
                           kurs_walut=kurs_walut,
                           wykres_waluty=wykres_waluty,
                           wykres_zlota=wykres_zlota,
                           cena_zlota=cena_zlota,
                           currency_codes=currency_codes,
                           currency_rates=currency_rates,
                           all_currencies_for_tiles=all_currencies_for_tiles)

def get_currency_chart(currency_code):
    """AJAX endpoint for dynamic currency chart generation
    
    Args:
        currency_code: Currency code (e.g., 'EUR', 'USD')
        
    Returns:
        JSON response with success status, chart data, and message
    """
    try:
        # Check if JSON file exists
        json_path = os.path.join('data', 'economics', f'{currency_code.upper()}.json')
        
        if not os.path.exists(json_path):
            return jsonify({
                'success': False,
                'message': f'Brak danych dla waluty {currency_code.upper()}',
                'chart': None
            })
        
        # Generate chart
        chart_data = generate_currency_plot(currency_code, '#6c7c40')
        
        return jsonify({
            'success': True,
            'message': f'Wykres dla {currency_code.upper()} wygenerowany',
            'chart': chart_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd podczas generowania wykresu: {str(e)}',
            'chart': None
        })
