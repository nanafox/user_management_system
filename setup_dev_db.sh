#!/bin/bash

source .env

# create a user
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Create a new PostgreSQL database and assign it to the user
psql -U postgres -c "CREATE DATABASE ${DB_NAME} OWNER $DB_USER;"

# grant permissions to the user
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO $DB_USER;"

echo "User '$DB_USER' and Database ${DB_NAME}_test created successfully for testing."
