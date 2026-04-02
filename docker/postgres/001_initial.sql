-- AgentCanvas — PostgreSQL Bootstrap
-- Mounted into postgres container at /docker-entrypoint-initdb.d/001_initial.sql
-- Runs automatically on first docker-compose up
--
-- IMPORTANT:
-- Alembic migrations are the single source of truth for the schema.
-- This script should only bootstrap DB-level prerequisites.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTE:
-- Tables, indexes, constraints, triggers, and sample data are created by Alembic.
