#!/bin/sh
set -e

echo "Waiting for SQL Server to become available..."

# Wait until SQL Server is accepting connections on 'master' (always exists).
until python -c "
import os, pyodbc
cs = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=' + os.environ.get('DB_SERVER', 'db') + ';'
    'DATABASE=master;'
    'UID=' + os.environ.get('DB_USERNAME', 'sa') + ';'
    'PWD=' + os.environ.get('DB_PASSWORD', '') + ';'
    'TrustServerCertificate=yes;'
    'Encrypt=no;'
    'Connect Timeout=5'
)
pyodbc.connect(cs)
" 2>/dev/null; do
  echo "  SQL Server is not ready yet - retrying in 3s..."
  sleep 3
done

echo "SQL Server is up. Creating database if it does not exist..."
python backend/database/create_db.py

echo "Initialising tables and seed data..."
python -c "
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from database.init_db import initialize_database
initialize_database()
"

echo "Starting Flask app..."
exec python backend/app.py
