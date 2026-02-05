from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
import sqlite3
from datetime import datetime, timedelta
import os
from functools import wraps
from io import BytesIO
from urllib.parse import urlencode
import math
import qrcode
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["PREFERRED_URL_SCHEME"] = "https"

DB_NAME = os.environ.get("DB_PATH", "attendance.db")

TEACHER_EMAIL = os.environ.get("TEACHER_EMAIL", "").strip()
TEACHER_PASSWORD = os.environ.get("TEACHER_PASSWORD", "")
TEACHER_PASSWORD_HASH = os.environ.get("TEACHER_PASSWORD_HASH", "")

STUDENT_URL = os.environ.get("STUDENT_URL", "").strip()
API_BASE = os.environ.get("API_BASE", "").strip()

CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "").split(",")
    if origin.strip()
]


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


GEOFENCE_LAT = parse_float(os.environ.get("GEOFENCE_LAT"))
GEOFENCE_LON = parse_float(os.environ.get("GEOFENCE_LON"))
GEOFENCE_RADIUS_M = parse_float(os.environ.get("GEOFENCE_RADIUS_M"))
RETENTION_DAYS = parse_int(os.environ.get("RETENTION_DAYS"), 30)
RATE_LIMIT_PER_MINUTE = parse_int(os.environ.get("RATE_LIMIT_PER_MINUTE"), 6)
DEVICE_LIMIT_PER_DAY = parse_int(os.environ.get("DEVICE_LIMIT_PER_DAY"), 1)
DEVICE_COOLDOWN_HOURS = parse_int(os.environ.get("DEVICE_COOLDOWN_HOURS"), 20)

_rate_limit = {}


def geofence_enabled():
    return (
        GEOFENCE_LAT is not None
        and GEOFENCE_LON is not None
        and GEOFENCE_RADIUS_M is not None
    )


def get_client_ip():
    return (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "").strip()
        or request.remote_addr
        or "unknown"
    )


def rate_limit_ok():
    if RATE_LIMIT_PER_MINUTE <= 0:
        return True
    now = time.time()
    cutoff = now - 60
    ip = get_client_ip()
    timestamps = _rate_limit.get(ip, [])
    timestamps = [t for t in timestamps if t > cutoff]
    if len(timestamps) >= RATE_LIMIT_PER_MINUTE:
        _rate_limit[ip] = timestamps
        return False
    timestamps.append(now)
    _rate_limit[ip] = timestamps
    return True


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def cleanup_old_records(conn):
    if RETENTION_DAYS <= 0:
        return 0
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE time < ?", (cutoff_str,))
    return cur.rowcount


def teacher_login_configured():
    return bool(TEACHER_EMAIL and (TEACHER_PASSWORD or TEACHER_PASSWORD_HASH))


