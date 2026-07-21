-- Run once, on the Postgres server behind 127.0.0.1:6432, by a superuser (or a role
-- with CREATEDB/CREATEROLE). Creates a NEW, isolated database for the bot — it does
-- NOT touch the existing production database (e.g. lntech_db) or its data.
--
--   psql -h 127.0.0.1 -p 6432 -U <superuser> -f scripts/create_database.sql
--
-- Replace CHANGE_ME_PASSWORD below with a real password before running, then put the
-- same value in the server's .env as DB_PASS (never commit the real password to git).

CREATE ROLE lntech_bot WITH LOGIN PASSWORD 'CHANGE_ME_PASSWORD';

CREATE DATABASE lntech_bot_db OWNER lntech_bot;

-- Dedicated role scoped to only lntech_bot_db, so the bot has no access to the
-- existing lntech_db (which already has production data from the Django app).
