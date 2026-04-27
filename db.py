import os
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host":        os.environ.get("DB_HOST",     "127.0.0.1"),
    "port":        int(os.environ.get("DB_PORT", "3306")),
    "user":        os.environ.get("DB_USER",     "tutoring_app_user"),
    "password":    os.environ.get("DB_PASSWORD", ""),
    "database":    os.environ.get("DB_NAME",     "tutoring_db"),
    "cursorclass": pymysql.cursors.DictCursor,
    "charset":     "utf8mb4",
    "autocommit":  False,
}


def get_connection():
    """Return a raw PyMySQL connection."""
    return pymysql.connect(**DB_CONFIG)


@contextmanager
def managed_connection():
    """
    Context manager that yields a _ConnWrapper.
    Commits on clean exit, rolls back on exception, always closes.
    Usage (same as old SQLite pattern):
        with managed_connection() as conn:
            conn.execute("SELECT ...", (...,))
    """
    raw  = get_connection()
    conn = _ConnWrapper(raw)
    try:
        yield conn
        raw.commit()
    except Exception:
        raw.rollback()
        raise
    finally:
        raw.close()


class _ConnWrapper:
    """
    Thin wrapper so app.py can call conn.execute(sql, params) and
    conn.commit() exactly as it did with SQLite.
    """
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def execute(self, sql, params=()):
        cur = self._conn.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def __getattr__(self, name):
        return getattr(self._conn, name)


# ── Bootstrap ──────────────────────────────────────────────────────────────────

