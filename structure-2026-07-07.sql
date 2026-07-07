-- ============================================================================
-- LSBA - Database schema
--
-- Purpose:
--   - Create the initial application tables
--   - Grant CRUD permissions required by the batch application user
--   - Grant read/write permissions required by the web application user
--
-- Must be executed while connected to lsba_db as db_migration_usr.
-- db_migration_usr owns and migrates database objects through Alembic.
-- ============================================================================

GRANT USAGE ON SCHEMA public TO db_batch_usr;
GRANT USAGE ON SCHEMA public TO db_webapp_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES
TO db_batch_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT
ON SEQUENCES
TO db_batch_usr;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT
ON TABLES
TO db_webapp_usr;

CREATE TABLE IF NOT EXISTS book (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isbn TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    numero INTEGER NOT NULL,
    titre TEXT NOT NULL,
    authors TEXT[] NOT NULL DEFAULT '{}',
    last_parution_date DATE NOT NULL DEFAULT DATE '1900-01-01',
    description TEXT NOT NULL DEFAULT '',
    official BOOLEAN NOT NULL DEFAULT FALSE,
    image TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS book_price (
    isbn TEXT NOT NULL,
    source TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    price NUMERIC(12,2) NOT NULL,
    url TEXT NOT NULL,
    currency CHAR(3) NOT NULL,

    PRIMARY KEY (isbn, source, date),

    CONSTRAINT fk_book_price_book
        FOREIGN KEY (isbn)
        REFERENCES book(isbn)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS book_acquired (
    isbn TEXT NOT NULL,
    source TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,

    PRIMARY KEY (isbn, source, date),

    CONSTRAINT fk_book_acquired_book_price
        FOREIGN KEY (isbn, source, date)
        REFERENCES book_price(isbn, source, date)
        ON DELETE RESTRICT
);

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO db_batch_usr;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO db_batch_usr;

GRANT SELECT
ON ALL TABLES IN SCHEMA public
TO db_webapp_usr;

GRANT INSERT, UPDATE, DELETE
ON book_acquired
TO db_webapp_usr;
