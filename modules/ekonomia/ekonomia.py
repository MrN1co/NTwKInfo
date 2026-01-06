from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, session
from modules.ekonomia.klasy_api_obsluga.Manager import Manager
from modules.auth import api_login_required
from modules.database import FavoriteCurrency
from modules.ekonomia import fetch_nbp
import io
import base64
import matplotlib
import os
import json
import pandas as pd

# Use non-interactive Agg backend for server-side image generation
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Create blueprint for economics module 
ekonomia_bp = Blueprint('ekonomia', __name__)

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


def format_pl_number(value):
    """Format number with Polish separators (space thousands, comma decimals)."""
    try:
        formatted = f"{float(value):,.2f}"
        # 1,234.56 -> 1 234,56
        return formatted.replace(',', ' ').replace('.', ',')
    except Exception:
        return "–"


def get_homepage_rates(preferred_codes=None):
    """Return list of currency rates for homepage.

    Tries local JSON snapshots first; if missing, falls back to live NBP API.
    """
    preferred_codes = preferred_codes or ["USD", "EUR", "GBP", "CHF"]

    # JSON first
    json_rates = {}
    for code in preferred_codes:
        df = load_currency_json(code)
        if df is not None and not df.empty:
            json_rates[code] = float(df["rate"].iloc[-1])

    # API fallback only if needed
    api_rates = None
    if len(json_rates) < len(preferred_codes):
        api_rates = Manager().currencies.get_current_rates()

    rates = []
    for code in preferred_codes:
        rate = json_rates.get(code)
        if rate is None and api_rates:
            rate = api_rates.get(code.lower())
        if rate:
            rates.append({"code": code, "rate": round(rate, 4)})

    return rates

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

@ekonomia_bp.route('/ekonomia')
def ekonomia():
    """Main economy module handler"""
    
    # aktualizacja JSON-ów przy starcie
    # Update JSONs only on first run, then once per 24 hours
    last_update_file = os.path.join('data', 'economics', '.last_update')
    should_update = False
    
    if not os.path.exists(last_update_file):
        should_update = True
    else:
        try:
            with open(last_update_file, 'r') as f:
                last_update = datetime.fromisoformat(f.read().strip())
            if datetime.now() - last_update > timedelta(hours=24):
                should_update = True
        except:
            should_update = True
    
    if should_update:
        fetch_nbp.run_update()
        os.makedirs(os.path.dirname(last_update_file), exist_ok=True)
        with open(last_update_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
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
    current_gold = mgr.gold.get_current_price()
    cena_zlota = round(current_gold * 31.1034768, 2) if current_gold else 0
    cena_zlota_formatted = format_pl_number(cena_zlota)

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
                           cena_zlota_formatted=cena_zlota_formatted,
                           currency_codes=currency_codes,
                           currency_rates=currency_rates,
                           all_currencies_for_tiles=all_currencies_for_tiles)

@ekonomia_bp.route('/ekonomia/chart/<currency_code>')
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

# ======================= API: EXCHANGE RATES =======================

@ekonomia_bp.route('/ekonomia/api/exchange-rates')
def api_get_exchange_rates():
    """Zwraca listę dostępnych walut z kursami z NBP API"""
    try:
        mgr = Manager()
        raw_rates = mgr.currencies.get_current_rates()
        
        # Normalize to uppercase and add PLN=1
        currency_rates = {k.upper(): v for k, v in raw_rates.items()}
        currency_rates['PLN'] = 1.0
        
        # Prepare currencies for table (include main ones with rate 0)
        all_currencies_for_tiles = []
        main_currencies = ['EUR', 'USD', 'CHF', 'GBP', 'JPY', 'AUD', 'CAD', 'NOK', 'SEK', 'DKK']
        
        for code in main_currencies:
            all_currencies_for_tiles.append({'code': code, 'rate': currency_rates.get(code, 0)})
        
        return jsonify(all_currencies_for_tiles), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ======================= API: FAVORITE CURRENCIES =======================

@ekonomia_bp.route('/ekonomia/api/favorite-currencies', methods=['GET'])
@api_login_required
def api_get_favorite_currencies():
    """Zwraca listę ulubionych walut zalogowanego użytkownika (max 3)"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'not_authenticated'}), 401
        
        favs = FavoriteCurrency.get_for_user(user_id)
        currencies = [{'currency_code': f.currency_code, 'order': f.order} for f in favs]
        
        return jsonify({'favorite_currencies': currencies}), 200
    except Exception as e:
        print(f"Error getting favorites: {e}")
        return jsonify({'error': str(e)}), 500


@ekonomia_bp.route('/ekonomia/api/favorite-currencies', methods=['POST'])
@api_login_required
def api_add_favorite_currency():
    """Dodaj ulubioną walutę (max 3 na użytkownika)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    
    body = request.get_json() or {}
    currency_code = body.get('currency_code', '').upper()
    
    if not currency_code:
        return jsonify({'error': 'currency_code required'}), 400
    
    # Validate currency code format
    if len(currency_code) < 2 or len(currency_code) > 10:
        return jsonify({'error': 'invalid currency_code'}), 400
    
    try:
        fav = FavoriteCurrency.create(user_id, currency_code)
        if fav is None:
            return jsonify({'error': 'max_favorites_reached', 'message': 'Możesz mieć maksymalnie 3 ulubione waluty'}), 409
        
        favs = FavoriteCurrency.get_for_user(user_id)
        currencies = [{'currency_code': f.currency_code, 'order': f.order} for f in favs]
        return jsonify({'favorite_currencies': currencies}), 201
    except Exception as e:
        print(f"Error adding favorite: {e}")
        return jsonify({'error': str(e)}), 500


@ekonomia_bp.route('/ekonomia/api/favorite-currencies/<currency_code>', methods=['DELETE'])
@api_login_required
def api_delete_favorite_currency(currency_code):
    """Usuń ulubioną walutę"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_authenticated'}), 401
    
    currency_code = currency_code.upper()
    
    try:
        FavoriteCurrency.delete_by_code(user_id, currency_code)
        favs = FavoriteCurrency.get_for_user(user_id)
        currencies = [{'currency_code': f.currency_code, 'order': f.order} for f in favs]
        return jsonify({'favorite_currencies': currencies}), 200
    except Exception as e:
        print(f"Error deleting favorite: {e}")
        return jsonify({'error': str(e)}), 500
