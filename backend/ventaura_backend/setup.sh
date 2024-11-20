#!/bin/bash

echo "Starting automated database setup for Ventaura..."

# Define variables that match appsettings.json
DB_NAME="ventaura"
DB_USER="postgres"
DB_PASSWORD="password"
DB_PORT="5432"
PG_SUPERUSER="postgres"
PG_SUPERPASS="password" 

# Export the superuser password so psql can use it without prompting
export PGPASSWORD=$PG_SUPERPASS

# Create the database and user
psql -U $PG_SUPERUSER -p $DB_PORT -d postgres <<EOSQL
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
