from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3, math
from datetime import datetime

app = Flask(__name__)
app.secret_key="secret"
DB="attendance.db"

PPI_LAT=22.2885
PPI_LON=73.3620
RADIUS=150

def dist(a,b,c,d):
    R=6371000
    import math
    d1=math.radians(c-a)
    d2=math.radians(d-b)
    x=math.sin(d1/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(d2/2)**2
    return 2*R*math.atan2(math.sqrt(x),math.sqrt(1-x))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    d=request.json
    if dist(d["lat"],d["lon"],PPI_LAT,PPI_LON)<=RADIUS:
        return jsonify({"status":"inside"})
    return jsonify({"status":"outside"})

@app.route("/mark", methods=["POST"])
def mark():
    d=request.json
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("INSERT INTO attendance VALUES (NULL,?,?,?,?,?)",
              (d["enroll"],d["name"],d["class"],datetime.now(),"Present"))
    conn.commit(); conn.close()
    return jsonify({"status":"done"})

@app.route("/teacher",methods=["GET","POST"])
def teacher():
    if request.method=="POST":
        e=request.form["email"]
        p=request.form["password"]
        conn=sqlite3.connect(DB)
        c=conn.cursor()
        r=c.execute("SELECT * FROM teacher WHERE email=? AND password=?",(e,p)).fetchone()
        conn.close()
        if r:
            session["t"]=True
            return redirect("/dashboard")
    return render_template("teacher.html")

@app.route("/dashboard")
def dash():
    if "t" not in session:
        return redirect("/teacher")
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    rows=c.execute("SELECT * FROM attendance").fetchall()
    conn.close()
    return render_template("dashboard.html",rows=rows)

if __name__=="__main__":
    app.run()

