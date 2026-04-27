# TutorConnect — Peer-to-Peer Tutoring Marketplace
CS 4750
Ronit Malhotra (vxn4cm), Jessica Kim (njp9yc), Ethan Zhang (dnq8kp)

## Overview
TutorConnect is a web-based peer-to-peer tutoring marketplace backed by a MySQL relational database. Students can search for tutors, book sessions, and leave reviews. Tutors manage their profiles, availability, and session requests. Admins manage users and subjects.

---

## Tech Stack
- **Backend:** Python 3 + Flask
- **Database:** MySQL 8 via XAMPP (local)
- **Frontend:** Jinja2 HTML templates + vanilla CSS
- **Auth:** Werkzeug password hashing (bcrypt)

---

## Prerequisites
- [XAMPP](https://www.apachefriends.org/) with MySQL running
- Python 3.9 or higher
- pip

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-github-url>
cd tutoring_app
```

### 2. Install Python dependencies
```bash
pip install flask pymysql werkzeug
```

### 3. Start XAMPP MySQL
Open the XAMPP Control Panel and click **Start** next to MySQL.

### 4. Create the database and tables
Open your browser and go to `http://localhost/phpmyadmin`.

In the SQL tab, run:
```sql
CREATE DATABASE IF NOT EXISTS tutoring_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tutoring_db;
```

Then paste and run the contents of `schema_mysql.sql` to create all 10 tables and the trigger.

### 5. Set up database security (required for rubric)
Still in phpMyAdmin (logged in as root), paste and run the contents of `security_mysql.sql`.
This creates the restricted `tutoring_app_user` account the app connects as.

### 6. Configure environment variables
Copy `.env.example` to `.env` and fill in your password:
```bash
cp .env.example .env
```

Edit `.env`:
```
FLASK_SECRET_KEY=any-long-random-string
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=tutoring_app_user
DB_PASSWORD=AppUser!2025
DB_NAME=tutoring_db
```

Load the environment variables before running:

**Mac/Linux:**
```bash
export $(cat .env | xargs)
```

**Windows (Command Prompt):**
```cmd
for /f "tokens=*" %i in (.env) do set %i
```

### 7. Run the app
```bash
python app.py
```

Open your browser at `http://127.0.0.1:5000`.

---

## Default Admin Account
On first run, `bootstrap_database()` seeds an admin user:
- **Email:** admin@school.edu
- **Password:** AdminPass123!

Use this to log in to the Admin Dashboard.

---

## Database Tables Used (all 10)
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
- **DB level:** `tutoring_app_user` has only `SELECT, INSERT, UPDATE, DELETE` — no DDL. `tutoring_dev_user` has full privileges for schema changes. See `security_mysql.sql`.
- **App level:** Passwords hashed with Werkzeug (bcrypt). `login_required()` decorator blocks unauthenticated access. Role-based routing sends students, tutors, and admins to separate dashboards. Prepared statements (`%s` placeholders via PyMySQL) prevent SQL injection.