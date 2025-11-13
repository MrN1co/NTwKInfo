from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user from database using SQLAlchemy (prevents SQL injection)
        user = User.get_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email', f'{username}@example.com')
        password = request.form['password']
        
        # Query existing user using SQLAlchemy (parameterized query)
        existing_user = User.get_by_username(username)
        
        if existing_user:
            flash('Username already exists', 'error')
        else:
            try:
                # Create new user using SQLAlchemy ORM
                User.create(username, email, password)
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
