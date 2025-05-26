#!/usr/bin/env python3
"""
Update the embeddings table schema to support text-embedding-3-large with HNSW indexing for users who want higher quality embeddings.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add the db directory to the path so we can import config
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db'))
from config import DB_CONFIG

# Load environment variables
load_dotenv()

def update_embedding_schema():
    """Update the embeddings table to support 3072-dimension vectors with HNSW indexing"""
    
    connection = None
    cursor = None
    
    try:
        # Connect to database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print("✓ Connected to PostgreSQL database")
        
        # Check current schema
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'embeddings' AND column_name = 'embedding'
        """)
        
        current_schema = cursor.fetchone()
        if current_schema:
            print(f"Current embedding column: {current_schema}")
        
        # Check if we have any existing embeddings
        cursor.execute("SELECT COUNT(*) as count FROM embeddings")
        embedding_count = cursor.fetchone()['count']
        
        if embedding_count > 0:
            print(f"⚠️  Warning: Found {embedding_count} existing embeddings in the table")
            print("   These will need to be regenerated with the new model")
            
            response = input("Do you want to proceed and clear existing embeddings? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled")
                return False
            
            # Clear existing embeddings
            cursor.execute("DELETE FROM embeddings")
            print(f"✓ Cleared {embedding_count} existing embeddings")
        
        # Update the embedding column to support 3072 dimensions
        print("🔄 Updating embedding column to support 3072 dimensions...")
        
        cursor.execute("""
            ALTER TABLE embeddings 
            ALTER COLUMN embedding TYPE vector(3072)
        """)
        
        # Recreate the index using HNSW (supports higher dimensions than ivfflat)
        cursor.execute("DROP INDEX IF EXISTS embeddings_embedding_idx")
        print("🔄 Creating HNSW index (supports high-dimensional vectors)...")
        cursor.execute("""
            CREATE INDEX embeddings_embedding_idx ON embeddings 
            USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)
        """)
        
        # Commit changes
        connection.commit()
        
        print("✓ Successfully updated embeddings table schema")
        print("✓ Updated embedding column to vector(3072)")
        print("✓ Created HNSW vector similarity index")
        print("ℹ️  HNSW index provides excellent performance for high-dimensional vectors")
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating schema: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("✓ Database connection closed")


def main():
    """Main function"""
    print("Embedding Schema Updater for text-embedding-3-large")
    print("=" * 60)
    print("This script will update the embeddings table to support")
    print("3072-dimension vectors from OpenAI's text-embedding-3-large model")
    print("using HNSW indexing for optimal performance with high dimensions")
    print("=" * 60)
    
    success = update_embedding_schema()
    
    if success:
        print("\n✅ Schema update completed successfully!")
        print("You can now run generate_embeddings.py to create embeddings")
        print("with the text-embedding-3-large model.")
        print("\nNote: Remember to update EMBEDDING_MODEL in generate_embeddings.py")
        print("to 'text-embedding-3-large' and EMBEDDING_DIMENSION to 3072")
        return 0
    else:
        print("\n❌ Schema update failed!")
        return 1


if __name__ == "__main__":
    exit(main()) 