-- ============================================================================
-- LSBA - PostgreSQL application initialization for Bitnami/Kubernetes
--
-- Purpose:
--   - Create application users
--   - Grant database-level permissions
--
-- db_migration_usr and lsba_db are created by the Bitnami PostgreSQL chart
-- from Helm values.
--
-- This script is intended to run during delivery with an admin user such as
-- postgres, while connected to lsba_db.
-- It should be overridden by the CD pipeline to set the correct passwords.
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'db_batch_usr') THEN
        CREATE USER db_batch_usr WITH PASSWORD 'db_batch_usr_pwd';
    ELSE
        ALTER USER db_batch_usr WITH PASSWORD 'db_batch_usr_pwd';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'db_webapp_usr') THEN
        CREATE USER db_webapp_usr WITH PASSWORD 'db_webapp_usr_pwd';
    ELSE
        ALTER USER db_webapp_usr WITH PASSWORD 'db_webapp_usr_pwd';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE lsba_db TO db_batch_usr;
GRANT CONNECT ON DATABASE lsba_db TO db_webapp_usr;

GRANT USAGE ON SCHEMA public TO db_batch_usr;
GRANT USAGE ON SCHEMA public TO db_webapp_usr;
