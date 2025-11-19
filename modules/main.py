from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from modules.auth import login_required
from modules.news.collectors import get_kryminalki_news

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    
    news_list = get_kryminalki_news(limit=3)
    return render_template('homepage.html', news_list=news_list)


@main_bp.route('/news')
def news():
    
    return redirect(url_for('tables.news'))


@main_bp.route('/ekonomia')
def economy():
    return render_template('base.html')


@main_bp.route('/pogoda')
def weather():
    return render_template('base.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    username = session.get('user_id', 'Guest')
    return render_template('main/dashboard.html', username=username)

