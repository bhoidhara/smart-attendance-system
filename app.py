from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
from datetime import datetime
import math

app = Flask(__name__)
DB = "attendance.db"

CLASS_LAT = 19.0760      # 🔴 change to your classroom GPS
CLASS_LON = 72.8777     # 🔴 change to your classroom GPS
RADIUS_METERS = 100     # 100 meters allowed

def distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_db():
    return sqlite3.connect(DB)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mark", methods=["POST"])
def mark():
    data = request.json
    phone = data["phone"]
    lat = float(data["lat"])
    lon = float(data["lon"])

    d = distance(CLASS_LAT, CLASS_LON, lat, lon)

    if d > RADIUS_METERS:
        return jsonify({"status":"fail","msg":"Outside class range"})

    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO attendance(phone,time,lat,lon,mode) VALUES(?,?,?,?,?)",
              (phone, datetime.now(), lat, lon, "SYSTEM"))
    db.commit()
    return jsonify({"status":"ok"})

@app.route("/teacher")
def teacher():
    db = get_db()
    data = db.execute("SELECT * FROM attendance ORDER BY time DESC").fetchall()
    return render_template("teacher.html", data=data)

@app.route("/override", methods=["POST"])
def override():
    phone = request.form["phone"]
    db = get_db()
    db.execute("INSERT INTO attendance(phone,time,lat,lon,mode) VALUES(?,?,?,?,?)",
               (phone, datetime.now(), 0, 0, "FACULTY"))
    db.commit()
    return redirect("/teacher")

if __name__ == "__main__":
    app.run()


