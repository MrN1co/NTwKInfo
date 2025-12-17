"""Fix favorite_currencies table - drop and recreate with order column"""
from flask import Flask
from modules.database import db, FavoriteCurrency
import os

app = Flask(__name__)
# Use the same database path as main app.py
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Drop the old table
    print("Dropping old favorite_currencies table...")
    db.session.execute(db.text("DROP TABLE IF EXISTS favorite_currencies"))
    db.session.commit()
    
    # Create new table with order column
    print("Creating new favorite_currencies table with order column...")
    db.create_all()
    
    print("✓ Table recreated successfully!")
    print("✓ favorite_currencies now has: id, user_id, currency_code, order, created_at")
