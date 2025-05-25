"""
Example script showing how to use the PostgreSQL database from the openai-pdf folder
"""

import sys
import os
from datetime import datetime

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection


def store_document_info(filename, content, file_size, file_type):
    """Store document information in the database"""
    db = DatabaseConnection()
    
    if db.connect():
        # Insert document information
        success = db.execute_command(
            """INSERT INTO documents (filename, content, file_size, file_type) 
               VALUES (%s, %s, %s, %s)""",
            (filename, content, file_size, file_type)
        )
        
        if success:
            print(f"Document '{filename}' stored successfully in database")
        else:
            print(f"Failed to store document '{filename}'")
        
        db.disconnect()
        return success
    
    return False


def get_all_documents():
    """Retrieve all documents from the database"""
    db = DatabaseConnection()
    
    if db.connect():
        documents = db.execute_query("SELECT * FROM documents ORDER BY processed_at DESC")
        db.disconnect()
        return documents
    
    return []


def get_documents_by_type(file_type):
    """Retrieve documents by file type"""
    db = DatabaseConnection()
    
    if db.connect():
        documents = db.execute_query(
            "SELECT * FROM documents WHERE file_type = %s ORDER BY processed_at DESC",
            (file_type,)
        )
        db.disconnect()
        return documents
    
    return []


def main():
    """Example usage of database functions"""
    print("=== Database Example from openai-pdf folder ===\n")
    
    # Example 1: Store a document
    print("1. Storing a sample document...")
    store_document_info(
        filename="sample.pdf",
        content="This is sample PDF content extracted by OpenAI",
        file_size=1024,
        file_type="pdf"
    )
    
    # Example 2: Get all documents
    print("\n2. Retrieving all documents...")
    all_docs = get_all_documents()
    for doc in all_docs:
        print(f"  - {doc['filename']} ({doc['file_type']}) - {doc['processed_at']}")
    
    # Example 3: Get PDF documents only
    print("\n3. Retrieving PDF documents only...")
    pdf_docs = get_documents_by_type("pdf")
    for doc in pdf_docs:
        print(f"  - {doc['filename']} - Size: {doc['file_size']} bytes")
    
    # Example 4: Check users table
    print("\n4. Checking users in database...")
    db = DatabaseConnection()
    if db.connect():
        users = db.execute_query("SELECT * FROM users")
        for user in users:
            print(f"  - {user['username']} ({user['email']})")
        db.disconnect()


if __name__ == "__main__":
    main() 