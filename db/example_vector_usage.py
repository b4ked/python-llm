#!/usr/bin/env python3
"""
Example script demonstrating how to use vector embeddings with the database.
This shows how you would typically use the database from other directories in the project.
"""

import sys
import os
import numpy as np

# Add the db directory to the path (this is how you'd import from other directories)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseConnection


def create_sample_document():
    """Create a sample document for testing embeddings"""
    db = DatabaseConnection()
    if not db.connect():
        return None
    
    # Insert a sample document
    success = db.execute_command(
        """INSERT INTO documents (filename, content, file_size, file_type) 
           VALUES (%s, %s, %s, %s) 
           ON CONFLICT DO NOTHING 
           RETURNING id""",
        ("sample_document.txt", "This is a sample document for testing vector embeddings.", 100, "text")
    )
    
    if success:
        # Get the document ID
        result = db.execute_query("SELECT id FROM documents WHERE filename = %s", ("sample_document.txt",))
        if result:
            doc_id = result[0]['id']
            db.disconnect()
            return doc_id
    
    db.disconnect()
    return None


def simulate_embedding_generation(text):
    """
    Simulate generating embeddings for text.
    In a real application, you would use OpenAI's API or another embedding service.
    """
    # This creates a random 1536-dimensional vector (OpenAI ada-002 size)
    # In practice, you would call something like:
    # response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    # return response['data'][0]['embedding']
    
    np.random.seed(hash(text) % 2**32)  # Deterministic "embedding" based on text
    return np.random.rand(1536)


def example_embedding_workflow():
    """Demonstrate a complete embedding workflow"""
    print("=== Vector Embedding Example ===\n")
    
    # Step 1: Ensure we have a document
    doc_id = create_sample_document()
    if not doc_id:
        print("Failed to create sample document")
        return
    
    print(f"Using document ID: {doc_id}")
    
    # Step 2: Connect to database
    db = DatabaseConnection()
    if not db.connect():
        print("Failed to connect to database")
        return
    
    # Step 3: Prepare some text chunks and their embeddings
    text_chunks = [
        "This is the first chunk of text from our document.",
        "Here is another piece of content that we want to embed.",
        "Vector embeddings allow us to find semantically similar content.",
        "Machine learning models can understand text through embeddings."
    ]
    
    print("Inserting embeddings for text chunks...")
    
    # Step 4: Insert embeddings for each chunk
    embedding_ids = []
    for i, chunk in enumerate(text_chunks):
        embedding = simulate_embedding_generation(chunk)
        
        embedding_id = db.insert_embedding(
            document_id=doc_id,
            content_chunk=chunk,
            embedding=embedding,
            chunk_index=i,
            metadata={"chunk_length": len(chunk), "example": True}
        )
        
        if embedding_id:
            embedding_ids.append(embedding_id)
            print(f"  ✓ Inserted embedding {embedding_id} for chunk {i}")
        else:
            print(f"  ✗ Failed to insert embedding for chunk {i}")
    
    print(f"\nInserted {len(embedding_ids)} embeddings successfully")
    
    # Step 5: Demonstrate similarity search
    print("\n=== Similarity Search Example ===")
    
    # Create a query embedding
    query_text = "Find content about machine learning and embeddings"
    query_embedding = simulate_embedding_generation(query_text)
    
    print(f"Searching for content similar to: '{query_text}'")
    
    # Find similar embeddings
    similar_results = db.find_similar_embeddings(
        query_embedding=query_embedding,
        similarity_threshold=0.0,  # Low threshold to see all results
        max_results=5
    )
    
    if similar_results:
        print(f"\nFound {len(similar_results)} similar embeddings:")
        for result in similar_results:
            print(f"  Similarity: {result['similarity']:.3f}")
            print(f"  Content: {result['content_chunk']}")
            print(f"  Metadata: {result['metadata']}")
            print()
    else:
        print("No similar embeddings found")
    
    # Step 6: Get all embeddings for the document
    print("=== All Embeddings for Document ===")
    all_embeddings = db.get_embeddings_by_document(doc_id)
    
    if all_embeddings:
        print(f"Document {doc_id} has {len(all_embeddings)} embeddings:")
        for emb in all_embeddings:
            print(f"  Chunk {emb['chunk_index']}: {emb['content_chunk'][:50]}...")
    
    db.disconnect()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    example_embedding_workflow() 