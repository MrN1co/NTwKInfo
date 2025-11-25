from flask import Flask
from modules.auth import auth_bp
from modules.main import main_bp
from modules.database import db, init_db
from modules.news.routes import tables_bp
from modules.news.news import init_news_module
import os
from dotenv import load_dotenv
from modules.weather_app import weather_bp
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()

def create_app():
    
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'True') == 'True'

    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'app.db'))
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tables_bp, url_prefix='/news')
    app.register_blueprint(weather_bp, url_prefix='/weather')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Flask gdy debug= True uruchamia proces podwójnie (proces główny + monitorujący zmiany)
    # Aby nie wyczerpać szybko limitów API należy uruchomić kolektory tylko w procesie głównym
    # Do usunięcia w produkcji
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_news_module()
    
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    app.run(debug=True, host=host, port=port)
