import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment TEXT,
    name TEXT,
    class TEXT,
    time TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("✅ attendance.db created with table")

