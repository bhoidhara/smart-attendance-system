from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3, math
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"
DB = "attendance.db"

# Parul PPI location
PPI_LAT = 22.2885
PPI_LON = 73.3620
RADIUS = 150

def distance(lat1, lon1, lat2, lon2):
    R = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    d = request.json
    if distance(d["lat"], d["lon"], PPI_LAT, PPI_LON) <= RADIUS:
        return jsonify({"status":"inside"})
    return jsonify({"status":"outside"})

@app.route("/mark", methods=["POST"])
def mark():
    d = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO attendance VALUES(NULL,?,?,?,?,?)",
              (d["enroll"], d["name"], d["class"], datetime.now(), "Present"))
    conn.commit()
    conn.close()
    return jsonify({"status":"done"})

# Teacher Login
@app.route("/teacher", methods=["GET","POST"])
def teacher():
    if request.method=="POST":
        e = request.form["email"]
        p = request.form["password"]
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        r = c.execute("SELECT * FROM teacher WHERE email=? AND password=?", (e,p)).fetchone()
        conn.close()
        if r:
            session["teacher"] = True
            return redirect("/dashboard")
    return render_template("teacher.html")

@app.route("/dashboard")
def dashboard():
    if "teacher" not in session:
        return redirect("/teacher")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute("SELECT * FROM attendance ORDER BY time DESC").fetchall()
    conn.close()
    return render_template("dashboard.html", rows=rows)

# Override
@app.route("/override", methods=["POST"])
def override():
    if "teacher" not in session:
        return redirect("/teacher")
    e = request.form["enroll"]
    n = request.form["name"]
    cl = request.form["class"]

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO attendance VALUES(NULL,?,?,?,?,?)",
              (e,n,cl,datetime.now(),"Manual"))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run()


