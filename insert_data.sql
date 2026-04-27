-- Insert Admin Users, which is our group
INSERT INTO Users (first_name, last_name, email, role, password_hash)
VALUES
  ('Ethan',   'Zhang',    'dnq8kp@virginia.edu',  'admin', 'pw_ethan'),
  ('Ronit',   'Malhotra', 'vxn4cm@virginia.edu',  'admin', 'pw_ronit'),
  ('Jessica', 'Kim',      'njp9yc@virginia.edu',  'admin', 'pw_jessica');

-- Insert Dummy Student Data
INSERT INTO Users (first_name, last_name, email, role, password_hash)
VALUES
  ('Joe',    'Nguyen',   'joe.student@example.com',    'student', 'pw_joe'),
  ('Mia',    'Patel',    'mia.student@example.com',    'student', 'pw_mia'),
  ('Liam',   'Rivera',   'liam.student@example.com',   'student', 'pw_liam'),
  ('Ava',    'Hughes',   'ava.student@example.com',    'student', 'pw_ava'),
  ('Noah',   'Bennett',  'noah.student@example.com',   'student', 'pw_noah'),
  ('Emma',   'Lopez',    'emma.student@example.com',   'student', 'pw_emma'),
  ('Oliver', 'Park',     'oliver.student@example.com', 'student', 'pw_oliver'),
  ('Sophia', 'Rogers',   'sophia.student@example.com', 'student', 'pw_sophia'),
  ('Lucas',  'Diaz',     'lucas.student@example.com',  'student', 'pw_lucas'),
  ('Grace',  'Chen',     'grace.student@example.com',  'student', 'pw_grace'),
  ('Henry',  'Ward',     'henry.student@example.com',  'student', 'pw_henry'),
  ('Nora',   'Price',    'nora.student@example.com',   'student', 'pw_nora');

-- Insert Dummy Tutor Data
INSERT INTO Users (first_name, last_name, email, role, password_hash)
VALUES
  ('Caleb',   'Stone',   'caleb.tutor@example.com',   'tutor', 'pw_caleb'),
  ('Riya',    'Sharma',  'riya.tutor@example.com',    'tutor', 'pw_riya'),
  ('Marcus',  'Lee',     'marcus.tutor@example.com',  'tutor', 'pw_marcus'),
  ('Diana',   'Garcia',  'diana.tutor@example.com',   'tutor', 'pw_diana'),
  ('Felix',   'Brooks',  'felix.tutor@example.com',   'tutor', 'pw_felix'),
  ('Hannah',  'Khan',    'hannah.tutor@example.com',  'tutor', 'pw_hannah');
  
-- Assuming an empty user table, user_ids would be
-- 1-3: Admins
-- 4-15: Students
-- 16-21: Tutors


-- Insert TutorProfile rows, which would be one per tutor
INSERT INTO TutorProfile (tutor_id, bio, hourly_rate, profile_picture_url)
VALUES
  (16, 'Caleb specializes in Calculus and Physics with 4 years of tutoring experience.', 40.00, 'https://example.com/img/caleb.jpg'),
  (17, 'Riya focuses on Data Structures and Algorithms and SWE interview prep.', 45.00, 'https://example.com/img/riya.jpg'),
  (18, 'Marcus helps beginners in programming and intro to CS courses.', 30.00, 'https://example.com/img/marcus.jpg'),
  (19, 'Diana is a Chemistry and Physics PHD with a lab background.', 38.00, 'https://example.com/img/diana.jpg'),
  (20, 'Felix teaches Statistics and helps with data analysis projects.', 42.50, 'https://example.com/img/felix.jpg'),
  (21, 'Hannah tutors Linear Algebra and other advanced math topics.', 47.00, 'https://example.com/img/hannah.jpg');


-- Insert Subject data
-- IDs
-- 1: Calculus I
-- 2: Linear Algebra
-- 3: Data Structures
-- 4: Algorithms
-- 5: Physics I
-- 6: Chemistry
-- 7: Statistics
-- 8: Intro to Programming

INSERT INTO Subject (subject_name)
VALUES
  ('Calculus I'),
  ('Linear Algebra'),
  ('Data Structures'),
  ('Algorithms'),
  ('Physics I'),
  ('Chemistry'),
  ('Statistics'),
  ('Intro to Programming');


-- Insert Teaches relationships, which is which tutor teachers which subject(s)
INSERT INTO Teaches (tutor_id, subject_id)
VALUES
  (16, 1), -- Caleb teaches Calculus I
  (16, 5), -- Caleb teaches Physics I
  (17, 3), -- Riya teaches Data Structures
  (17, 4), -- Riya teaches Algorithms
  (18, 8), -- Marcus teaches Intro to Programming
  (18, 3), -- Marcus teaches Data Structures
  (19, 6), -- Diana teaches Chemistry
  (19, 5), -- Diana teaches Physics I
  (20, 7), -- Felix teaches Statistics
  (20, 1), -- Felix teaches Calculus I
  (21, 2), -- Hannah teaches Linear Algebra
  (21, 7); -- Hannah teaches Statistics


