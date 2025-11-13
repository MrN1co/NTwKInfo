"""
Database utilities and models for the Flask application.
This module provides SQLAlchemy ORM models with SQLite backend for safe database operations.
SQLAlchemy automatically prevents SQL injection attacks through parameterized queries.
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime
from sqlalchemy import func

# Initialize SQLAlchemy
db = SQLAlchemy()


# Database Models

class User(db.Model):
    """User model - stores user account information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    sessions = db.relationship('Session', back_populates='user', cascade='all, delete-orphan')
    api_logs = db.relationship('APILog', back_populates='user', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='author', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def create(username, email, password):
        """Create a new user - uses parameterized queries for safety"""
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_by_username(username):
        """Get user by username - parameterized for SQL injection prevention"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_all():
        """Get all users"""
        return User.query.order_by(User.created_at.desc()).all()
    
    def update(self, **kwargs):
        """Update user information using ORM"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete user"""
        db.session.delete(self)
        db.session.commit()


class Session(db.Model):
    """Session model - stores user sessions"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='sessions')
    
    def __repr__(self):
        return f'<Session {self.session_token}>'


class Post(db.Model):
    """Post model - stores blog posts or articles"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = db.relationship('User', back_populates='posts')
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    @staticmethod
    def create(title, content, author_id):
        """Create a new post"""
        post = Post(title=title, content=content, author_id=author_id)
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID"""
        return Post.query.get(post_id)
    
    @staticmethod
    def get_all(limit=None):
        """Get all posts"""
        query = Post.query.order_by(Post.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_by_author(author_id):
        """Get posts by author"""
        return Post.query.filter_by(author_id=author_id).order_by(Post.created_at.desc()).all()
    
    def update(self, **kwargs):
        """Update post"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """Delete post"""
        db.session.delete(self)
        db.session.commit()


class APILog(db.Model):
    """API logging model - tracks API requests for monitoring"""
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(255), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = db.relationship('User', back_populates='api_logs')
    
    def __repr__(self):
        return f'<APILog {self.endpoint} {self.status_code}>'
    
    @staticmethod
    def log_request(endpoint, method, user_id=None, status_code=200, response_time=0):
        """Log an API request - uses ORM for safety"""
        log = APILog(
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            status_code=status_code,
            response_time=response_time
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def get_recent_logs(limit=100):
        """Get recent API logs"""
        return APILog.query.order_by(APILog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_stats():
        """Get API usage statistics using aggregation functions"""
        # Total requests
        total_requests = db.session.query(func.count(APILog.id)).scalar()
        
        # Requests by status code
        status_stats = db.session.query(
            APILog.status_code,
            func.count(APILog.id).label('count')
        ).group_by(APILog.status_code).order_by(func.count(APILog.id).desc()).all()
        
        # Average response time
        avg_response_time = db.session.query(func.avg(APILog.response_time)).scalar() or 0
        
        return {
            'total_requests': total_requests,
            'status_stats': [{'status_code': row[0], 'count': row[1]} for row in status_stats],
            'avg_response_time': avg_response_time
        }


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        create_default_users()


def create_default_users():
    """Create default users for testing"""
    # Check if admin user exists
    admin_exists = User.query.filter_by(username='admin').first()
    
    if not admin_exists:
        # Create admin user
        User.create('admin', 'admin@example.com', 'password123')
        # Create regular user
        User.create('user', 'user@example.com', 'user123')
