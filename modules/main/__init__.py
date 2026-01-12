from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from modules.auth import login_required
from modules.news.collectors import get_kryminalki_news
from modules.ekonomia.ekonomia import ekonomia, get_currency_chart, get_homepage_rates

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    news_list = get_kryminalki_news(limit=3)
    homepage_rates = get_homepage_rates()
    return render_template('main/index.html', news_list=news_list, homepage_rates=homepage_rates)


@main_bp.route('/news')
def news():
    return redirect(url_for('tables.news'))


@main_bp.route('/ekonomia')
def economy():
    return ekonomia()


@main_bp.route('/ekonomia/chart/<currency_code>')
def economy_chart(currency_code):
    return get_currency_chart(currency_code)


@main_bp.route('/pogoda')
def weather():
    return redirect(url_for('weather.weather_index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    from modules.database import User
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if not user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('auth/dashboard.html', user=user)
