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
-- This script is intended to run once during PostgreSQL initialization.
-- It should be overridden by the CD pipeline to set the correct passwords.
-- ============================================================================

CREATE USER db_batch_usr WITH PASSWORD 'db_batch_usr_pwd';
CREATE USER db_webapp_usr WITH PASSWORD 'db_webapp_usr_pwd';

GRANT CONNECT ON DATABASE lsba_db TO db_batch_usr;
GRANT CONNECT ON DATABASE lsba_db TO db_webapp_usr;