"""
Database utility functions for PostgreSQL operations
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the db directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import DB_CONFIG, DATABASE_URL


class DatabaseConnection:
    """Database connection manager using psycopg2"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_command(self, command, params=None):
        """Execute INSERT, UPDATE, DELETE commands"""
        try:
            self.cursor.execute(command, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error executing command: {e}")
            self.connection.rollback()
            return False


class SQLAlchemyConnection:
    """Database connection manager using SQLAlchemy"""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def execute_query(self, query, params=None):
        """Execute a query using SQLAlchemy"""
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]


def test_connection():
    """Test the database connection"""
    db = DatabaseConnection()
    if db.connect():
        # Test query
        users = db.execute_query("SELECT * FROM users")
        print("Users in database:", users)
        
        # Test insert
        success = db.execute_command(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
            ("test_user", "test@example.com")
        )
        if success:
            print("Test user inserted successfully")
        
        db.disconnect()
        return True
    return False


if __name__ == "__main__":
    test_connection() 