# NTwKInfo - Flask Web Application

A modern, modular Flask web application with HTML/CSS frontend, featuring user authentication, RESTful API, and responsive design.

## Features

- 🔐 **User Authentication** - Secure login/registration system
- 🎨 **Modern UI** - Bootstrap 5 with custom styling
- 📱 **Responsive Design** - Mobile-first approach
- 🔗 **RESTful API** - JSON API endpoints for data access
- 🏗️ **Modular Architecture** - Clean separation of concerns
- 📊 **Dashboard** - User dashboard with statistics
- 📝 **Contact Form** - Contact page with form handling
- 🚀 **Production Ready** - Configured for easy deployment

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd NTwKInfo
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - Open your browser to `http://localhost:5000`
   - Use demo accounts: `admin/password123` or `user/user123`

## Project Structure

```
NTwKInfo/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── modules/              # Application modules
│   ├── auth.py          # Authentication & user management
│   ├── main.py          # Main application routes
│   ├── api.py           # RESTful API endpoints
│   ├── database.py      # Database models & utilities
│   └── utils.py         # Helper functions
├── templates/           # Jinja2 HTML templates
│   ├── base.html        # Base template with navigation
│   ├── auth/           # Authentication pages
│   └── main/           # Main application pages
├── static/             # Static assets
│   ├── css/style.css   # Custom styles
│   ├── js/main.js      # JavaScript functionality
│   └── images/         # Image assets
└── docs/              # Documentation
    ├── API.md         # API documentation
    └── DEVELOPMENT.md # Development guide
```

## Technology Stack

### Backend
- **Flask** - Python web framework
- **Werkzeug** - WSGI utilities and security
- **Jinja2** - Template engine
- **SQLite** - Database (easily replaceable)

### Frontend
- **Bootstrap 5** - CSS framework
- **Font Awesome** - Icon library
- **Custom CSS** - Enhanced styling with CSS variables
- **Vanilla JavaScript** - Client-side functionality

## API Endpoints

### Authentication Required
- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create new post

### Public Endpoints
- `GET /api/status` - API health check
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get specific user

See [API Documentation](docs/API.md) for detailed information.

## Development

### Adding New Features

1. **Backend Routes**: Add to appropriate module in `modules/`
2. **Frontend Pages**: Create templates in `templates/`
3. **Styling**: Add CSS to `static/css/style.css`
4. **JavaScript**: Add functionality to `static/js/main.js`

### Database Models

The application includes ready-to-use models for:
- **Users** - User accounts and authentication
- **Posts** - Blog posts or content
- **API Logs** - Request logging and analytics

### Testing

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

## Deployment

### Development Server
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Docker
```bash
docker build -t flask-app .
docker run -p 5000:5000 flask-app
```

## Screenshots

### Home Page
Modern landing page with feature highlights and statistics.

### Dashboard
User dashboard with activity monitoring and quick actions.

### Authentication
Clean login/registration forms with validation.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- 📧 Email: contact@example.com
- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: Create an issue on GitHub

## Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the UI components
- Contributors and testers