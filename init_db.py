import sqlite3

conn = sqlite3.connect("attendance.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
phone TEXT,
time TEXT,
lat TEXT,
lon TEXT,
mode TEXT
)
""")

conn.commit()
conn.close()

print("Database ready")
