import sys
import os

# Add parent directory to sys.path so app and database can be imported
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app

# Vercel looks for the WSGI application callable `app`
if __name__ == "__main__":
    app.run()
