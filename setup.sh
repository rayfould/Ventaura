#!/bin/bash

echo "Starting database setup for Ventaura..."

# Prompt for PostgreSQL credentials
read -p "Enter your PostgreSQL username (default: postgres): " PGUSER
PGUSER=${PGUSER:-postgres} # Default to 'postgres' if no input

read -s -p "Enter your PostgreSQL password: " PGPASSWORD
echo

# Prompt for custom database details (optional)
DB_NAME="ventaura"
DB_USER="postgres"
DB_PASSWORD="password"
DB_PORT="5432"

# Connect to PostgreSQL and execute the setup commands
psql -U $PGUSER -p $DB_PORT -d postgres <<EOSQL
CREATE DATABASE $DB_NAME;
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = '$DB_USER') THEN
      CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASSWORD';
   END IF;
END
\$do\$;

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL

echo "Database setup completed successfully!"
