#!/usr/bin/env python3
"""
Debug script to help diagnose embedding search issues
"""

import os
import sys
import openai
from dotenv import load_dotenv

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db'))
from database import DatabaseConnection

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

EMBEDDING_MODEL = "text-embedding-3-small"

def get_embedding(text: str):
    """Generate embedding for a given text using OpenAI API"""
    try:
        response = openai.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return None

def debug_embeddings_content():
    """Check what content is actually in the embeddings table"""
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Get basic stats
        result = db.execute_query("SELECT COUNT(*) as count FROM embeddings")
        total_embeddings = result[0]['count'] if result else 0
        print(f"📊 Total embeddings in database: {total_embeddings}")
        
        if total_embeddings == 0:
            print("❌ No embeddings found! You need to run generate_embeddings.py first")
            return
        
        # Get sample content
        print("\n📄 Sample embedding content:")
        sample_results = db.execute_query("""
            SELECT document_id, content_chunk, metadata 
            FROM embeddings 
            ORDER BY id 
            LIMIT 5
        """)
        
        for i, row in enumerate(sample_results, 1):
            content_preview = row['content_chunk'][:200] + "..." if len(row['content_chunk']) > 200 else row['content_chunk']
            print(f"\n{i}. Document ID: {row['document_id']}")
            print(f"   Content: {content_preview}")
            
            # Parse metadata if it's JSON
            metadata = row.get('metadata', {})
            if isinstance(metadata, str):
                import json
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            if metadata.get('filename'):
                print(f"   Filename: {metadata['filename']}")
        
        # Get unique document IDs
        doc_results = db.execute_query("""
            SELECT DISTINCT document_id, COUNT(*) as chunk_count
            FROM embeddings 
            GROUP BY document_id 
            ORDER BY document_id
        """)
        
        print(f"\n📁 Documents with embeddings:")
        for row in doc_results:
            print(f"   Document ID {row['document_id']}: {row['chunk_count']} chunks")
            
    finally:
        db.disconnect()

def test_similarity_search(query: str, thresholds: list = [0.1, 0.3, 0.5, 0.7, 0.9]):
    """Test similarity search with different thresholds"""
    print(f"\n🔍 Testing similarity search for: '{query}'")
    print("="*60)
    
    # Generate embedding for query
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        for threshold in thresholds:
            print(f"\n📊 Threshold: {threshold}")
            results = db.find_similar_embeddings(
                query_embedding, 
                similarity_threshold=threshold, 
                max_results=3
            )
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    similarity = result.get('similarity', 0)
                    content_preview = result['content_chunk'][:100] + "..." if len(result['content_chunk']) > 100 else result['content_chunk']
                    print(f"   {i}. Similarity: {similarity:.3f} - {content_preview}")
            else:
                print(f"   📭 No results found")
                
    finally:
        db.disconnect()

def test_raw_similarity():
    """Test raw similarity without threshold to see all results"""
    query = input("\nEnter a test query: ").strip()
    if not query:
        query = "diabetes"
    
    print(f"\n🔍 Testing raw similarity for: '{query}'")
    print("="*60)
    
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("❌ Failed to generate query embedding")
        return
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Get top 10 most similar without threshold
        query = """
            SELECT 
                e.document_id,
                e.content_chunk,
                1 - (e.embedding <=> %s::vector) as similarity,
                e.metadata
            FROM embeddings e
            ORDER BY e.embedding <=> %s::vector
            LIMIT 10
        """
        db.cursor.execute(query, (query_embedding, query_embedding))
        results = db.cursor.fetchall()
        
        if results:
            print(f"✅ Top {len(results)} most similar results (no threshold):")
            for i, result in enumerate(results, 1):
                similarity = result['similarity']
                content_preview = result['content_chunk'][:150] + "..." if len(result['content_chunk']) > 150 else result['content_chunk']
                
                # Parse metadata
                metadata = result.get('metadata', {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                filename = metadata.get('filename', f'Doc {result["document_id"]}')
                
                print(f"\n{i}. Similarity: {similarity:.4f}")
                print(f"   File: {filename}")
                print(f"   Content: {content_preview}")
        else:
            print("❌ No results found at all - this indicates a serious issue")
            
    except Exception as e:
        print(f"❌ Error in raw similarity test: {e}")
    finally:
        db.disconnect()

def main():
    """Main debug function"""
    print("🔧 Embedding Search Debug Tool")
    print("="*60)
    
    # Check database content
    debug_embeddings_content()
    
    # Test with common queries
    test_queries = ["diabetes", "colonoscopy", "medical", "health", "report"]
    
    for query in test_queries:
        test_similarity_search(query)
    
    # Interactive raw similarity test
    test_raw_similarity()
    
    print("\n💡 Recommendations:")
    print("1. If no embeddings found: Run generate_embeddings.py first")
    print("2. If low similarity scores: Try lowering the threshold to 0.3 or 0.5")
    print("3. If content doesn't match: Check if your documents contain the expected content")
    print("4. If still no results: There might be an issue with the embedding model or database")

if __name__ == "__main__":
    main() 