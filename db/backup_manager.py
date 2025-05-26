#!/usr/bin/env python3
"""
PostgreSQL Database Backup Manager
A Python script to manage database backups programmatically
"""

import os
import subprocess
import datetime
import glob
import sys
from pathlib import Path

class DatabaseBackupManager:
    def __init__(self):
        self.container_name = "python-llm-postgres"
        self.db_name = "python_llm_db"
        self.db_user = "postgres"
        self.backup_dir = Path("./backup")
        self.backup_dir.mkdir(exist_ok=True)
    
    def is_container_running(self):
        """Check if the PostgreSQL container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True, text=True, check=True
            )
            return self.container_name in result.stdout
        except subprocess.CalledProcessError:
            return False
    
    def create_backup(self):
        """Create a new database backup"""
        if not self.is_container_running():
            print(f"❌ Error: Container '{self.container_name}' is not running")
            print("Start it with: docker-compose up -d")
            return False
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"postgres_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_file
        
        print(f"🔄 Creating backup: {backup_file}")
        
        try:
            # Create backup using pg_dump
            with open(backup_path, 'w') as f:
                subprocess.run([
                    "docker", "exec", self.container_name,
                    "pg_dump", "-U", self.db_user, "-d", self.db_name,
                    "--verbose", "--clean", "--if-exists", "--create"
                ], stdout=f, stderr=subprocess.PIPE, check=True)
            
            # Verify backup was created and has content
            if backup_path.exists() and backup_path.stat().st_size > 0:
                size = self._format_size(backup_path.stat().st_size)
                print(f"✅ Backup created successfully!")
                print(f"   File: {backup_path}")
                print(f"   Size: {size}")
                
                self._cleanup_old_backups()
                self._list_recent_backups()
                return True
            else:
                print("❌ Backup failed - file is empty or wasn't created")
                backup_path.unlink(missing_ok=True)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Backup failed: {e}")
            backup_path.unlink(missing_ok=True)
            return False
    
    def list_backups(self):
        """List all available backups"""
        backup_files = sorted(
            self.backup_dir.glob("*.sql"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not backup_files:
            print("📁 No backup files found")
            return []
        
        print("📋 Available backups:")
        for i, backup_file in enumerate(backup_files, 1):
            size = self._format_size(backup_file.stat().st_size)
            mtime = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
            print(f"   {i:2d}. {backup_file.name} ({size}) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return backup_files
    
    def restore_backup(self, backup_file=None):
        """Restore database from backup"""
        if not self.is_container_running():
            print(f"❌ Error: Container '{self.container_name}' is not running")
            return False
        
        if backup_file is None or backup_file == "latest":
            backup_files = self.list_backups()
            if not backup_files:
                return False
            backup_path = backup_files[0]
        else:
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                print(f"❌ Backup file not found: {backup_path}")
                self.list_backups()
                return False
        
        print(f"\n⚠️  WARNING: This will completely replace the current database!")
        print(f"📁 Backup file: {backup_path.name}")
        print(f"📊 File size: {self._format_size(backup_path.stat().st_size)}")
        
        confirm = input("\nAre you sure you want to continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("🚫 Restore cancelled")
            return False
        
        try:
            print("🔄 Starting database restore...")
            
            # Terminate active connections
            subprocess.run([
                "docker", "exec", self.container_name,
                "psql", "-U", self.db_user, "-d", "postgres", "-c",
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{self.db_name}' AND pid <> pg_backend_pid();"
            ], capture_output=True)
            
            # Restore database
            with open(backup_path, 'r') as f:
                subprocess.run([
                    "docker", "exec", "-i", self.container_name,
                    "psql", "-U", self.db_user, "-d", "postgres"
                ], stdin=f, check=True)
            
            print("✅ Database restored successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def _cleanup_old_backups(self, keep=10):
        """Remove old backup files, keeping only the most recent ones"""
        backup_files = sorted(
            self.backup_dir.glob("*.sql"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(backup_files) > keep:
            old_files = backup_files[keep:]
            print(f"🧹 Cleaning up {len(old_files)} old backup(s)")
            for old_file in old_files:
                old_file.unlink()
    
    def _list_recent_backups(self, count=5):
        """List recent backups"""
        backup_files = sorted(
            self.backup_dir.glob("*.sql"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:count]
        
        if backup_files:
            print(f"\n📋 Recent backups:")
            for backup_file in backup_files:
                size = self._format_size(backup_file.stat().st_size)
                mtime = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                print(f"   • {backup_file.name} ({size}) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"


def main():
    """Main function to handle command line arguments"""
    manager = DatabaseBackupManager()
    
    if len(sys.argv) == 1:
        print("🗄️  PostgreSQL Database Backup Manager")
        print("=====================================")
        print("\nUsage:")
        print("  python backup_manager.py backup          # Create new backup")
        print("  python backup_manager.py list            # List all backups")
        print("  python backup_manager.py restore         # Restore latest backup")
        print("  python backup_manager.py restore <file>  # Restore specific backup")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        success = manager.create_backup()
        sys.exit(0 if success else 1)
    
    elif command == "list":
        manager.list_backups()
    
    elif command == "restore":
        backup_file = sys.argv[2] if len(sys.argv) > 2 else "latest"
        success = manager.restore_backup(backup_file)
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: backup, list, restore")
        sys.exit(1)


if __name__ == "__main__":
    main() 