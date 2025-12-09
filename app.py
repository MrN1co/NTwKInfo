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
from modules.scheduler import init_scheduler
import tests

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
    
    # Initialize database (creates tables and default users if needed)
    init_db(app)
    
    # Context processor to make current user available to all templates
    @app.context_processor
    def inject_user():
        from flask import session
        from modules.database import User
        current_user = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
        return dict(current_user=current_user)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tables_bp, url_prefix='/news')
    app.register_blueprint(weather_bp, url_prefix='/weather')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Initialize background scheduler for daily alerts
    init_scheduler(app)
    
    return app

if __name__ == '__main__':
    print("\n=== Uruchamianie testów ===\n")
    tests.run_tests()
    print("\n=== Testy zakończone ===\n")
    
    app = create_app()
    
    # Flask gdy debug= True uruchamia proces podwójnie (proces główny + monitorujący zmiany)
    # Aby nie wyczerpać szybko limitów API należy uruchomić kolektory tylko w procesie głównym
    # Do usunięcia w produkcji
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("\n=== Uruchamianie testów ===\n")
        tests.run_tests()
        print("\n=== Testy zakończone ===\n")
        init_news_module()
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    app.run(debug=True, host=host, port=port)