import os
import time
import tempfile
import threading
from multiprocessing import Process
from flask import Flask, jsonify, request
import pytest

# Create a simple e2e_server fixture that runs the app on a test port.
# It registers a small test-only blueprint to check user existence and delete user.

from modules.database import db, User, init_db
from modules.auth import auth_bp
from modules.main import main_bp

TEST_PORT = 5001

def run_app(app):
    app.run(port=TEST_PORT, use_reloader=False)


@pytest.fixture(scope='session')
def e2e_server():
    # Ensure templates and static are found when server runs in a different working dir
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static'))

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config['TESTING'] = True
    # Use a temporary file DB so background server and test process share state
    tmpfile = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    sqlite_uri = f"sqlite:///{tmpfile.name}"
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'e2e-secret'

    # Init DB and blueprints
    db.init_app(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Testing-only admin blueprint
    from flask import Blueprint
    test_bp = Blueprint('test', __name__)

    @test_bp.route('/test/api/users/<username>/exists')
    def user_exists(username):
        u = User.get_by_username(username)
        return jsonify({'exists': bool(u)})

    @test_bp.route('/test/api/users/<username>/delete', methods=['POST'])
    def delete_user(username):
        u = User.get_by_username(username)
        if not u:
            return jsonify({'deleted': False}), 404
        u.delete()
        return jsonify({'deleted': True})

    app.register_blueprint(test_bp)

    # Start server in background thread
    with app.app_context():
        init_db(app)

        # Provide `current_user` to templates to mimic real app context processors
        @app.context_processor
        def inject_current_user():
            from flask import session
            user_id = session.get('user_id')
            user = User.get_by_id(user_id) if user_id else None
            return {'current_user': user}

    thread = threading.Thread(target=run_app, args=(app,), daemon=True)
    thread.start()

    # Give server time to start
    time.sleep(1.0)

    yield f'http://127.0.0.1:{TEST_PORT}'

    # Teardown
    try:
        tmpfile.close()
        os.unlink(tmpfile.name)
    except Exception:
        pass
