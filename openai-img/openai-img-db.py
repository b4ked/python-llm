#!/usr/bin/env python3
"""
openai-img-db.py

Extract text content from images using OpenAI Vision API and store it in PostgreSQL database.

Usage:
    python openai-img-db.py /path/to/your/image.jpg
"""

import sys
import os
import pathlib
import base64
import mimetypes
import requests
from typing import Optional

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection

# ────────────────────────────────────────────────────────────────────────────────
#  Config
# ────────────────────────────────────────────────────────────────────────────────
OPENAI_API_URL = "https://api.openai.com/v1"
MODEL_VISION_IMG = "gpt-4o"  # Updated to use gpt-4o which supports vision

# ────────────────────────────────────────────────────────────────────────────────
#  Helper functions
# ────────────────────────────────────────────────────────────────────────────────
def _headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"}

def _load_image_as_data_url(path: str) -> str:
    """Convert image file to base64 data URL"""
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode()
    return f"data:{mime};base64,{b64}"

def _extract_text_from_image(img_path: str, api_key: str) -> str:
    """Extract text from image using OpenAI Vision API"""
    data_url = _load_image_as_data_url(img_path)
    payload = {
        "model": MODEL_VISION_IMG,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text",
                 "text": ("Please extract text from the attached image in the following format:\n\n"
                         "1. First line: A short, concise title (3-6 words) with only first letters of words capitalized that summarizes the image content\n"
                         "2. Second line: A blank line\n"
                         "3. Remaining content: The **complete** extracted text in its original formatting without omitting, summarizing or repeating any content. "
                         "Extract ALL text content from the image, ensuring nothing is truncated or omitted.\n\n"
                         "If the image contains no text, reply with 'Empty Image' followed by a blank line and 'No text content found.'")},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]
        }],
        "max_tokens": 4000
    }

    rsp = requests.post(f"{OPENAI_API_URL}/chat/completions",
                        headers=_headers(api_key),
                        json=payload, timeout=60)
    rsp.raise_for_status()
    
    # The response is already in the correct format with title\n\ntext
    return rsp.json()["choices"][0]["message"]["content"].strip()

# ────────────────────────────────────────────────────────────────────────────────
#  Database helper functions
# ────────────────────────────────────────────────────────────────────────────────
def get_document_by_id(doc_id):
    """Retrieve a document by its ID from the database"""
    db = DatabaseConnection()
    
    if db.connect():
        try:
            result = db.execute_query(
                "SELECT * FROM documents WHERE id = %s",
                (doc_id,)
            )
            return result[0] if result else None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
        finally:
            db.disconnect()
    return None

def get_documents_by_filename(filename):
    """Retrieve documents by filename from the database"""
    db = DatabaseConnection()
    
    if db.connect():
        try:
            result = db.execute_query(
                "SELECT * FROM documents WHERE filename = %s ORDER BY processed_at DESC",
                (filename,)
            )
            return result
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
        finally:
            db.disconnect()
    return []

def list_all_documents():
    """List all documents in the database"""
    db = DatabaseConnection()
    
    if db.connect():
        try:
            result = db.execute_query(
                "SELECT id, filename, file_size, file_type, processed_at FROM documents ORDER BY processed_at DESC"
            )
            return result
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []
        finally:
            db.disconnect()
    return []

def store_document_in_db(filename, content, file_size, file_type="image"):
    """Store document information in the PostgreSQL database"""
    db = DatabaseConnection()
    
    if db.connect():
        try:
            # Insert document information and get the ID
            db.cursor.execute(
                """INSERT INTO documents (filename, content, file_size, file_type) 
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (filename, content, file_size, file_type)
            )
            
            # Fetch the returned ID
            result = db.cursor.fetchone()
            if result:
                db.connection.commit()
                doc_id = result['id']
                print(f"✓ Document '{filename}' stored successfully in database with ID: {doc_id}")
                return doc_id
            else:
                db.connection.rollback()
                print(f"✗ Failed to store document '{filename}' in database")
                return False
                
        except Exception as e:
            print(f"✗ Error storing document in database: {e}")
            db.connection.rollback()
            return False
        finally:
            db.disconnect()
    else:
        print("✗ Failed to connect to database")
        return False

# ────────────────────────────────────────────────────────────────────────────────
#  Main processing function
# ────────────────────────────────────────────────────────────────────────────────
def extract_text_from_image(file_path: str, api_key: Optional[str] = None) -> str:
    """
    Given an image file, return extracted text in the format:
        <title line>
        
        <full text>
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")

    p = pathlib.Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(file_path)

    # Check if it's a supported image format
    supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    ext = p.suffix.lower()
    if ext not in supported_extensions:
        raise ValueError(f"Unsupported image format: {ext}. Supported formats: {', '.join(supported_extensions)}")

    return _extract_text_from_image(str(p), api_key)

# ────────────────────────────────────────────────────────────────────────────────
#  Main script execution
# ────────────────────────────────────────────────────────────────────────────────
def main():
    # 1️⃣ Validate input arguments
    if len(sys.argv) != 2:
        print("Usage: python openai-img-db.py /path/to/your/image.jpg")
        print("Supported formats: jpg, jpeg, png, gif, bmp, webp, tiff, tif")
        sys.exit(1)

    img_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    if not img_path.is_file():
        sys.exit(f"File not found: {img_path}")

    # Check if OPENAI_API_KEY is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("Error: OPENAI_API_KEY environment variable not set")

    # 2️⃣ Extract text from image
    print(f"⇢ Processing image: {img_path.name}")
    try:
        extracted_text = extract_text_from_image(str(img_path), api_key)
        print("✓ Text extraction completed successfully")
    except Exception as e:
        sys.exit(f"✗ Error extracting text from image: {e}")

    # 3️⃣ Store in database
    print("⇢ Storing extracted text in database …")
    file_size = img_path.stat().st_size
    filename = img_path.name

    # Check if document already exists
    existing_docs = get_documents_by_filename(filename)
    if existing_docs:
        print(f"⚠ Warning: Document '{filename}' already exists in database ({len(existing_docs)} entries)")
        print("  Proceeding to add new entry...")

    # Store the document in the database
    document_id = store_document_in_db(filename, extracted_text, file_size, "image")

    if document_id:
        print(f"✓ Image text extraction and database storage completed successfully!")
        print(f"  - File: {filename}")
        print(f"  - Size: {file_size} bytes")
        print(f"  - Document ID: {document_id}")
        print(f"  - Extracted text length: {len(extracted_text)} characters")
        
        # Show a preview of the extracted text
        if extracted_text:
            lines = extracted_text.split('\n')
            if len(lines) > 0:
                print(f"  - Title: {lines[0]}")
            if len(extracted_text) > 200:
                print(f"  - Preview: {extracted_text[:200]}...")
            else:
                print(f"  - Content: {extracted_text}")
    else:
        sys.exit("✗ Failed to store document in database")

# ────────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main() 