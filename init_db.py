import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()

# Attendance table
cur.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment TEXT,
    name TEXT,
    class_name TEXT,
    date TEXT,
    time TEXT,
    last_status TEXT
)
''')

# Teacher table
cur.execute('''
CREATE TABLE IF NOT EXISTS teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
''')

# Default teacher (change email/password)
cur.execute('''
INSERT OR IGNORE INTO teacher (email,password) VALUES ('teacher@example.com','1234')
''')

conn.commit()
conn.close()
print("Database Initialized")
