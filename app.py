import csv
import io
import os
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import bootstrap_database, managed_connection

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
VALID_TRANSITIONS = {
    "requested": {"accepted", "canceled"},
    "accepted":  {"completed", "canceled"},
    "completed": set(),
    "canceled":  set(),
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def login_required(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Unauthorized access.")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def notify_user(conn, user_id, message):
    conn.execute(
        "INSERT INTO Notification(message, user_id) VALUES (%s, %s)",
        (message, user_id)
    )


def is_valid_email(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def parse_session_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return None


def is_within_availability(conn, tutor_id, requested_dt):
    slots = conn.execute(
        "SELECT day_of_week, start_time, end_time FROM Availability WHERE tutor_id = %s",
        (tutor_id,),
    ).fetchall()
    if not slots:
        return True
    day_name     = DAY_NAMES[requested_dt.weekday()]
    request_time = requested_dt.strftime("%H:%M:%S")
    for slot in slots:
        # TIME columns come back as timedelta in PyMySQL — convert to HH:MM:SS string
        start = str(slot["start_time"]) if not isinstance(slot["start_time"], str) else slot["start_time"]
        end   = str(slot["end_time"])   if not isinstance(slot["end_time"],   str) else slot["end_time"]
        # timedelta str is like "10:00:00"
        if slot["day_of_week"] == day_name and start <= request_time <= end:
            return True
    return False


def render_stars(rating):
    filled = int(round(float(rating or 0)))
    return "★" * filled + "☆" * (5 - filled)


app.jinja_env.globals["render_stars"] = render_stars


def format_time_value(value):
    if value is None:
        return ""
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        period = "AM" if hours < 12 else "PM"
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minutes:02d} {period}"
    if hasattr(value, "strftime"):
        return value.strftime("%I:%M %p").lstrip("0")
    text = str(value)
    if len(text) >= 8 and ":" in text:
        try:
            parsed = datetime.strptime(text[:8], "%H:%M:%S")
            return parsed.strftime("%I:%M %p").lstrip("0")
        except ValueError:
            pass
    return text


def format_datetime_value(value):
    if value is None:
        return "TBD"
    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
    text = str(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            parsed = datetime.strptime(text[: len(fmt)], fmt)
            return parsed.strftime("%b %d, %Y %I:%M %p").replace(" 0", " ")
        except ValueError:
            continue
    return text


app.jinja_env.globals["fmt_time"] = format_time_value
app.jinja_env.globals["fmt_datetime"] = format_datetime_value


# ── Auth ───────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        if not is_valid_email(form["email"]):
            flash("Please use a valid email address.")
            return render_template("register.html")
        if len(form["password"]) < 8:
            flash("Password must be at least 8 characters.")
            return render_template("register.html")
        password_hash = generate_password_hash(form["password"])
        with managed_connection() as conn:
            try:
                cur = conn.execute(
                    "INSERT INTO Users(first_name,last_name,email,role,password_hash) VALUES (%s,%s,%s,%s,%s)",
                    (form["first_name"], form["last_name"], form["email"],
                     form["role"], password_hash),
                )
                new_user_id = cur.lastrowid
                if form["role"] == "tutor":
                    conn.execute(
                        "INSERT INTO TutorProfile(tutor_id,bio,hourly_rate,profile_picture_url) VALUES (%s,%s,%s,%s)",
                        (new_user_id, "", 25, ""),
                    )
                flash("Registration successful. Please log in.")
                return redirect(url_for("login"))
            except Exception as exc:
                flash(f"Registration failed: {exc}")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]
        with managed_connection() as conn:
            user = conn.execute(
                "SELECT * FROM Users WHERE email = %s", (email,)
            ).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid credentials.")
        else:
            session["user_id"] = user["user_id"]
            session["role"]    = user["role"]
            session["name"]    = f"{user['first_name']} {user['last_name']}"
            return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required()
def dashboard():
    role = session["role"]
    if role == "student": return redirect(url_for("student_dashboard"))
    if role == "tutor":   return redirect(url_for("tutor_dashboard"))
    return redirect(url_for("admin_dashboard"))


# ── Tutor Public Profile ───────────────────────────────────────────────────────

@app.route("/tutor/<int:tutor_id>")
@login_required()
def tutor_public_profile(tutor_id):
    with managed_connection() as conn:
        tutor = conn.execute(
            """
            SELECT u.user_id, u.first_name, u.last_name,
                   tp.bio, tp.hourly_rate, tp.profile_picture_url,
                   COALESCE(ROUND(AVG(r.rating), 2), 0) AS avg_rating,
                   COUNT(DISTINCT r.review_id)           AS review_count,
                   COUNT(DISTINCT ts.session_id)         AS session_count
            FROM TutorProfile tp
            JOIN Users u ON u.user_id = tp.tutor_id
            LEFT JOIN TutoringSession ts ON ts.tutor_id = tp.tutor_id
            LEFT JOIN Review r ON r.session_id = ts.session_id
            WHERE tp.tutor_id = %s
            GROUP BY tp.tutor_id
            """, (tutor_id,),
        ).fetchone()

        if not tutor:
            flash("Tutor not found.")
            return redirect(url_for("search_tutors"))

        subjects = conn.execute(
            """
            SELECT s.subject_name FROM Subject s
            JOIN Teaches t ON t.subject_id = s.subject_id
            WHERE t.tutor_id = %s ORDER BY s.subject_name
            """, (tutor_id,),
        ).fetchall()

        reviews = conn.execute(
            """
            SELECT r.rating, r.comment, ts.session_time,
                   u.first_name AS reviewer_first, u.last_name AS reviewer_last
            FROM Review r
            JOIN TutoringSession ts ON ts.session_id = r.session_id
            JOIN Users u ON u.user_id = r.reviewer_id
            WHERE ts.tutor_id = %s
            ORDER BY ts.session_time DESC
            """, (tutor_id,),
        ).fetchall()

        availability = conn.execute(
            "SELECT day_of_week, start_time, end_time FROM Availability WHERE tutor_id = %s ORDER BY day_of_week, start_time",
            (tutor_id,),
        ).fetchall()

    return render_template("tutor_public_profile.html",
                           tutor=tutor, subjects=subjects,
                           reviews=reviews, availability=availability)


# ── Student ────────────────────────────────────────────────────────────────────

@app.route("/search")
@login_required("student")
def search_tutors():
    subject = request.args.get("subject", "")
    sort    = request.args.get("sort", "rating")
    with managed_connection() as conn:
        tutors = conn.execute(
            """
            SELECT tp.tutor_id, u.first_name, u.last_name, tp.bio,
                   tp.hourly_rate, tp.profile_picture_url,
                   COALESCE(AVG(r.rating), 0) AS avg_rating,
                   GROUP_CONCAT(DISTINCT s.subject_name) AS subjects
            FROM TutorProfile tp
            JOIN Users u ON u.user_id = tp.tutor_id
            LEFT JOIN Teaches t ON t.tutor_id = tp.tutor_id
            LEFT JOIN Subject s ON s.subject_id = t.subject_id
            LEFT JOIN TutoringSession ts ON ts.tutor_id = tp.tutor_id
            LEFT JOIN Review r ON r.session_id = ts.session_id
            GROUP BY tp.tutor_id, u.first_name, u.last_name,
                     tp.bio, tp.hourly_rate, tp.profile_picture_url
            """
        ).fetchall()
        subjects = conn.execute(
            "SELECT * FROM Subject ORDER BY subject_name"
        ).fetchall()

    filtered = [
        t for t in tutors
        if not subject or (t["subjects"] and subject in t["subjects"].split(","))
    ]
    filtered.sort(
        key=lambda row: row["avg_rating"] if sort == "rating" else row["hourly_rate"],
        reverse=(sort == "rating"),
    )
    return render_template("search_tutors.html", tutors=filtered, subjects=subjects,
                           selected_subject=subject, selected_sort=sort)


@app.route("/book/<int:tutor_id>", methods=["GET", "POST"])
@login_required("student")
def book_session(tutor_id):
    with managed_connection() as conn:
        tutor = conn.execute(
            """
            SELECT u.first_name, u.last_name, tp.profile_picture_url
            FROM Users u JOIN TutorProfile tp ON tp.tutor_id = u.user_id
            WHERE tp.tutor_id = %s
            """, (tutor_id,),
        ).fetchone()
        subjects = conn.execute(
            "SELECT s.* FROM Subject s JOIN Teaches t ON t.subject_id = s.subject_id WHERE t.tutor_id = %s",
            (tutor_id,),
        ).fetchall()
        availability = conn.execute(
            "SELECT day_of_week, start_time, end_time FROM Availability WHERE tutor_id = %s ORDER BY day_of_week, start_time",
            (tutor_id,),
        ).fetchall()

    if request.method == "POST":
        requested_dt = parse_session_datetime(request.form["session_time"])
        if not requested_dt:
            flash("Invalid date/time format.")
            return redirect(url_for("book_session", tutor_id=tutor_id))
        if requested_dt <= datetime.now():
            flash("Session time must be in the future.")
            return redirect(url_for("book_session", tutor_id=tutor_id))
        subject_id = int(request.form["subject_id"])
        with managed_connection() as conn:
            if not conn.execute(
                "SELECT 1 FROM Teaches WHERE tutor_id = %s AND subject_id = %s",
                (tutor_id, subject_id)
            ).fetchone():
                flash("Tutor does not teach that subject.")
                return redirect(url_for("book_session", tutor_id=tutor_id))
            if not is_within_availability(conn, tutor_id, requested_dt):
                flash("Requested time is outside tutor availability.")
                return redirect(url_for("book_session", tutor_id=tutor_id))
            conn.execute(
                """
                INSERT INTO TutoringSession
                    (session_time, duration, status, tutor_id, student_id, subject_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (request.form["session_time"], int(request.form["duration"]),
                 "requested", tutor_id, session["user_id"], subject_id),
            )
        flash("Session request sent!")
        return redirect(url_for("student_dashboard"))

    return render_template("book_session.html", tutor=tutor, tutor_id=tutor_id,
                           subjects=subjects, availability=availability)


@app.route("/student/dashboard", methods=["GET", "POST"])
@login_required("student")
def student_dashboard():
    if request.method == "POST":
        session_id = int(request.form["session_id"])
        with managed_connection() as conn:
            current = conn.execute(
                "SELECT status, tutor_id FROM TutoringSession WHERE session_id = %s AND student_id = %s",
                (session_id, session["user_id"]),
            ).fetchone()
            if not current:
                flash("Session not found.")
                return redirect(url_for("student_dashboard"))
            if "canceled" not in VALID_TRANSITIONS.get(current["status"], set()):
                flash("This session can no longer be canceled.")
                return redirect(url_for("student_dashboard"))
            conn.execute(
                "UPDATE TutoringSession SET status = 'canceled' WHERE session_id = %s AND student_id = %s",
                (session_id, session["user_id"]),
            )
            notify_user(conn, current["tutor_id"], f"Student canceled session #{session_id}.")
        flash("Session canceled.")

    with managed_connection() as conn:
        sessions = conn.execute(
            """
            SELECT ts.*, s.subject_name, u.first_name, u.last_name,
                   (SELECT 1 FROM Review r WHERE r.session_id = ts.session_id) AS has_review
            FROM TutoringSession ts
            JOIN Subject s ON s.subject_id = ts.subject_id
            JOIN Users u ON u.user_id = ts.tutor_id
            WHERE ts.student_id = %s
            ORDER BY ts.session_time DESC
            """, (session["user_id"],),
        ).fetchall()
        notifications = conn.execute(
            "SELECT * FROM Notification WHERE user_id = %s ORDER BY created_at DESC",
            (session["user_id"],),
        ).fetchall()
        my_reviews = conn.execute(
            """
            SELECT r.rating, r.comment, s.subject_name,
                   u.first_name AS tutor_first, u.last_name AS tutor_last,
                   ts.session_time
            FROM Review r
            JOIN TutoringSession ts ON ts.session_id = r.session_id
            JOIN Subject s ON s.subject_id = ts.subject_id
            JOIN Users u ON u.user_id = ts.tutor_id
            WHERE r.reviewer_id = %s
            ORDER BY ts.session_time DESC
            """, (session["user_id"],),
        ).fetchall()

    return render_template("student_dashboard.html",
                           sessions=sessions, notifications=notifications,
                           my_reviews=my_reviews)


@app.post("/notification/read/<int:notification_id>")
@login_required()
def mark_notification_read(notification_id):
    with managed_connection() as conn:
        conn.execute(
            "UPDATE Notification SET is_read = 1 WHERE notification_id = %s AND user_id = %s",
            (notification_id, session["user_id"]),
        )
    return redirect(url_for("student_dashboard"))


@app.post("/notification/read-all")
@login_required()
def mark_all_notifications_read():
    with managed_connection() as conn:
        conn.execute(
            "UPDATE Notification SET is_read = 1 WHERE user_id = %s",
            (session["user_id"],),
        )
    flash("All notifications marked as read.")
    return redirect(url_for("student_dashboard"))


@app.route("/review/<int:session_id>", methods=["GET", "POST"])
@login_required("student")
def review(session_id):
    if request.method == "POST":
        with managed_connection() as conn:
            session_row = conn.execute(
                "SELECT status, tutor_id FROM TutoringSession WHERE session_id = %s AND student_id = %s",
                (session_id, session["user_id"]),
            ).fetchone()
            if not session_row or session_row["status"] != "completed":
                flash("You can only review completed sessions you attended.")
                return redirect(url_for("student_dashboard"))
            if conn.execute(
                "SELECT 1 FROM Review WHERE session_id = %s", (session_id,)
            ).fetchone():
                flash("A review already exists for this session.")
                return redirect(url_for("student_dashboard"))
            conn.execute(
                "INSERT INTO Review(rating, comment, session_id, reviewer_id) VALUES (%s, %s, %s, %s)",
                (int(request.form["rating"]), request.form["comment"],
                 session_id, session["user_id"]),
            )
            notify_user(
                conn, session_row["tutor_id"],
                f"{session['name']} left a {request.form['rating']}-star review for session #{session_id}.",
            )
        flash("Review submitted. Thank you!")
        return redirect(url_for("student_dashboard"))
    return render_template("review.html", session_id=session_id)


# ── Tutor ──────────────────────────────────────────────────────────────────────

@app.route("/tutor/profile", methods=["GET", "POST"])
@login_required("tutor")
def tutor_profile():
    uid = session["user_id"]
    with managed_connection() as conn:
        profile      = conn.execute(
            "SELECT * FROM TutorProfile WHERE tutor_id = %s", (uid,)
        ).fetchone()
        all_subjects = conn.execute(
            "SELECT * FROM Subject ORDER BY subject_name"
        ).fetchall()
        taught = {
            row["subject_id"]
            for row in conn.execute(
                "SELECT subject_id FROM Teaches WHERE tutor_id = %s", (uid,)
            ).fetchall()
        }

    if request.method == "POST":
        selected_subjects = request.form.getlist("subject_ids")
        pic_url      = request.form.get("profile_picture_url", "").strip()

        with managed_connection() as conn:
            conn.execute(
                "UPDATE TutorProfile SET bio = %s, hourly_rate = %s, profile_picture_url = %s WHERE tutor_id = %s",
                (request.form["bio"], float(request.form["hourly_rate"]), pic_url, uid),
            )
            conn.execute("DELETE FROM Teaches WHERE tutor_id = %s", (uid,))
            for sid in selected_subjects:
                conn.execute(
                    "INSERT INTO Teaches(tutor_id, subject_id) VALUES (%s, %s)",
                    (uid, int(sid)),
                )
        flash("Profile updated.")
        return redirect(url_for("tutor_profile"))

    with managed_connection() as conn:
        availability = conn.execute(
            "SELECT day_of_week, start_time, end_time FROM Availability WHERE tutor_id = %s ORDER BY day_of_week, start_time",
            (uid,),
        ).fetchall()

    return render_template("tutor_profile.html", profile=profile,
                           all_subjects=all_subjects, taught=taught,
                           availability=availability, day_names=DAY_NAMES)


@app.post("/tutor/availability/add")
@login_required("tutor")
def add_availability_slot():
    day = request.form.get("day_of_week", "")
    start = request.form.get("start_time", "")
    end = request.form.get("end_time", "")
    if day not in DAY_NAMES or not start or not end:
        flash("Please provide day, start time, and end time.")
        return redirect(url_for("tutor_profile"))
    if start >= end:
        flash("Start time must be before end time.")
        return redirect(url_for("tutor_profile"))

    with managed_connection() as conn:
        conn.execute(
            """
            INSERT INTO Availability(tutor_id, day_of_week, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE end_time = VALUES(end_time)
            """,
            (session["user_id"], day, start, end),
        )
    flash("Availability slot saved.")
    return redirect(url_for("tutor_profile"))


@app.post("/tutor/availability/remove")
@login_required("tutor")
def remove_availability_slot():
    day = request.form.get("day_of_week", "")
    start = request.form.get("start_time", "")
    if day not in DAY_NAMES or not start:
        flash("Invalid availability slot selected.")
        return redirect(url_for("tutor_profile"))
    with managed_connection() as conn:
        conn.execute(
            "DELETE FROM Availability WHERE tutor_id = %s AND day_of_week = %s AND start_time = %s",
            (session["user_id"], day, start),
        )
    flash("Availability slot removed.")
    return redirect(url_for("tutor_profile"))


@app.route("/tutor/dashboard", methods=["GET", "POST"])
@login_required("tutor")
def tutor_dashboard():
    if request.method == "POST":
        session_id = int(request.form["session_id"])
        action = request.form["action"]
        status = ("accepted"  if action == "accept"
                  else "completed" if action == "complete"
                  else "canceled")
        with managed_connection() as conn:
            current = conn.execute(
                "SELECT status, student_id FROM TutoringSession WHERE session_id = %s AND tutor_id = %s",
                (session_id, session["user_id"]),
            ).fetchone()
            if not current:
                flash("Session not found.")
                return redirect(url_for("tutor_dashboard"))
            if status not in VALID_TRANSITIONS.get(current["status"], set()):
                flash(f"Cannot change status from {current['status']} to {status}.")
                return redirect(url_for("tutor_dashboard"))
            conn.execute(
                "UPDATE TutoringSession SET status = %s WHERE session_id = %s AND tutor_id = %s",
                (status, session_id, session["user_id"]),
            )
            notify_user(conn, current["student_id"],
                        f"Your session #{session_id} has been {status} by your tutor.")
        flash("Session updated.")

    with managed_connection() as conn:
        sessions = conn.execute(
            """
            SELECT ts.*, u.first_name, u.last_name, s.subject_name
            FROM TutoringSession ts
            JOIN Users u ON u.user_id = ts.student_id
            JOIN Subject s ON s.subject_id = ts.subject_id
            WHERE ts.tutor_id = %s
            ORDER BY ts.session_time DESC
            """, (session["user_id"],),
        ).fetchall()
        notifications = conn.execute(
            "SELECT * FROM Notification WHERE user_id = %s ORDER BY created_at DESC LIMIT 20",
            (session["user_id"],),
        ).fetchall()

    return render_template("tutor_dashboard.html",
                           sessions=sessions, notifications=notifications)


@app.post("/tutor/notification/read-all")
@login_required("tutor")
def tutor_mark_all_read():
    with managed_connection() as conn:
        conn.execute(
            "UPDATE Notification SET is_read = 1 WHERE user_id = %s",
            (session["user_id"],),
        )
    return redirect(url_for("tutor_dashboard"))


@app.get("/tutor/export")
@login_required("tutor")
def export_sessions():
    with managed_connection() as conn:
        rows = conn.execute(
            """
            SELECT ts.session_id, ts.session_time, ts.duration, ts.status,
                   CONCAT(u.first_name, ' ', u.last_name) AS student_name,
                   s.subject_name
            FROM TutoringSession ts
            JOIN Users u ON u.user_id = ts.student_id
            JOIN Subject s ON s.subject_id = ts.subject_id
            WHERE ts.tutor_id = %s
            ORDER BY ts.session_time DESC
            """, (session["user_id"],),
        ).fetchall()
        conn.execute(
            "INSERT INTO SessionExport(file_url, tutor_id) VALUES (%s, %s)",
            ("generated_in_memory.csv", session["user_id"]),
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "session_time", "duration",
                     "status", "student_name", "subject_name"])
    for row in rows:
        writer.writerow([row["session_id"], row["session_time"], row["duration"],
                         row["status"], row["student_name"], row["subject_name"]])
    return Response(
        output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tutor_sessions.csv"},
    )


# ── Admin ──────────────────────────────────────────────────────────────────────

@app.route("/admin/dashboard", methods=["GET", "POST"])
@login_required("admin")
def admin_dashboard():
    if request.method == "POST":
        action    = request.form["action"]
        target_id = int(request.form["target_id"])
        with managed_connection() as conn:
            if action == "delete_review":
                conn.execute("DELETE FROM Review WHERE review_id = %s", (target_id,))
                target_type = "Review"
            elif action == "delete_user":
                conn.execute("DELETE FROM Users WHERE user_id = %s", (target_id,))
                target_type = "User"
            elif action == "delete_subject":
                conn.execute("DELETE FROM Subject WHERE subject_id = %s", (target_id,))
                target_type = "Subject"
            else:
                target_type = "unknown"
            conn.execute(
                "INSERT INTO AdminLog(action_type, target_type, target_id, admin_id) VALUES (%s, %s, %s, %s)",
                (action, target_type, target_id, session["user_id"]),
            )
        flash("Action completed.")

    with managed_connection() as conn:
        users = conn.execute(
            "SELECT user_id, first_name, last_name, email, role FROM Users ORDER BY user_id DESC"
        ).fetchall()
        reviews = conn.execute(
            "SELECT review_id, rating, comment, session_id FROM Review ORDER BY review_id DESC"
        ).fetchall()
        subjects = conn.execute(
            """
            SELECT s.subject_id, s.subject_name,
                   COUNT(DISTINCT t.tutor_id) AS tutor_count
            FROM Subject s
            LEFT JOIN Teaches t ON t.subject_id = s.subject_id
            GROUP BY s.subject_id, s.subject_name
            ORDER BY s.subject_name
            """
        ).fetchall()
        logs = conn.execute(
            "SELECT * FROM AdminLog ORDER BY action_time DESC LIMIT 20"
        ).fetchall()

    return render_template("admin_dashboard.html", users=users, reviews=reviews,
                           subjects=subjects, logs=logs)


@app.route("/admin/add-subject", methods=["POST"])
@login_required("admin")
def add_subject():
    name = request.form.get("subject_name", "").strip()
    if not name:
        flash("Subject name cannot be empty.")
        return redirect(url_for("admin_dashboard"))
    with managed_connection() as conn:
        try:
            conn.execute("INSERT INTO Subject(subject_name) VALUES (%s)", (name,))
            conn.execute(
                "INSERT INTO AdminLog(action_type, target_type, target_id, admin_id) VALUES (%s, %s, %s, %s)",
                ("add_subject", "Subject", 0, session["user_id"]),
            )
            flash(f"Subject '{name}' added.")
        except Exception:
            flash(f"Subject '{name}' already exists.")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/import-subjects", methods=["POST"])
@login_required("admin")
def import_subjects():
    file = request.files.get("csv_file")
    if not file:
        flash("No file selected.")
        return redirect(url_for("admin_dashboard"))
    text_stream = io.StringIO(file.stream.read().decode("utf-8"))
    reader   = csv.DictReader(text_stream)
    imported = 0
    with managed_connection() as conn:
        for row in reader:
            name = (row.get("subject_name") or "").strip()
            if not name:
                continue
            try:
                conn.execute(
                    "INSERT IGNORE INTO Subject(subject_name) VALUES (%s)", (name,)
                )
                imported += 1
            except Exception:
                pass
    flash(f"Imported {imported} subject(s) (duplicates ignored).")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    bootstrap_database()
    app.run(debug=True)