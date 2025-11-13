from flask import Flask
from modules.auth import auth_bp
from modules.main import main_bp
import os
from flask_sqlalchemy import SQLAlchemy

def create_app():
    
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['DEBUG'] = True
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///{}'.format(os.path.join(os.path.dirname(__file__), 'app.db'))
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
