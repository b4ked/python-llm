#!/usr/bin/env python3
"""
Example script demonstrating semantic search using generated embeddings.
This script shows how to search for similar documents based on a text query.
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

# Use the same embedding model as the generation script
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
        print(f"✗ Error generating embedding: {e}")
        return None

def search_similar_documents(query: str, similarity_threshold: float = 0.7, max_results: int = 5):
    """Search for documents similar to the given query"""
    
    print(f"🔍 Searching for: '{query}'")
    print(f"   Similarity threshold: {similarity_threshold}")
    print(f"   Max results: {max_results}")
    print("-" * 60)
    
    # Generate embedding for the query
    print("🔄 Generating query embedding...")
    query_embedding = get_embedding(query)
    
    if query_embedding is None:
        print("✗ Failed to generate query embedding")
        return
    
    # Connect to database and search
    db = DatabaseConnection()
    if not db.connect():
        print("✗ Failed to connect to database")
        return
    
    try:
        # Find similar embeddings
        print("🔄 Searching for similar documents...")
        results = db.find_similar_embeddings(
            query_embedding, 
            similarity_threshold=similarity_threshold, 
            max_results=max_results
        )
        
        if not results:
            print("📭 No similar documents found")
            return
        
        print(f"✓ Found {len(results)} similar document(s)")
        print("=" * 60)
        
        # Display results
        for i, result in enumerate(results, 1):
            similarity = result['similarity']
            content_preview = result['content_chunk'][:200] + "..." if len(result['content_chunk']) > 200 else result['content_chunk']
            
            print(f"\n📄 Result {i}")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Similarity: {similarity:.3f}")
            print(f"   Content Preview: {content_preview}")
            
            # Show metadata if available
            if result.get('metadata'):
                metadata = result['metadata']
                if isinstance(metadata, dict):
                    if 'filename' in metadata:
                        print(f"   Filename: {metadata['filename']}")
                    if 'file_type' in metadata:
                        print(f"   File Type: {metadata['file_type']}")
                    if 'content_length' in metadata:
                        print(f"   Content Length: {metadata['content_length']} characters")
            
            print("-" * 40)
    
    finally:
        db.disconnect()

def interactive_search():
    """Interactive search mode"""
    print("🔍 Interactive Semantic Search")
    print("=" * 60)
    print("Enter search queries to find similar documents.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n🔍 Enter search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                print("Please enter a search query")
                continue
            
            # Optional: Ask for similarity threshold
            threshold_input = input("   Similarity threshold (0.0-1.0, default 0.7): ").strip()
            try:
                threshold = float(threshold_input) if threshold_input else 0.7
                threshold = max(0.0, min(1.0, threshold))  # Clamp between 0 and 1
            except ValueError:
                threshold = 0.7
                print(f"   Using default threshold: {threshold}")
            
            # Perform search
            search_similar_documents(query, similarity_threshold=threshold)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    """Main function"""
    print("Semantic Search Example")
    print("=" * 60)
    
    # Check if we have any embeddings in the database
    db = DatabaseConnection()
    if db.connect():
        try:
            result = db.execute_query("SELECT COUNT(*) as count FROM embeddings")
            if result and result[0]['count'] > 0:
                print(f"✓ Found {result[0]['count']} embeddings in database")
            else:
                print("⚠️  No embeddings found in database")
                print("   Run generate_embeddings.py first to create embeddings")
                return 1
        finally:
            db.disconnect()
    else:
        print("✗ Failed to connect to database")
        return 1
    
    # Example searches
    print("\n📋 Example Searches:")
    print("-" * 30)
    
    example_queries = [
        "machine learning algorithms",
        "data processing techniques", 
        "user interface design",
        "database optimization"
    ]
    
    for query in example_queries:
        print(f"\n🔍 Example: '{query}'")
        search_similar_documents(query, similarity_threshold=0.6, max_results=3)
    
    # Interactive mode
    print("\n" + "=" * 60)
    interactive_search()
    
    return 0

if __name__ == "__main__":
    exit(main()) 