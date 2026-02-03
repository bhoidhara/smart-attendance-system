from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# DATABASE CONFIG (FIXED)
# =========================

DB_PATH = "/tmp/attendance.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



# 🔥 TABLE AUTO CREATE (MOST IMPORTANT)
def init_db():
    conn = get_db()
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

# app start hote hi table ban jaayegi
init_db()

# =========================
# STUDENT PAGE
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# VERIFY LOCATION
# =========================
@app.route("/verify_location", methods=["POST"])
def verify_location():
    return jsonify({
        "status": "success",
        "message": "Location verified"
    })

# =========================
# MARK ATTENDANCE (FIXED)
# =========================
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    enrollment = data.get('enrollment')
    name = data.get('name')
    class_name = data.get('class_name')

    if not enrollment or not name or not class_name:
        return jsonify({"message": "Missing student data"}), 400

    try:
        now = datetime.now()
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO attendance
            (enrollment, name, class_name, date, time, last_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            enrollment,
            name,
            class_name,
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            'Student'
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Attendance marked successfully"})

    except Exception as e:
        print("DB ERROR:", e)
        return jsonify({"message": "Database error"}), 500


# =========================
# TEACHER LOGIN
# =========================
@app.route("/teacher_login", methods=["GET","POST"])
def teacher_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM teacher WHERE email=? AND password=?",
            (email, password)
        )
        teacher = cur.fetchone()
        conn.close()

        if teacher:
            session["teacher"] = email
            return redirect("/teacher_dashboard")
        else:
            return render_template("teacher.html", error="Invalid login")

    return render_template("teacher.html")

# =========================
# TEACHER DASHBOARD
# =========================
@app.route("/teacher_dashboard")
def teacher_dashboard():
    if "teacher" not in session:
        return redirect("/teacher_login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance ORDER BY date DESC, time DESC")
    rows = cur.fetchall()
    conn.close()

    return render_template("teacher.html", attendance=rows)

# =========================
# OVERRIDE
# =========================
@app.route("/override", methods=["POST"])
def override():
    if "teacher" not in session:
        return redirect("/teacher_login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE attendance SET last_status='Override'")
    conn.commit()
    conn.close()

    return redirect("/teacher_dashboard")

# =========================
if __name__ == "__main__":
    app.run(debug=True)
