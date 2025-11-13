from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from modules.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    username = session.get('user_id', 'Guest')
    return render_template('main/dashboard.html', username=username)

