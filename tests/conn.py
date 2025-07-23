import os
from sqlalchemy import create_engine

db_url = "postgresql://postgres:secret@localhost:5432/ktb-in-scrape"
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("Database connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")