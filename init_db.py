import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment TEXT,
    name TEXT,
    class_name TEXT,
    date TEXT,
    time TEXT,
    last_status TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized successfully")