def verify_teacher(email, password):
    if not teacher_login_configured():
        return False
    if email.strip().lower() != TEACHER_EMAIL.lower():
        return False
    if TEACHER_PASSWORD_HASH:
        return check_password_hash(TEACHER_PASSWORD_HASH, password)
    return password == TEACHER_PASSWORD


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("teacher"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def build_student_url(class_name=""):
    base = STUDENT_URL or url_for("student", _external=True)
    if class_name:
        separator = "&" if "?" in base else "?"
        return f"{base}{separator}{urlencode({'class': class_name})}"
    return base


def resolve_db_path():
    db_path = DB_NAME or "attendance.db"
    db_dir = os.path.dirname(db_path)
    if db_dir:
        try:
            os.makedirs(db_dir, exist_ok=True)
        except (OSError, PermissionError):
            return "attendance.db"
    return db_path


def get_db():
    db_path = resolve_db_path()
    try:
        conn = sqlite3.connect(db_path)
    except (OSError, PermissionError):
        if db_path != "attendance.db":
            conn = sqlite3.connect("attendance.db")
        else:
            raise
    conn.row_factory = sqlite3.Row
    return conn


def get_columns(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cur.fetchall()}


def ensure_schema(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment TEXT,
            name TEXT,
            class TEXT,
            time TEXT,
            status TEXT
        )
    """
    )

    cols = get_columns(conn, "attendance")

    if "class" not in cols:
        cur.execute("ALTER TABLE attendance ADD COLUMN class TEXT")
        cols.add("class")
        if "class_name" in cols:
            cur.execute("UPDATE attendance SET class = class_name WHERE class IS NULL")

    if "time" not in cols:
        cur.execute("ALTER TABLE attendance ADD COLUMN time TEXT")
        cols.add("time")

    if "status" not in cols:
        cur.execute("ALTER TABLE attendance ADD COLUMN status TEXT")
        cols.add("status")
        if "last_status" in cols:
            cur.execute("UPDATE attendance SET status = last_status WHERE status IS NULL")

    if "ip" not in cols:
        cur.execute("ALTER TABLE attendance ADD COLUMN ip TEXT")
        cols.add("ip")

    conn.commit()


def init_db():
    conn = get_db()
    ensure_schema(conn)
    conn.close()


init_db()


@app.after_request
def add_cors_headers(response):
    if not CORS_ORIGINS:
        return response
    origin = request.headers.get("Origin")
    if origin and origin in CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def index():
    return redirect(url_for("student"))


@app.route("/student")
def student():
    return render_template("student.html", api_base=API_BASE)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if not teacher_login_configured():
        error = "Teacher login is not configured."
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if teacher_login_configured() and verify_teacher(email, password):
            session["teacher"] = email.strip().lower()
            return redirect(url_for("teacher"))
        elif teacher_login_configured():
            error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect(url_for("login"))


@app.route("/mark", methods=["POST", "OPTIONS"])
def mark():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        if not rate_limit_ok():
            return jsonify({"error": "Too many requests. Please wait and try again."}), 429

        data = request.get_json(silent=True)
        if data is None:
            data = request.form.to_dict()
        data = data or {}

        enrollment = str(data.get("enrollment", "")).strip()
        name = str(data.get("name", "")).strip()
        class_name = str(data.get("class", "")).strip()

        missing = []
        if not enrollment:
            missing.append("enrollment")
        if not name:
            missing.append("name")
        if not class_name:
            missing.append("class")

        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        if geofence_enabled():
            lat = parse_float(data.get("lat"))
            lon = parse_float(data.get("lon"))
            if lat is None or lon is None:
                return jsonify({"error": "Location required."}), 400
            distance = haversine_m(lat, lon, GEOFENCE_LAT, GEOFENCE_LON)
            if distance > GEOFENCE_RADIUS_M:
                return jsonify({"error": "Outside allowed area."}), 403

        conn = get_db()
        cur = conn.cursor()

        client_ip = get_client_ip()
        if DEVICE_LIMIT_PER_DAY > 0:
            cur.execute(
                "SELECT time FROM attendance WHERE ip = ? ORDER BY time DESC LIMIT 1",
                (client_ip,),
            )
            row = cur.fetchone()
            if row:
                try:
                    last_time = datetime.strptime(row["time"], "%Y-%m-%d %H:%M:%S")
                    hours_since = (datetime.now() - last_time).total_seconds() / 3600.0
                    if hours_since < DEVICE_COOLDOWN_HOURS:
                        wait_hours = max(1, int(DEVICE_COOLDOWN_HOURS - hours_since + 0.999))
                        return jsonify({"error": f"Attendance already marked. Try again after {wait_hours} hour(s)."}), 409
                except Exception:
                    return jsonify({"error": "Attendance already marked recently. Try again later."}), 409

        cur.execute(
            "INSERT INTO attendance (enrollment, name, class, time, status, ip) VALUES (?,?,?,?,?,?)",
            (
                enrollment,
                name,
                class_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Present",
                client_ip,
            ),
        )

        cleanup_old_records(conn)

        conn.commit()
        conn.close()

        return jsonify({"message": "Attendance marked"})
    except Exception as exc:
        app.logger.exception("mark failed: %s", exc)
        return jsonify({"error": "Server error. Please try again."}), 500


@app.route("/teacher")
@login_required
def teacher():
    class_name = request.args.get("class", "").strip()
    filter_class = request.args.get("filter_class", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    student_url = build_student_url(class_name)

    conn = get_db()
    cur = conn.cursor()
    cleanup_old_records(conn)
    query = "SELECT * FROM attendance"
    where = []
    params = []
    if filter_class:
        where.append("class LIKE ?")
        params.append(f"%{filter_class}%")
    if date_from:
        where.append("date(time) >= date(?)")
        params.append(date_from)
    if date_to:
        where.append("date(time) <= date(?)")
        params.append(date_to)
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY time DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return render_template(
        "teacher.html",
        rows=rows,
        class_name=class_name,
        student_url=student_url,
        qr_url=url_for("qr", **{"class": class_name}),
        geofence_enabled=geofence_enabled(),
        geofence_radius_m=GEOFENCE_RADIUS_M,
        retention_days=RETENTION_DAYS,
        filter_class=filter_class,
        date_from=date_from,
        date_to=date_to,
    )


@app.route("/teacher/delete-old", methods=["POST"])
@login_required
def delete_old():
    conn = get_db()
    deleted = cleanup_old_records(conn)
    conn.commit()
    conn.close()
    return redirect(url_for("teacher"))


@app.route("/teacher/delete-all", methods=["POST"])
@login_required
def delete_all():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()
    return redirect(url_for("teacher"))


@app.route("/teacher/delete/<int:row_id>", methods=["POST"])
@login_required
def delete_one(row_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM attendance WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("teacher"))


@app.route("/teacher/edit/<int:row_id>", methods=["GET", "POST"])
@login_required
def edit_record(row_id):
    conn = get_db()
    cur = conn.cursor()
    if request.method == "POST":
        enrollment = request.form.get("enrollment", "").strip()
        name = request.form.get("name", "").strip()
        class_name = request.form.get("class", "").strip()
        status = request.form.get("status", "").strip() or "Present"

        if not enrollment or not name or not class_name:
            conn.close()
            return redirect(url_for("edit_record", row_id=row_id))

        cur.execute(
            "UPDATE attendance SET enrollment = ?, name = ?, class = ?, status = ? WHERE id = ?",
            (enrollment, name, class_name, status, row_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("teacher"))

    cur.execute("SELECT * FROM attendance WHERE id = ?", (row_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return redirect(url_for("teacher"))
    return render_template("edit.html", row=row)


@app.route("/teacher/override", methods=["POST"])
@login_required
def override_attendance():
    enrollment = request.form.get("enrollment", "").strip()
    name = request.form.get("name", "").strip()
    class_name = request.form.get("class", "").strip()

    missing = []
    if not enrollment:
        missing.append("enrollment")
    if not name:
        missing.append("name")
    if not class_name:
        missing.append("class")

    if missing:
        return redirect(url_for("teacher"))

    conn = get_db()
    cur = conn.cursor()
    client_ip = get_client_ip()
    cur.execute(
        "INSERT INTO attendance (enrollment, name, class, time, status, ip) VALUES (?,?,?,?,?,?)",
        (
            enrollment,
            name,
            class_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Present (Override)",
            client_ip,
        ),
    )
    cleanup_old_records(conn)
    conn.commit()
    conn.close()
    return redirect(url_for("teacher"))


@app.route("/qr")
@login_required
def qr():
    class_name = request.args.get("class", "").strip()
    target_url = build_student_url(class_name)

    img = qrcode.make(target_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
