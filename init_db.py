import sqlite3

conn = sqlite3.connect("attendance.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
enroll TEXT,
name TEXT,
class TEXT,
time TEXT,
status TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS teacher(
email TEXT,
password TEXT
)
""")

c.execute("DELETE FROM teacher")
c.execute("INSERT INTO teacher VALUES('teacher@parul.com','1234')")

conn.commit()
conn.close()
print("Database ready")

