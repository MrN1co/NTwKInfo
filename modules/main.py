from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from modules.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    username = session.get('user_id', 'Guest')
    return render_template('main/dashboard.html', username=username)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # In a real app, you'd save this to a database or send an email
        flash(f'Thank you {name}! Your message has been received.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('main/contact.html')
