"""Main entrypoint for Kestra CLI."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the app directly from main_cli.py file
from main_cli import app

if __name__ == "__main__":
    app()
