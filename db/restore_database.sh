#!/bin/bash

# PostgreSQL Database Restore Script
# This script restores a PostgreSQL database from a backup file

set -e  # Exit on any error

# Configuration
CONTAINER_NAME="python-llm-postgres"
DB_NAME="python_llm_db"
DB_USER="postgres"
BACKUP_DIR="./backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PostgreSQL Database Restore Script${NC}"
echo -e "${YELLOW}===================================${NC}"

# Check if Docker container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: PostgreSQL container '$CONTAINER_NAME' is not running.${NC}"
    echo "Please start the container with: docker-compose up -d"
    exit 1
fi

# Function to list available backups
list_backups() {
    echo -e "\n${BLUE}Available backup files:${NC}"
    if ls "$BACKUP_DIR"/*.sql 1> /dev/null 2>&1; then
        ls -lht "$BACKUP_DIR"/*.sql | nl
    else
        echo -e "${RED}No backup files found in $BACKUP_DIR${NC}"
        exit 1
    fi
}

# Check if backup file was provided as argument
if [ $# -eq 0 ]; then
    list_backups
    echo -e "\n${YELLOW}Usage: $0 <backup_file>${NC}"
    echo -e "${YELLOW}   or: $0 latest${NC} (to restore the most recent backup)"
    echo -e "\nExample: $0 postgres_backup_20241201_143022.sql"
    exit 1
fi

# Handle 'latest' option
if [ "$1" = "latest" ]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}No backup files found in $BACKUP_DIR${NC}"
        exit 1
    fi
    BACKUP_FILE=$(basename "$BACKUP_FILE")
else
    BACKUP_FILE="$1"
fi

# Construct full path
if [[ "$BACKUP_FILE" == *"/"* ]]; then
    # Full path provided
    BACKUP_PATH="$BACKUP_FILE"
else
    # Just filename provided
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"
fi

# Check if backup file exists
if [ ! -f "$BACKUP_PATH" ]; then
    echo -e "${RED}Error: Backup file '$BACKUP_PATH' not found.${NC}"
    list_backups
    exit 1
fi

echo -e "\n${YELLOW}Backup file: $BACKUP_PATH${NC}"
BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
echo -e "${YELLOW}File size: $BACKUP_SIZE${NC}"

# Confirmation prompt
echo -e "\n${RED}WARNING: This will completely replace the current database!${NC}"
echo -e "${YELLOW}Current database '$DB_NAME' will be dropped and recreated.${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

echo -e "\n${YELLOW}Starting database restore...${NC}"

# Stop any active connections to the database
echo -e "${YELLOW}Terminating active connections...${NC}"
docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>/dev/null || true

# Restore the database
echo -e "${YELLOW}Restoring database from backup...${NC}"
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres < "$BACKUP_PATH"

# Verify the restore
echo -e "\n${YELLOW}Verifying restore...${NC}"
TABLE_COUNT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Database restored successfully!${NC}"
    echo -e "${GREEN}  Tables found: $TABLE_COUNT${NC}"
    
    # Show table list
    echo -e "\n${BLUE}Tables in restored database:${NC}"
    docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "\dt" 2>/dev/null || echo "No tables to display"
    
    # Check for pgvector extension
    PGVECTOR_EXISTS=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM pg_extension WHERE extname = 'vector';" 2>/dev/null | tr -d ' ')
    if [ "$PGVECTOR_EXISTS" -gt 0 ]; then
        echo -e "${GREEN}✓ pgvector extension is available${NC}"
    else
        echo -e "${YELLOW}⚠ pgvector extension not found - you may need to enable it${NC}"
    fi
else
    echo -e "${RED}✗ Restore verification failed - no tables found${NC}"
    exit 1
fi

echo -e "\n${GREEN}Database restore completed successfully!${NC}" 