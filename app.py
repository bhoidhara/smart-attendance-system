import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key'

TEACHER_EMAIL = 'teacher@parul.edu'
TEACHER_PASSWORD = 'password123'

def get_db():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))