-- Insert Availability for tutors, which are weekly timeslots
INSERT INTO Availability (tutor_id, day_of_week, start_time, end_time)
VALUES
  (16, 'Monday',    '15:00:00', '17:00:00'), -- Caleb
  (16, 'Wednesday', '10:00:00', '12:00:00'), -- Caleb
  (17, 'Tuesday',   '14:00:00', '16:00:00'), -- Riya
  (17, 'Thursday',  '09:00:00', '11:00:00'), -- Riya
  (18, 'Monday',    '18:00:00', '20:00:00'), -- Marcus
  (18, 'Friday',    '10:00:00', '12:00:00'), -- Marcus
  (19, 'Wednesday', '13:00:00', '15:00:00'), -- Diana
  (19, 'Saturday',  '10:00:00', '12:00:00'), -- Diana
  (20, 'Tuesday',   '16:00:00', '18:00:00'), -- Felix
  (20, 'Thursday',  '18:00:00', '20:00:00'), -- Felix
  (21, 'Friday',    '09:00:00', '11:00:00'), -- Hannah
  (21, 'Sunday',    '15:00:00', '17:00:00'); -- Hannah


-- Insert TutoringSession rows
-- Using tutor_ids 16-21, student_ids 4-15, subject_ids 1-8
-- After this insert below, session_ids will be 1-12 in order
INSERT INTO TutoringSession (session_time, duration, status, tutor_id, student_id, subject_id)
VALUES
  ('2026-03-18 15:00:00', 60, 'completed', 16, 4, 1), -- Caleb with Joe, Calculus I
  ('2026-03-19 16:00:00', 60, 'completed', 16, 5, 1), -- Caleb with Mia, Calculus I
  ('2026-03-20 10:00:00', 90, 'scheduled', 17, 6, 3), -- Riya with Liam, Data Structures
  ('2026-03-21 14:00:00', 60, 'completed', 17, 7, 3), -- Riya with Ava, Data Structures
  ('2026-03-22 11:00:00', 60, 'canceled',  18, 8, 8), -- Marcus with Noah, Intro to Programming
  ('2026-03-23 09:00:00', 60, 'completed', 18, 9, 8), -- Marcus with Emma, Intro to Programming
  ('2026-03-24 13:00:00', 60, 'scheduled', 19, 10, 6), -- Diana with Oliver, Chemistry
  ('2026-03-25 15:30:00', 60, 'completed', 19, 11, 5), -- Diana with Sophia, Physics I
  ('2026-03-26 17:00:00', 60, 'completed', 20, 12, 7), -- Felix with Lucas, Statistics
  ('2026-03-27 10:30:00', 60, 'scheduled', 21, 13, 2), -- Hannah with Grace, Linear Algebra
  ('2026-03-28 16:00:00', 60, 'completed', 21, 14, 2), -- Hannah with Henry, Linear Algebra
  ('2026-03-29 18:00:00', 90, 'completed', 20, 15, 7); -- Felix with Nora, Statistics


-- Insert Review data for completed sessions
INSERT INTO Review (rating, comment, session_id, reviewer_id)
VALUES
  (5, 'Really clarified derivatives and limits.', 1, 4),
  (4, 'Helped me review for the midterm.', 2, 5),
  (5, 'Great explanation of linked lists and recursion.', 4, 7),
  (3, 'Covered the basics, but moved a bit fast.', 6, 9),
  (5, 'Explained projectile motion with clear examples.', 8, 11),
  (4, 'Statistics concepts finally make sense.', 9, 12),
  (5, 'Matrix operations are much easier now.', 11, 14),
  (4, 'Good walkthrough of hypothesis testing on practice data.', 12, 15);


-- Insert Notification data, these are just some simple examples of students
INSERT INTO Notification (message, is_read, created_at, user_id)
VALUES
  ('Your session with Caleb on Calculus I has been completed.', 0, '2026-03-18 16:10:00', 4),
  ('Your session with Riya on Data Structures is scheduled.', 0, '2026-03-20 09:30:00', 6),
  ('Your session with Marcus on Intro to Programming has been completed.', 0, '2026-03-23 10:15:00', 9),
  ('Your session with Diana on Physics I has been completed.', 1, '2026-03-25 17:00:00', 11),
  ('Your session with Felix on Statistics has been completed.', 0, '2026-03-26 18:10:00', 12),
  ('Your session with Hannah on Linear Algebra is scheduled.', 0, '2026-03-27 09:00:00', 13);


-- Insert AdminLog data, which is just actions performed by admins
INSERT INTO AdminLog (action_type, target_type, target_id, action_time, admin_id)
VALUES
  ('CREATE_USER', 'User', 4,  '2026-03-10 09:00:00', 1),
  ('CREATE_USER', 'User', 5,  '2026-03-10 09:05:00', 1),
  ('CREATE_TUTOR', 'TutorProfile', 16, '2026-03-11 10:00:00', 2),
  ('CREATE_TUTOR', 'TutorProfile', 17, '2026-03-11 10:15:00', 2),
  ('CREATE_SESSION', 'TutoringSession', 1, '2026-03-17 14:50:00', 1),
  ('CANCEL_SESSION', 'TutoringSession', 5, '2026-03-22 10:30:00', 2);


-- Insert SessionExport data (dummy csvs exported for tutors)
INSERT INTO SessionExport (export_time, file_url, tutor_id)
VALUES
  ('2026-03-30 20:00:00', 'https://example.com/exports/caleb_march.csv', 16),
  ('2026-03-30 20:15:00', 'https://example.com/exports/riya_march.csv',  17),
  ('2026-03-30 20:30:00', 'https://example.com/exports/felix_march.csv', 20);









