from flask import Flask,render_template,request
import sqlite3,datetime,math

app = Flask(__name__)

db = sqlite3.connect("attendance.db", check_same_thread=False)
c = db.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
 phone TEXT,
 sid TEXT,
 date TEXT,
 lat REAL,
 lon REAL
)
""")
db.commit()

# CLASS LOCATION (change to your classroom)
CLASS_LAT = 23.0225
CLASS_LON = 72.5714
RADIUS = 200  # meters

def distance(lat1, lon1, lat2, lon2):
 R = 6371000
 phi1,phi2 = math.radians(lat1),math.radians(lat2)
 dphi = math.radians(lat2-lat1)
 dl = math.radians(lon2-lon1)
 a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
 return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))

@app.route("/")
def index(): return render_template("index.html")

@app.route("/student")
def student(): return render_template("student.html")

@app.route("/mark", methods=["POST"])
def mark():
 d = request.json
 dist = distance(CLASS_LAT,CLASS_LON,d["lat"],d["lon"])
 if dist > RADIUS:
  return "❌ Outside classroom"
 c.execute(
 "INSERT INTO attendance VALUES (?,?,?,?,?)",
 (d["phone"],d["sid"],str(datetime.date.today()),d["lat"],d["lon"])
 )
 db.commit()
 return "✅ Attendance Marked"

app.run(debug=True)

