-- =============================================================================
-- 1. Application user (end-user operations)
--    The Flask app connects as this user. It can only read and write data —
--    it cannot create, alter, or drop tables, and it cannot create triggers.
--    This limits blast radius if the app is ever compromised.
-- =============================================================================

-- Drop and recreate to ensure a clean state.
DROP USER IF EXISTS 'tutoring_app_user'@'localhost';
CREATE USER 'tutoring_app_user'@'localhost' IDENTIFIED BY 'AppUser!2025';

-- Grant only the DML operations the app actually needs.
GRANT SELECT, INSERT, UPDATE, DELETE
    ON tutoring_db.*
    TO 'tutoring_app_user'@'localhost';

-- Explicitly confirm no DDL rights (these are denied by default, listed here
-- for documentation and rubric evidence).
-- REVOKE CREATE, DROP, ALTER, INDEX, REFERENCES, TRIGGER
--     ON tutoring_db.*
--     FROM 'tutoring_app_user'@'localhost';


-- =============================================================================
-- 2. Developer user (schema management)
--    Used by the team for migrations, schema updates, and trigger creation.
--    Has full privileges on the tutoring_db database only — not a global admin.
-- =============================================================================

DROP USER IF EXISTS 'tutoring_dev_user'@'localhost';
CREATE USER 'tutoring_dev_user'@'localhost' IDENTIFIED BY 'DevUser!2025';

GRANT ALL PRIVILEGES
    ON tutoring_db.*
    TO 'tutoring_dev_user'@'localhost';


-- =============================================================================
-- Apply changes immediately.
-- =============================================================================
FLUSH PRIVILEGES;


-- =============================================================================
-- Verification queries — run these to confirm privileges are set correctly.
-- =============================================================================

-- Show grants for the app user (should list SELECT, INSERT, UPDATE, DELETE only)
SHOW GRANTS FOR 'tutoring_app_user'@'localhost';

-- Show grants for the dev user (should list ALL PRIVILEGES)
SHOW GRANTS FOR 'tutoring_dev_user'@'localhost';
