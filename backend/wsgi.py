"""
WSGI entry point for Gunicorn
"""
from main import app

if __name__ == "__main__":
    app.run()

