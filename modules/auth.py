from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from modules.database import db, User
import functools

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    """Decorator to require login for views"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def api_login_required(view):
    """Decorator for endpoints used by AJAX/JS: returns 401 JSON when not authenticated,
    otherwise behaves like normal `login_required` (redirect to login for browser requests).
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            # If caller expects JSON (AJAX), return 401 JSON. Otherwise redirect.
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            accepts = request.headers.get('Accept', '')
            if is_ajax or 'application/json' in accepts:
                return jsonify({'error': 'not_authenticated'}), 401
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Query user from database using SQLAlchemy (prevents SQL injection)
        user = User.get_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            # Return JSON for AJAX, or redirect for traditional form submission
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Login successful!', 'redirect': url_for('main.dashboard')})
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Return JSON error for AJAX, or redirect for traditional form submission
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            flash('Invalid username or password', 'error')
            return redirect(url_for('main.index'))
    
    # GET request: redirect to main index
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', f'{username}@example.com')
        password = request.form.get('password', '')
        
        # Query existing user using SQLAlchemy (parameterized query)
        existing_user = User.get_by_username(username)
        
        if existing_user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Username already exists'}), 409
            flash('Username already exists', 'error')
            return redirect(url_for('main.index'))
        else:
            try:
                # Create new user using SQLAlchemy ORM
                User.create(username, email, password)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True, 'message': 'Registration successful! Please log in.', 'redirect': url_for('main.index')})
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 400
                flash(f'Registration failed: {str(e)}', 'error')
                return redirect(url_for('main.index'))
    
    # GET request: redirect to main index
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
