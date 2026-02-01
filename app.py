from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key'  # Change this in production

# Hardcoded teacher credentials (replace with proper auth)
TEACHER_EMAIL = 'teacher@parul.edu'
TEACHER_PASSWORD = 'password123'

def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teacher')
def teacher():
    if 'teacher' not in session:
        return redirect(url_for('login'))
    return render_template('teacher.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == TEACHER_EMAIL and password == TEACHER_PASSWORD:
            session['teacher'] = True
            return redirect(url_for('teacher'))
        return "Invalid credentials", 401
    return render_template('dashboard.html')  # Simple login form

@app.route('/logout')
def logout():
    session.pop('teacher', None)
    return redirect(url_for('index'))

@app.route('/mark', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    name = data.get('name')
    enrollment = data.get('enrollment')
    class_name = data.get('class')
    if not name or not enrollment or not class_name:
        return jsonify({'msg': 'All fields required'}), 400

    conn = get_db()
    conn.execute('INSERT INTO attendance (name, enrollment, class) VALUES (?, ?, ?)',
                 (name, enrollment, class_name))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Attendance marked successfully!'})

@app.route('/override', methods=['POST'])
def override_attendance():
    if 'teacher' not in session:
        return jsonify({'msg': 'Unauthorized'}), 401
    data = request.get_json()
    name = data.get('name')
    enrollment = data.get('enrollment')
    class_name = data.get('class')
    if not name or not enrollment or not class_name:
        return jsonify({'msg': 'All fields required'}), 400

    conn = get_db()
    conn.execute('INSERT INTO attendance (name, enrollment, class) VALUES (?, ?, ?)',
                 (name, enrollment, class_name))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Attendance overridden successfully!'})

@app.route('/get_attendance')
def get_attendance():
    if 'teacher' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    rows = conn.execute('SELECT * FROM attendance ORDER BY timestamp DESC').fetchall()
    conn.close()
    attendance = [dict(row) for row in rows]
    return jsonify(attendance)

@app.route('/delete_old')
def delete_old():
    if 'teacher' not in session:
        return jsonify({'msg': 'Unauthorized'}), 401
    one_day_ago = datetime.now() - timedelta(days=1)
    conn = get_db()
    conn.execute('DELETE FROM attendance WHERE timestamp < ?', (one_day_ago,))
    conn.commit()
    deleted_count = conn.total_changes
    conn.close()
    return jsonify({'msg': f'Deleted {deleted_count} old records'})

if __name__ == '__main__':
    app.run(debug=True)