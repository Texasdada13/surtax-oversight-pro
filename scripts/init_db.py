#!/usr/bin/env python
"""Initialize the database with the unified schema."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
