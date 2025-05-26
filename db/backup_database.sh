#!/bin/bash

# PostgreSQL Database Backup Script
# This script creates a backup of the PostgreSQL database with pgvector extension

set -e  # Exit on any error

# Configuration
CONTAINER_NAME="python-llm-postgres"
DB_NAME="python_llm_db"
DB_USER="postgres"
BACKUP_DIR="./backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="postgres_backup_${TIMESTAMP}.sql"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting PostgreSQL database backup...${NC}"

# Check if Docker container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}Error: PostgreSQL container '$CONTAINER_NAME' is not running.${NC}"
    echo "Please start the container with: docker-compose up -d"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create the backup
echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" --verbose --clean --if-exists --create > "$BACKUP_PATH"

# Check if backup was successful
if [ $? -eq 0 ] && [ -s "$BACKUP_PATH" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo -e "${GREEN}  File: $BACKUP_PATH${NC}"
    echo -e "${GREEN}  Size: $BACKUP_SIZE${NC}"
    
    # List recent backups
    echo -e "\n${YELLOW}Recent backups:${NC}"
    ls -lht "$BACKUP_DIR"/*.sql 2>/dev/null | head -5 || echo "No previous backups found."
    
    # Optional: Clean up old backups (keep last 10)
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        echo -e "\n${YELLOW}Cleaning up old backups (keeping last 10)...${NC}"
        ls -t "$BACKUP_DIR"/*.sql | tail -n +11 | xargs rm -f
        echo -e "${GREEN}✓ Old backups cleaned up${NC}"
    fi
    
else
    echo -e "${RED}✗ Backup failed!${NC}"
    rm -f "$BACKUP_PATH"  # Remove empty/failed backup file
    exit 1
fi

echo -e "\n${GREEN}Backup process completed!${NC}" 