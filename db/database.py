"""
Database utility functions for PostgreSQL operations with pgvector support
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os
import numpy as np
from pgvector.psycopg2 import register_vector

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
            # Register pgvector types
            register_vector(self.connection)
            print("Successfully connected to PostgreSQL database with pgvector support")
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
    
    def insert_embedding(self, document_id, content_chunk, embedding, chunk_index, metadata=None):
        """Insert a vector embedding into the embeddings table"""
        try:
            # Convert numpy array to list if needed
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            import json
            metadata_json = json.dumps(metadata or {})
            
            query = """
                INSERT INTO embeddings (document_id, content_chunk, embedding, chunk_index, metadata)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (document_id, chunk_index) 
                DO UPDATE SET 
                    content_chunk = EXCLUDED.content_chunk,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = CURRENT_TIMESTAMP
                RETURNING id
            """
            self.cursor.execute(query, (document_id, content_chunk, embedding, chunk_index, metadata_json))
            self.connection.commit()
            return self.cursor.fetchone()['id']
        except Exception as e:
            print(f"Error inserting embedding: {e}")
            self.connection.rollback()
            return None
    
    def find_similar_embeddings(self, query_embedding, similarity_threshold=0.8, max_results=10):
        """Find similar embeddings using cosine similarity"""
        try:
            # Convert numpy array to list if needed
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Use direct SQL with proper vector casting
            query = """
                SELECT 
                    e.id,
                    e.document_id,
                    e.content_chunk,
                    1 - (e.embedding <=> %s::vector) as similarity,
                    e.metadata
                FROM embeddings e
                WHERE 1 - (e.embedding <=> %s::vector) >= %s
                ORDER BY e.embedding <=> %s::vector
                LIMIT %s
            """
            self.cursor.execute(query, (query_embedding, query_embedding, similarity_threshold, query_embedding, max_results))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error finding similar embeddings: {e}")
            return None
    
    def get_embeddings_by_document(self, document_id):
        """Get all embeddings for a specific document"""
        try:
            query = """
                SELECT id, content_chunk, embedding, chunk_index, metadata, created_at
                FROM embeddings 
                WHERE document_id = %s 
                ORDER BY chunk_index
            """
            self.cursor.execute(query, (document_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting embeddings for document: {e}")
            return None


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
    """Test the database connection and vector functionality"""
    db = DatabaseConnection()
    if db.connect():
        # Test basic query
        users = db.execute_query("SELECT * FROM users")
        print("Users in database:", users)
        
        # Test insert
        success = db.execute_command(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
            ("test_user", "test@example.com")
        )
        if success:
            print("Test user inserted successfully")
        
        # Test vector functionality
        try:
            # Check if pgvector extension is available
            result = db.execute_query("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if result:
                print("pgvector extension is installed and available")
                
                # Test with a sample embedding (1536 dimensions for OpenAI ada-002)
                sample_embedding = np.random.rand(1536).tolist()
                
                # First, ensure we have a document to reference
                doc_result = db.execute_query("SELECT id FROM documents LIMIT 1")
                if doc_result:
                    doc_id = doc_result[0]['id']
                    
                    # Test embedding insertion
                    embedding_id = db.insert_embedding(
                        document_id=doc_id,
                        content_chunk="This is a test chunk of text for embedding",
                        embedding=sample_embedding,
                        chunk_index=0,
                        metadata={"test": True, "source": "test_function"}
                    )
                    
                    if embedding_id:
                        print(f"Test embedding inserted with ID: {embedding_id}")
                        
                        # Test similarity search
                        similar = db.find_similar_embeddings(sample_embedding, similarity_threshold=0.5, max_results=5)
                        if similar:
                            print(f"Found {len(similar)} similar embeddings")
                        else:
                            print("No similar embeddings found")
                    else:
                        print("Failed to insert test embedding")
                else:
                    print("No documents found - skipping embedding test")
            else:
                print("pgvector extension not found")
        except Exception as e:
            print(f"Error testing vector functionality: {e}")
        
        db.disconnect()
        return True
    return False


if __name__ == "__main__":
    test_connection() 