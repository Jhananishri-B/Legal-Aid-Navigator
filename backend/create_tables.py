"""
create_tables.py  –  Run this ONCE to create all tables in TiDB/MySQL.

Usage (from the backend folder, with the conda env active):
    python create_tables.py
"""

import sys
from app.database import engine, Base
import app.models  # ensures all models are registered

print("Connecting to database...")
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ All tables created (or already exist).")
except Exception as e:
    print(f"❌ Failed to create tables: {e}")
    sys.exit(1)
