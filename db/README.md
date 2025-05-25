# PostgreSQL Docker Setup

This directory contains a PostgreSQL database setup using Docker that can be accessed by Python scripts throughout the project.

## Quick Start

1. **Start the database:**
   ```bash
   cd db
   docker-compose up -d
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the connection:**
   ```bash
   python database.py
   ```

## Database Configuration

- **Host:** localhost
- **Port:** 5432
- **Database:** python_llm_db
- **Username:** postgres
- **Password:** postgres123

## Files

- `docker-compose.yml` - Docker Compose configuration for PostgreSQL
- `init/01-init.sql` - Database initialization script (runs on first startup)
- `config.py` - Database connection configuration
- `database.py` - Python utility functions for database operations
- `requirements.txt` - Python dependencies for database connectivity

## Usage from Other Folders

To use the database from Python scripts in other folders (like `openai-pdf/`), you can import the database utilities:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection

# Use the database
db = DatabaseConnection()
if db.connect():
    # Your database operations here
    users = db.execute_query("SELECT * FROM users")
    print(users)
    db.disconnect()
```

## Docker Commands

- **Start database:** `docker-compose up -d`
- **Stop database:** `docker-compose down`
- **View logs:** `docker-compose logs postgres`
- **Access PostgreSQL shell:** `docker exec -it python-llm-postgres psql -U postgres -d python_llm_db`

## Sample Tables

The database is initialized with two sample tables:

1. **users** - Sample user table with id, username, email, created_at
2. **documents** - Table for storing document metadata (useful for PDF processing)

## Environment Variables

You can override the default database configuration by setting these environment variables:

- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: python_llm_db)
- `DB_USER` (default: postgres)
- `DB_PASSWORD` (default: postgres123) 