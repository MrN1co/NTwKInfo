# Setup Guide

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the Flask development server:

```bash
/Users/mrnico/Documents/NTwKInfo/.venv/bin/python app.py
```

The app will be available at `http://127.0.0.1:5001`

## Project Structure

- `app.py` - Main application entry point
- `modules/` - Core application modules (auth, database, main)
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JS, images)
- `tests/` - Unit tests