def bootstrap_database():
    """
    Create all 10 tables, the trigger, and seed data if the DB is empty.
    Safe to call on every startup — uses CREATE TABLE IF NOT EXISTS throughout.
    Trigger creation is wrapped in try/except: if the app DB user lacks
    TRIGGER privilege the app still starts; create the trigger manually in
    phpMyAdmin using the root account instead.
    """
    raw = get_connection()
    cur = raw.cursor()

    # Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id       INT AUTO_INCREMENT PRIMARY KEY,
            first_name    VARCHAR(50)  NOT NULL,
            last_name     VARCHAR(50)  NOT NULL,
            email         VARCHAR(255) NOT NULL UNIQUE,
            role          VARCHAR(20)  NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # TutorProfile
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TutorProfile (
            tutor_id            INT           PRIMARY KEY,
            bio                 TEXT,
            hourly_rate         DECIMAL(10,2) NOT NULL,
            profile_picture_url VARCHAR(500),
            CONSTRAINT chk_tutor_hourly_rate_positive CHECK (hourly_rate > 0),
            FOREIGN KEY (tutor_id) REFERENCES Users(user_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Subject
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Subject (
            subject_id   INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Teaches  (M:N bridge)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Teaches (
            tutor_id   INT NOT NULL,
            subject_id INT NOT NULL,
            PRIMARY KEY (tutor_id, subject_id),
            FOREIGN KEY (tutor_id)   REFERENCES TutorProfile(tutor_id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Availability  (weak entity)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Availability (
            tutor_id    INT         NOT NULL,
            day_of_week VARCHAR(10) NOT NULL,
            start_time  TIME        NOT NULL,
            end_time    TIME        NOT NULL,
            PRIMARY KEY (tutor_id, day_of_week, start_time),
            FOREIGN KEY (tutor_id) REFERENCES TutorProfile(tutor_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # TutoringSession
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TutoringSession (
            session_id   INT AUTO_INCREMENT PRIMARY KEY,
            session_time DATETIME    NOT NULL,
            duration     INT         NOT NULL,
            status       VARCHAR(20) NOT NULL,
            tutor_id     INT         NOT NULL,
            student_id   INT         NOT NULL,
            subject_id   INT         NOT NULL,
            CONSTRAINT chk_session_status_valid
                CHECK (status IN ('requested','accepted','completed','canceled')),
            FOREIGN KEY (tutor_id)   REFERENCES TutorProfile(tutor_id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (student_id) REFERENCES Users(user_id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Review
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Review (
            review_id   INT AUTO_INCREMENT PRIMARY KEY,
            rating      INT  NOT NULL,
            comment     TEXT,
            session_id  INT  NOT NULL UNIQUE,
            reviewer_id INT  NOT NULL,
            CONSTRAINT chk_review_rating_range CHECK (rating BETWEEN 1 AND 5),
            FOREIGN KEY (session_id)  REFERENCES TutoringSession(session_id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (reviewer_id) REFERENCES Users(user_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # Notification
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Notification (
            notification_id INT AUTO_INCREMENT PRIMARY KEY,
            message         TEXT       NOT NULL,
            is_read         TINYINT(1) NOT NULL DEFAULT 0,
            created_at      DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id         INT        NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # SessionExport
    cur.execute("""
        CREATE TABLE IF NOT EXISTS SessionExport (
            export_id   INT AUTO_INCREMENT PRIMARY KEY,
            export_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            file_url    VARCHAR(500),
            tutor_id    INT          NOT NULL,
            FOREIGN KEY (tutor_id) REFERENCES TutorProfile(tutor_id)
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # AdminLog
    cur.execute("""
        CREATE TABLE IF NOT EXISTS AdminLog (
            log_id      INT AUTO_INCREMENT PRIMARY KEY,
            action_type VARCHAR(100) NOT NULL,
            target_type VARCHAR(100) NOT NULL,
            target_id   INT          NOT NULL,
            action_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            admin_id    INT          NOT NULL,
            FOREIGN KEY (admin_id) REFERENCES Users(user_id)
                ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # ── Trigger ────────────────────────────────────────────────────────────────
    # Automatically notify the student whenever a new TutoringSession is created.
    # Wrapped in try/except: if the app DB user lacks TRIGGER privilege the app
    # still starts. In that case, create the trigger once manually in phpMyAdmin
    # while logged in as root.
    try:
        cur.execute("DROP TRIGGER IF EXISTS trg_notification_on_session_create")
        cur.execute("""
            CREATE TRIGGER trg_notification_on_session_create
            AFTER INSERT ON TutoringSession
            FOR EACH ROW
            BEGIN
                DECLARE tutor_first VARCHAR(50);
                DECLARE tutor_last  VARCHAR(50);
                SELECT first_name, last_name
                  INTO tutor_first, tutor_last
                  FROM Users
                 WHERE user_id = NEW.tutor_id;
                INSERT INTO Notification(message, is_read, created_at, user_id)
                VALUES (
                    CONCAT('Your tutoring session on ', DATE(NEW.session_time),
                           ' with ', tutor_first, ' ', tutor_last,
                           ' has been ', NEW.status, '.'),
                    0,
                    NOW(),
                    NEW.student_id
                );
            END
        """)
        print("[db] Trigger created.")
    except Exception as e:
        print(f"[db] Warning: could not create trigger ({e}). "
              "Create it manually in phpMyAdmin as root if needed.")

    # ── Seed data ──────────────────────────────────────────────────────────────
    cur.execute("SELECT COUNT(*) AS c FROM Subject")
    if cur.fetchone()["c"] == 0:
        for name in [
            "Algorithms", "Calculus I", "Chemistry",
            "Computer Science", "Data Structures", "Intro to Programming",
            "Linear Algebra", "Physics I", "Statistics",
        ]:
            cur.execute("INSERT IGNORE INTO Subject(subject_name) VALUES (%s)", (name,))

    cur.execute("SELECT COUNT(*) AS c FROM Users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO Users(first_name,last_name,email,role,password_hash) VALUES (%s,%s,%s,%s,%s)",
            ("Admin", "User", "admin@school.edu", "admin",
             generate_password_hash("AdminPass123!")),
        )

    raw.commit()
    cur.close()
    raw.close()
    print("[db] Bootstrap complete.")