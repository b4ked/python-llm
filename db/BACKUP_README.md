# PostgreSQL Database Backup & Restore

This directory contains scripts to backup and restore your PostgreSQL database with pgvector extension.

## 📁 Directory Structure

```
db/
├── backup/                    # Backup files (auto-created, git-ignored)
├── backup_database.sh         # Backup script
├── restore_database.sh        # Restore script
├── docker-compose.yml         # Database container configuration
└── BACKUP_README.md          # This file
```

## 🔄 Creating Backups

### Automatic Backup
```bash
cd db
./backup_database.sh
```

This will:
- ✅ Check if the PostgreSQL container is running
- ✅ Create a timestamped backup file in `./backup/`
- ✅ Include all data, schema, and pgvector extensions
- ✅ Automatically clean up old backups (keeps last 10)
- ✅ Show backup size and recent backup list

### Backup File Format
Backups are named: `postgres_backup_YYYYMMDD_HHMMSS.sql`

Example: `postgres_backup_20241201_143022.sql`

## 🔙 Restoring from Backup

### Restore Latest Backup
```bash
cd db
./restore_database.sh latest
```

### Restore Specific Backup
```bash
cd db
./restore_database.sh postgres_backup_20241201_143022.sql
```

### List Available Backups
```bash
cd db
./restore_database.sh
```

## ⚠️ Important Notes

### Before Restoring
- **WARNING**: Restore completely replaces your current database
- All current data will be lost
- The script will ask for confirmation before proceeding
- Make sure to backup current data if needed

### Prerequisites
- Docker container must be running: `docker-compose up -d`
- Container name: `python-llm-postgres`
- Database name: `python_llm_db`

### What's Included in Backups
- ✅ All database schemas
- ✅ All table data
- ✅ All indexes and constraints
- ✅ pgvector extension configuration
- ✅ User-defined functions and procedures

## 🛠️ Troubleshooting

### Container Not Running
```bash
cd db
docker-compose up -d
```

### Permission Issues
```bash
chmod +x backup_database.sh restore_database.sh
```

### Check Container Status
```bash
docker ps | grep python-llm-postgres
```

### View Container Logs
```bash
docker logs python-llm-postgres
```

## 📋 Backup Best Practices

1. **Regular Backups**: Run backups before major changes
2. **Test Restores**: Periodically test restore process
3. **Monitor Space**: Check backup directory size regularly
4. **External Storage**: Consider copying backups to external storage
5. **Automation**: Add to cron for automatic daily backups

### Example Cron Job (Daily at 2 AM)
```bash
# Add to crontab with: crontab -e
0 2 * * * cd /path/to/your/project/db && ./backup_database.sh >> backup.log 2>&1
```

## 🔐 Security Notes

- Backup files contain sensitive data
- Backup directory is git-ignored for security
- Store backups securely if copying elsewhere
- Consider encryption for sensitive environments

## 📊 Monitoring Backup Health

The backup script automatically:
- Verifies backup file creation
- Checks backup file size
- Lists recent backups
- Cleans up old backups (keeps 10 most recent)

## 🆘 Emergency Recovery

If your Docker container is completely lost:

1. Recreate the container:
   ```bash
   cd db
   docker-compose down
   docker-compose up -d
   ```

2. Wait for container to be ready:
   ```bash
   docker logs -f python-llm-postgres
   ```

3. Restore from backup:
   ```bash
   ./restore_database.sh latest
   ```

## 📞 Support

If you encounter issues:
1. Check container is running: `docker ps`
2. Check container logs: `docker logs python-llm-postgres`
3. Verify backup file exists and isn't empty
4. Ensure proper permissions on script files 