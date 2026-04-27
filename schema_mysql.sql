
-- Drop tables in reverse dependency order so FK constraints don't block drops.
DROP TABLE IF EXISTS AdminLog;
DROP TABLE IF EXISTS SessionExport;
DROP TABLE IF EXISTS Notification;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS TutoringSession;
DROP TABLE IF EXISTS Availability;
DROP TABLE IF EXISTS Teaches;
DROP TABLE IF EXISTS TutorProfile;
DROP TABLE IF EXISTS Subject;
DROP TABLE IF EXISTS Users;

-- =============================================================================
-- 1. Users
--    Stores all platform users (students, tutors, admins).
--    email is a candidate key (UNIQUE).
-- =============================================================================
CREATE TABLE Users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(50)  NOT NULL,
    last_name     VARCHAR(50)  NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    role          VARCHAR(20)  NOT NULL,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 2. TutorProfile
--    Tutor-specific data separated from Users to avoid NULL-heavy rows for
--    non-tutor accounts. tutor_id is both PK and FK to Users (1:1 extension).
-- =============================================================================
CREATE TABLE TutorProfile (
    tutor_id            INT           PRIMARY KEY,
    bio                 TEXT,
    hourly_rate         DECIMAL(10,2) NOT NULL,
    profile_picture_url VARCHAR(500),
    CONSTRAINT chk_tutor_hourly_rate_positive CHECK (hourly_rate > 0),
    FOREIGN KEY (tutor_id) REFERENCES Users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 3. Subject
--    Academic subjects available on the platform. subject_name is a candidate
--    key (UNIQUE).
-- =============================================================================
CREATE TABLE Subject (
    subject_id   INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 4. Teaches  (M:N relationship table)
--    A tutor can teach many subjects; a subject can be taught by many tutors.
--    Maps to the TEACHES relationship in the E-R diagram.
-- =============================================================================
CREATE TABLE Teaches (
    tutor_id   INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (tutor_id, subject_id),
    FOREIGN KEY (tutor_id)   REFERENCES TutorProfile(tutor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 5. Availability  (weak entity)
--    Weekly availability slots for tutors. Composite PK includes tutor_id
--    because slots have no meaning outside the context of their tutor.
--    A tutor cannot have two entries with the same (day_of_week, start_time).
-- =============================================================================
CREATE TABLE Availability (
    tutor_id    INT         NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time  TIME        NOT NULL,
    end_time    TIME        NOT NULL,
    PRIMARY KEY (tutor_id, day_of_week, start_time),
    FOREIGN KEY (tutor_id) REFERENCES TutorProfile(tutor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 6. TutoringSession  (central entity)
--    Connects student ↔ tutor ↔ subject. Total participation on all three FK
--    sides (NOT NULL). Status is constrained to four valid workflow states.
-- =============================================================================
CREATE TABLE TutoringSession (
    session_id   INT AUTO_INCREMENT PRIMARY KEY,
    session_time DATETIME    NOT NULL,
    duration     INT         NOT NULL,          -- minutes
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 7. Review
--    One review per session (UNIQUE on session_id). Rating constrained 1–5.
--    reviewer_id ties the review to the student who wrote it for accountability.
-- =============================================================================
CREATE TABLE Review (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 8. Notification
--    System notifications sent to users. Populated automatically by the
--    trg_notification_on_session_create trigger (see below).
-- =============================================================================
CREATE TABLE Notification (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    message         TEXT       NOT NULL,
    is_read         TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id         INT        NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 9. SessionExport
--    Audit trail of CSV exports generated by tutors through the app.
-- =============================================================================
CREATE TABLE SessionExport (
    export_id   INT AUTO_INCREMENT PRIMARY KEY,
    export_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_url    VARCHAR(500),
    tutor_id    INT          NOT NULL,
    FOREIGN KEY (tutor_id) REFERENCES TutorProfile(tutor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- 10. AdminLog
--     Audit trail of administrative actions (delete user, delete review, etc.).
-- =============================================================================
CREATE TABLE AdminLog (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(100) NOT NULL,
    target_type VARCHAR(100) NOT NULL,
    target_id   INT          NOT NULL,
    action_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    admin_id    INT          NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES Users(user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =============================================================================
-- Advanced SQL: TRIGGER
-- Automatically inserts a Notification for the student whenever a new
-- TutoringSession row is created, regardless of which app component did the
-- INSERT. This enforces the notification workflow at the database level.
-- =============================================================================
DROP TRIGGER IF EXISTS trg_notification_on_session_create;

DELIMITER $$
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
END$$
DELIMITER ;


-- =============================================================================
-- Seed Data — Subjects
-- =============================================================================
INSERT IGNORE INTO Subject(subject_name) VALUES
    ('Algorithms'),
    ('Calculus I'),
    ('Chemistry'),
    ('Computer Science'),
    ('Data Structures'),
    ('Intro to Programming'),
    ('Linear Algebra'),
    ('Physics I'),
    ('Statistics');