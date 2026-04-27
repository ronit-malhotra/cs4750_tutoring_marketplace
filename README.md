# TutorConnect — Peer-to-Peer Tutoring Marketplace
CS 4750
Ronit Malhotra (vxn4cm), Jessica Kim (njp9yc), Ethan Zhang (dnq8kp)

## Overview
TutorConnect is a web-based peer-to-peer tutoring marketplace backed by a MySQL relational database. Students can search for tutors, book sessions, and leave reviews. Tutors manage their profiles, availability, and session requests. Admins manage users and subjects.

---

## Live Deployment (GCP)
**App URL:** https://tutoring-app-1041453566779.us-central1.run.app

---

## Tech Stack
- **Backend:** Python 3.12 + Flask
- **Database:** MySQL 8
- **Frontend:** Jinja2 HTML templates + vanilla CSS
- **Auth:** Werkzeug password hashing (scrypt)

---

## Prerequisites
- Python 3.9 or higher
- MySQL 8 running locally

---

## Local Setup

### 1. Clone the repository
```bash
git clone <your-github-url>
cd cs4750_tutoring_marketplace
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create the database
```bash
mysql -u root -p
```
```sql
CREATE DATABASE IF NOT EXISTS tutoring_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tutoring_db;
```
Then paste and run the contents of `schema_mysql.sql`.

### 5. Set up database security
```bash
mysql -u root -p < security_sql.sql
```

### 6. Set environment variables
```bash
export FLASK_SECRET_KEY=any-long-random-string
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_USER=tutoring_dev_user
export DB_PASSWORD='DevUser!2025'
export DB_NAME=tutoring_db
```

### 7. (Optional) Load dummy data
```bash
mysql -u root -p tutoring_db < insert_data.sql
```

### 8. Run the app
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## Default Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@school.edu | AdminPass123! |
| Tutor (demo) | caleb.tutor@example.com | Password123! |
| Student (demo) | joe.student@example.com | Password123! |

---

## Database Tables Used
| Table | Purpose |
|---|---|
| Users | All platform users — students, tutors, admins |
| TutorProfile | Tutor-specific data (bio, rate, photo) |
| Subject | Academic subjects available on the platform |
| Teaches | M:N — which tutors teach which subjects |
| Availability | Weekly availability slots per tutor |
| TutoringSession | Booked sessions connecting student ↔ tutor ↔ subject |
| Review | Student reviews of completed sessions |
| Notification | System notifications (auto-created by DB trigger) |
| SessionExport | Audit log of CSV exports by tutors |
| AdminLog | Audit log of admin actions |

---

## Advanced SQL Features
- **Trigger** (`trg_notification_on_session_create`): fires `AFTER INSERT ON TutoringSession`, automatically inserts a `Notification` row for the student without requiring the app to make a second INSERT call.
- **CHECK constraints**: `chk_review_rating_range` (rating 1–5), `chk_tutor_hourly_rate_positive` (rate > 0), `chk_session_status_valid` (status must be one of four valid states).

---

## Database Security
- **DB level:** `tutoring_app_user` has only `SELECT, INSERT, UPDATE, DELETE` — no DDL. `tutoring_dev_user` has full privileges for schema changes. See `security_sql.sql`.
- **App level:** Passwords hashed with Werkzeug (scrypt). `login_required()` decorator blocks unauthenticated access. Role-based routing sends students, tutors, and admins to separate dashboards. Prepared statements (`%s` placeholders via PyMySQL) prevent SQL injection.
