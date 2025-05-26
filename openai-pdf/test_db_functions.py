#!/usr/bin/env python3
"""
test_db_functions.py

Test script to demonstrate the database helper functions for document management.
This script shows how to use the helper functions from openai-pdf-db.py

Usage:
    python test_db_functions.py
"""

import sys
import os

# Add the current directory to path to import the helper functions
sys.path.append(os.path.dirname(__file__))

# Import the helper functions from openai-pdf-db.py
# Since the filename has hyphens, we need to import it differently
import importlib.util
spec = importlib.util.spec_from_file_location("openai_pdf_db", "openai-pdf-db.py")
openai_pdf_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openai_pdf_db)

# Now we can use the functions
get_document_by_id = openai_pdf_db.get_document_by_id
get_documents_by_filename = openai_pdf_db.get_documents_by_filename
list_all_documents = openai_pdf_db.list_all_documents

def main():
    """Test the database helper functions"""
    print("=== Testing Database Helper Functions ===\n")
    
    # Test 1: List all documents
    print("1. Listing all documents in the database:")
    print("-" * 40)
    documents = list_all_documents()
    
    if documents:
        for doc in documents:
            print(f"  ID: {doc['id']}")
            print(f"  Filename: {doc['filename']}")
            print(f"  File Type: {doc['file_type']}")
            print(f"  File Size: {doc['file_size']:,} bytes")
            print(f"  Processed: {doc['processed_at']}")
            print()
    else:
        print("  No documents found in the database.")
        print("  Run openai-pdf-db.py with a PDF file first!")
        return
    
    # Test 2: Get a specific document by ID
    if documents:
        first_doc_id = documents[0]['id']
        print(f"2. Retrieving document with ID {first_doc_id}:")
        print("-" * 40)
        
        doc = get_document_by_id(first_doc_id)
        if doc:
            print(f"  Filename: {doc['filename']}")
            print(f"  Content length: {len(doc['content']):,} characters")
            print(f"  Content preview: {doc['content'][:200]}...")
            print()
        else:
            print(f"  Document with ID {first_doc_id} not found.")
    
    # Test 3: Search by filename
    if documents:
        filename = documents[0]['filename']
        print(f"3. Searching for documents with filename '{filename}':")
        print("-" * 40)
        
        matching_docs = get_documents_by_filename(filename)
        print(f"  Found {len(matching_docs)} document(s) with this filename:")
        
        for doc in matching_docs:
            print(f"    - ID: {doc['id']}, Processed: {doc['processed_at']}")
        print()
    
    print("=== Test completed ===")

if __name__ == "__main__":
    main() 