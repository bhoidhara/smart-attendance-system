import sqlite3

conn = sqlite3.connect("attendance.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    enroll TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Clean database ready")
