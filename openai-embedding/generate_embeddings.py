#!/usr/bin/env python3
"""
Generate OpenAI embeddings for all documents in the PostgreSQL database.
This script reads documents from the documents table and creates embeddings
in the embeddings table, avoiding duplicates.
"""

import os
import sys
import openai
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
import json
from typing import List, Optional

# Add the db directory to the path so we can import config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db'))
from config import DB_CONFIG

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# OpenAI embedding model
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536  # text-embedding-3-small has 1536 dimensions

class EmbeddingGenerator:
    """Class to handle embedding generation and database operations"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect_to_database(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            # Register pgvector types
            register_vector(self.connection)
            print("✓ Successfully connected to PostgreSQL database with pgvector support")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def disconnect_from_database(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✓ Database connection closed")
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a given text using OpenAI API"""
        try:
            response = openai.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"✗ Error generating embedding: {e}")
            return None
    
    def get_all_documents(self) -> List[dict]:
        """Retrieve all documents from the documents table"""
        try:
            query = """
                SELECT id, filename, content, processed_at, file_size, file_type
                FROM documents
                WHERE content IS NOT NULL AND content != ''
                ORDER BY id
            """
            self.cursor.execute(query)
            documents = self.cursor.fetchall()
            print(f"✓ Found {len(documents)} documents with content")
            return documents
        except Exception as e:
            print(f"✗ Error retrieving documents: {e}")
            return []
    
    def check_embedding_exists(self, document_id: int, chunk_index: int = 0) -> bool:
        """Check if an embedding already exists for a document"""
        try:
            query = """
                SELECT id FROM embeddings 
                WHERE document_id = %s AND chunk_index = %s
            """
            self.cursor.execute(query, (document_id, chunk_index))
            result = self.cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"✗ Error checking existing embedding: {e}")
            return False
    
    def insert_embedding(self, document_id: int, content: str, embedding: List[float], 
                        chunk_index: int = 0, metadata: dict = None) -> bool:
        """Insert an embedding into the embeddings table"""
        try:
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
            self.cursor.execute(query, (document_id, content, embedding, chunk_index, metadata_json))
            self.connection.commit()
            embedding_id = self.cursor.fetchone()['id']
            return True
        except Exception as e:
            print(f"✗ Error inserting embedding: {e}")
            self.connection.rollback()
            return False
    
    def process_documents(self):
        """Main function to process all documents and generate embeddings"""
        print("🚀 Starting embedding generation process...")
        
        # Get all documents
        documents = self.get_all_documents()
        if not documents:
            print("No documents found to process")
            return
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for doc in documents:
            document_id = doc['id']
            filename = doc['filename']
            content = doc['content']
            
            print(f"\n📄 Processing document {document_id}: {filename}")
            
            # Check if embedding already exists
            if self.check_embedding_exists(document_id):
                print(f"   ⏭️  Embedding already exists, skipping...")
                skipped_count += 1
                continue
            
            # Generate embedding
            print(f"   🔄 Generating embedding...")
            embedding = self.get_embedding(content)
            
            if embedding is None:
                print(f"   ✗ Failed to generate embedding")
                error_count += 1
                continue
            
            # Prepare metadata
            metadata = {
                "filename": filename,
                "file_type": doc.get('file_type'),
                "file_size": doc.get('file_size'),
                "processed_at": doc.get('processed_at').isoformat() if doc.get('processed_at') else None,
                "content_length": len(content),
                "embedding_model": EMBEDDING_MODEL
            }
            
            # Insert embedding
            if self.insert_embedding(document_id, content, embedding, metadata=metadata):
                print(f"   ✓ Embedding stored successfully")
                processed_count += 1
            else:
                print(f"   ✗ Failed to store embedding")
                error_count += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"EMBEDDING GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total documents found: {len(documents)}")
        print(f"Embeddings created: {processed_count}")
        print(f"Documents skipped (already exist): {skipped_count}")
        print(f"Errors encountered: {error_count}")
        print(f"{'='*60}")
        
        if processed_count > 0:
            print(f"✓ Successfully generated {processed_count} new embeddings!")
        if skipped_count > 0:
            print(f"ℹ️  Skipped {skipped_count} documents that already had embeddings")
        if error_count > 0:
            print(f"⚠️  {error_count} documents failed to process")


def main():
    """Main function"""
    print("OpenAI Embedding Generator for PostgreSQL Documents")
    print("=" * 60)
    
    # Validate OpenAI API key
    if not openai.api_key:
        print("✗ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return 1
    
    # Initialize embedding generator
    generator = EmbeddingGenerator()
    
    try:
        # Connect to database
        if not generator.connect_to_database():
            return 1
        
        # Process documents
        generator.process_documents()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    finally:
        # Always disconnect from database
        generator.disconnect_from_database()
    
    return 0


if __name__ == "__main__":
    exit(main()) 