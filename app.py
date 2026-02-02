from flask import Flask, render_template, request, jsonify
import sqlite3
import math

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

DB = 'attendance.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Haversine formula to check if student is near Parul University
def is_nearby(lat1, lon1, lat2=22.3072, lon2=73.1812, radius_km=0.5):
    import math
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2*math.asin(math.sqrt(a))
    km = 6371*c
    return km <= radius_km

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student')
def student():
    # Student page opens from QR, data comes from URL parameters
    return render_template('student.html')

@app.route('/verify_location', methods=['POST'])
def verify_location():
    data = request.get_json()
    enrollment = data.get('enrollment')
    name = data.get('name')
    class_name = data.get('class_name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not all([enrollment, name, class_name, latitude, longitude]):
        return jsonify({'status':'fail','message':'Missing data'}),400

    if not is_nearby(float(latitude), float(longitude)):
        return jsonify({'status':'fail','message':'You are not near Parul University'})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment TEXT UNIQUE,
            name TEXT,
            class TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO students(enrollment,name,class) VALUES (?,?,?)",
                   (enrollment,name,class_name))
    conn.commit()
    conn.close()

    return jsonify({'status':'success','message':'Location verified! You can now mark attendance'})

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    enrollment = data.get('enrollment')
    if not enrollment:
        return jsonify({'status':'fail','message':'Missing enrollment'}),400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    cursor.execute("SELECT id FROM students WHERE enrollment=?",(enrollment,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({'status':'fail','message':'Student not found'}),400

    cursor.execute("INSERT INTO attendance(student_id) VALUES (?)",(student['id'],))
    conn.commit()
    conn.close()

    return jsonify({'status':'success','message':'Attendance marked successfully!'})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
