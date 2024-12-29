#!/bin/bash
set -e

# Wait for the database to be ready
until psql -U postgres -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Create the app database and user
psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE DATABASE raven_db;
    CREATE USER app_user WITH PASSWORD 'app_password';
    GRANT ALL PRIVILEGES ON DATABASE raven_db TO app_user;

    -- Optional: Instead of dropping the postgres role, disable login for security
    ALTER ROLE postgres NOLOGIN;
EOSQL
