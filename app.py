from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret123"
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_db():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn

# Student page
@app.route("/")
def index():
    return render_template("index.html")  # tera purana HTML

# Verify location (generic, PPI check ignored)
@app.route("/verify_location", methods=["POST"])
def verify_location():
    data = request.get_json()
    # location optional, always success
    return jsonify({"status":"success", "message":"Location verified"})

# Mark attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()

        enrollment = data['enrollment']
        name = data['name']
        class_name = data['class_name']

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
        print("ERROR:", e)
        return jsonify({"message": "Error marking attendance"}), 500


# Teacher login
@app.route("/teacher_login", methods=["GET","POST"])
def teacher_login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM teacher WHERE email=? AND password=?", (email,password))
        teacher = cur.fetchone()
        conn.close()
        if teacher:
            session["teacher"] = email
            return redirect("/teacher_dashboard")
        else:
            return render_template("teacher.html", error="Invalid login")
    return render_template("teacher.html")

# Teacher dashboard
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

# Override
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

if __name__ == "__main__":
    app.run(debug=True)
