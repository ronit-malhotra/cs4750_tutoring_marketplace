-- =============================================================================
-- Dummy data for TutorConnect
--
-- Assumes bootstrap_database() has already run, which seeds:
--   user_id=1  -> admin@school.edu  (admin)
--   subject_ids: 1=Algorithms, 2=Calculus I, 3=Chemistry, 4=Computer Science,
--                5=Data Structures, 6=Intro to Programming, 7=Linear Algebra,
--                8=Physics I, 9=Statistics
--
-- All dummy users share the password: Password123!
-- =============================================================================

-- Team admin accounts (user_ids 2-4)
INSERT INTO Users (first_name, last_name, email, role, password_hash) VALUES
  ('Ethan',   'Zhang',    'dnq8kp@virginia.edu',  'admin', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Ronit',   'Malhotra', 'vxn4cm@virginia.edu',  'admin', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Jessica', 'Kim',      'njp9yc@virginia.edu',  'admin', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3');

-- Student accounts (user_ids 5-16)
INSERT INTO Users (first_name, last_name, email, role, password_hash) VALUES
  ('Joe',    'Nguyen',   'joe.student@example.com',    'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Mia',    'Patel',    'mia.student@example.com',    'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Liam',   'Rivera',   'liam.student@example.com',   'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Ava',    'Hughes',   'ava.student@example.com',    'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Noah',   'Bennett',  'noah.student@example.com',   'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Emma',   'Lopez',    'emma.student@example.com',   'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Oliver', 'Park',     'oliver.student@example.com', 'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Sophia', 'Rogers',   'sophia.student@example.com', 'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Lucas',  'Diaz',     'lucas.student@example.com',  'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Grace',  'Chen',     'grace.student@example.com',  'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Henry',  'Ward',     'henry.student@example.com',  'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Nora',   'Price',    'nora.student@example.com',   'student', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3');

-- Tutor accounts (user_ids 17-22)
INSERT INTO Users (first_name, last_name, email, role, password_hash) VALUES
  ('Caleb',   'Stone',   'caleb.tutor@example.com',   'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Riya',    'Sharma',  'riya.tutor@example.com',    'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Marcus',  'Lee',     'marcus.tutor@example.com',  'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Diana',   'Garcia',  'diana.tutor@example.com',   'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Felix',   'Brooks',  'felix.tutor@example.com',   'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3'),
  ('Hannah',  'Khan',    'hannah.tutor@example.com',  'tutor', 'scrypt:32768:8:1$wSHcnRZTk2XNmIcb$2f36eab4f632987c72c0c35e258c50f2aebccc2749d09699fcb65c01bd955b73c70b2d467d37b8929bb99133798e91731fa9918465ca8548b214d65538825be3');

-- TutorProfile (tutor user_ids 17-22)
INSERT INTO TutorProfile (tutor_id, bio, hourly_rate, profile_picture_url) VALUES
  (17, 'Caleb specializes in Calculus and Physics with 4 years of tutoring experience.', 40.00, NULL),
  (18, 'Riya focuses on Data Structures and Algorithms and SWE interview prep.',         45.00, NULL),
  (19, 'Marcus helps beginners in programming and intro to CS courses.',                  30.00, NULL),
  (20, 'Diana is a Chemistry and Physics PhD with a lab background.',                     38.00, NULL),
  (21, 'Felix teaches Statistics and helps with data analysis projects.',                 42.50, NULL),
  (22, 'Hannah tutors Linear Algebra and other advanced math topics.',                    47.00, NULL);

-- Teaches (subject_ids from bootstrap: 1=Algorithms, 2=Calculus I, 3=Chemistry,
--          5=Data Structures, 6=Intro to Programming, 7=Linear Algebra, 8=Physics I, 9=Statistics)
INSERT INTO Teaches (tutor_id, subject_id) VALUES
  (17, 2), -- Caleb teaches Calculus I
  (17, 8), -- Caleb teaches Physics I
  (18, 5), -- Riya teaches Data Structures
  (18, 1), -- Riya teaches Algorithms
  (19, 6), -- Marcus teaches Intro to Programming
  (19, 5), -- Marcus teaches Data Structures
  (20, 3), -- Diana teaches Chemistry
  (20, 8), -- Diana teaches Physics I
  (21, 9), -- Felix teaches Statistics
  (21, 2), -- Felix teaches Calculus I
  (22, 7), -- Hannah teaches Linear Algebra
  (22, 9); -- Hannah teaches Statistics

-- Availability
INSERT INTO Availability (tutor_id, day_of_week, start_time, end_time) VALUES
  (17, 'Monday',    '15:00:00', '17:00:00'),
  (17, 'Wednesday', '10:00:00', '12:00:00'),
  (18, 'Tuesday',   '14:00:00', '16:00:00'),
  (18, 'Thursday',  '09:00:00', '11:00:00'),
  (19, 'Monday',    '18:00:00', '20:00:00'),
  (19, 'Friday',    '10:00:00', '12:00:00'),
  (20, 'Wednesday', '13:00:00', '15:00:00'),
  (20, 'Saturday',  '10:00:00', '12:00:00'),
  (21, 'Tuesday',   '16:00:00', '18:00:00'),
  (21, 'Thursday',  '18:00:00', '20:00:00'),
  (22, 'Friday',    '09:00:00', '11:00:00'),
  (22, 'Sunday',    '15:00:00', '17:00:00');

-- TutoringSession (statuses: requested/accepted/completed/canceled)
INSERT INTO TutoringSession (session_time, duration, status, tutor_id, student_id, subject_id) VALUES
  ('2026-03-18 15:00:00', 60, 'completed', 17,  5, 2), -- Caleb + Joe,    Calculus I
  ('2026-03-19 16:00:00', 60, 'completed', 17,  6, 2), -- Caleb + Mia,    Calculus I
  ('2026-03-20 10:00:00', 90, 'accepted',  18,  7, 5), -- Riya  + Liam,   Data Structures
  ('2026-03-21 14:00:00', 60, 'completed', 18,  8, 5), -- Riya  + Ava,    Data Structures
  ('2026-03-22 11:00:00', 60, 'canceled',  19,  9, 6), -- Marcus + Noah,  Intro to Programming
  ('2026-03-23 09:00:00', 60, 'completed', 19, 10, 6), -- Marcus + Emma,  Intro to Programming
  ('2026-03-24 13:00:00', 60, 'accepted',  20, 11, 3), -- Diana  + Oliver, Chemistry
  ('2026-03-25 15:30:00', 60, 'completed', 20, 12, 8), -- Diana  + Sophia, Physics I
  ('2026-03-26 17:00:00', 60, 'completed', 21, 13, 9), -- Felix  + Lucas,  Statistics
  ('2026-03-27 10:30:00', 60, 'accepted',  22, 14, 7), -- Hannah + Grace,  Linear Algebra
  ('2026-03-28 16:00:00', 60, 'completed', 22, 15, 7), -- Hannah + Henry,  Linear Algebra
  ('2026-03-29 18:00:00', 90, 'completed', 21, 16, 9); -- Felix  + Nora,   Statistics

-- Reviews (only for completed sessions: 1,2,4,6,8,9,11,12)
INSERT INTO Review (rating, comment, session_id, reviewer_id) VALUES
  (5, 'Really clarified derivatives and limits.',            1,  5),
  (4, 'Helped me review for the midterm.',                   2,  6),
  (5, 'Great explanation of linked lists and recursion.',    4,  8),
  (3, 'Covered the basics, but moved a bit fast.',           6, 10),
  (5, 'Explained projectile motion with clear examples.',    8, 12),
  (4, 'Statistics concepts finally make sense.',             9, 13),
  (5, 'Matrix operations are much easier now.',             11, 15),
  (4, 'Good walkthrough of hypothesis testing.',            12, 16);

-- Notifications
INSERT INTO Notification (message, is_read, created_at, user_id) VALUES
  ('Your tutoring session on 2026-03-18 with Caleb Stone has been requested.',   0, '2026-03-18 16:10:00',  5),
  ('Your tutoring session on 2026-03-20 with Riya Sharma has been accepted.',    0, '2026-03-20 09:30:00',  7),
  ('Your tutoring session on 2026-03-23 with Marcus Lee has been requested.',    0, '2026-03-23 10:15:00', 10),
  ('Your tutoring session on 2026-03-25 with Diana Garcia has been completed.',  1, '2026-03-25 17:00:00', 12),
  ('Your tutoring session on 2026-03-26 with Felix Brooks has been completed.',  0, '2026-03-26 18:10:00', 13),
  ('Your tutoring session on 2026-03-27 with Hannah Khan has been accepted.',    0, '2026-03-27 09:00:00', 14);

-- AdminLog
INSERT INTO AdminLog (action_type, target_type, target_id, action_time, admin_id) VALUES
  ('CREATE_USER',    'User',           5,  '2026-03-10 09:00:00', 2),
  ('CREATE_USER',    'User',           6,  '2026-03-10 09:05:00', 2),
  ('CREATE_TUTOR',   'TutorProfile',  17,  '2026-03-11 10:00:00', 3),
  ('CREATE_TUTOR',   'TutorProfile',  18,  '2026-03-11 10:15:00', 3),
  ('CREATE_SESSION', 'TutoringSession', 1, '2026-03-17 14:50:00', 2),
  ('CANCEL_SESSION', 'TutoringSession', 5, '2026-03-22 10:30:00', 3);

-- SessionExport
INSERT INTO SessionExport (export_time, file_url, tutor_id) VALUES
  ('2026-03-30 20:00:00', NULL, 17),
  ('2026-03-30 20:15:00', NULL, 18),
  ('2026-03-30 20:30:00', NULL, 21);
