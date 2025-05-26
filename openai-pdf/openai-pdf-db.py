#!/usr/bin/env python3
"""
openai-pdf-db.py

Extract PDF text content using OpenAI and store it in PostgreSQL database.

Usage:
    python openai-pdf-db.py /path/to/your/file.pdf
"""

import sys, time, os, pathlib, json
from openai import OpenAI
from openai.types.beta.assistant import Assistant

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection

# Helper functions for document management
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

# 1️⃣ Setup -------------------------------------------------------------------
if len(sys.argv) != 2 or not sys.argv[1].lower().endswith(".pdf"):
    sys.exit("Usage: python openai-pdf-db.py your_doc.pdf")

pdf_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
if not pdf_path.is_file():
    sys.exit(f"File not found: {pdf_path}")

client = OpenAI()                # requires OPENAI_API_KEY env var
model_name = "gpt-4o"      # adjust if your account uses a different slug

# 2️⃣ Upload the PDF ----------------------------------------------------------
print("⇢ Uploading PDF …")
with open(pdf_path, "rb") as fp:
    file_obj = client.files.create(file=fp, purpose="assistants")
file_id = file_obj.id

# 3️⃣ Create / reuse an Assistant -------------------------------------------
print("⇢ Ensuring Assistant exists …")
asst_name = "PDF-extractor-retrieval"
assistant: Assistant

# Try to find an existing one (keeps your quota tidy)
for a in client.beta.assistants.list(order="desc", limit=100).data:
    if a.name == asst_name and a.model == model_name:
        assistant = a
        print("using existing assistant")
        break
else:
    assistant = client.beta.assistants.create(
        name=asst_name,
        model=model_name,
        tools=[{"type": "file_search"}],
        description="Extracts full text from PDFs using file search/retrieval"
    )
    print("creating new assistant")

# 4️⃣ Start a thread + run -----------------------------------------------------
message = (
    "Please extract **all** textual content from the attached PDF document "
    "in the original order. Return the complete text verbatim without any "
    "summaries, analysis, or modifications. If the PDF is empty or contains "
    "no readable text, reply with an empty string. Do not add any commentary "
    "or explanations - just the raw text content."
)

print("⇢ Creating thread and run …")
thread = client.beta.threads.create(
    messages=[{
        "role": "user",
        "content": message,
        "attachments": [{"file_id": file_id, "tools": [{"type": "file_search"}]}]
    }]
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Extract and return only the complete raw text content from the PDF. No analysis or formatting changes."
)

# 5️⃣ Poll until done ---------------------------------------------------------
print("⇢ Waiting for file search to finish …")
while run.status not in {"completed", "failed", "cancelled", "expired"}:
    time.sleep(3)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"   status: {run.status} …")

if run.status != "completed":
    sys.exit(f"Run ended with status {run.status}")

# 6️⃣ Fetch the answer --------------------------------------------------------
msgs = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
assistant_reply = next(m for m in msgs if m.role == "assistant").content[0].text.value

# 7️⃣ Store in database -------------------------------------------------------
def store_document_in_db(filename, content, file_size, file_type="pdf"):
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

print("⇢ Storing extracted text in database …")
file_size = pdf_path.stat().st_size
filename = pdf_path.name

# Check if document already exists
existing_docs = get_documents_by_filename(filename)
if existing_docs:
    print(f"⚠ Warning: Document '{filename}' already exists in database ({len(existing_docs)} entries)")
    print("  Proceeding to add new entry...")

# Store the document in the database
document_id = store_document_in_db(filename, assistant_reply, file_size)

if document_id:
    print(f"✓ PDF text extraction and database storage completed successfully!")
    print(f"  - File: {filename}")
    print(f"  - Size: {file_size} bytes")
    print(f"  - Text length: {len(assistant_reply)} characters")
    if isinstance(document_id, int):
        print(f"  - Database ID: {document_id}")
else:
    print("✗ Failed to store document in database")
    # Fallback: save to text file as well
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text(assistant_reply, encoding="utf-8")
    print(f"✓ Extracted text saved to {txt_path} as fallback")

# 8️⃣ Optional: Also save to text file ---------------------------------------
# Uncomment the lines below if you also want to save the text to a file
# txt_path = pdf_path.with_suffix(".txt")
# txt_path.write_text(assistant_reply, encoding="utf-8")
# print(f"✓ Extracted text also saved to {txt_path}")

# 9️⃣ Show summary information ------------------------------------------------
if document_id:
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"PDF File: {pdf_path}")
    print(f"Database ID: {document_id}")
    print(f"Text Length: {len(assistant_reply):,} characters")
    print(f"File Size: {file_size:,} bytes")
    print("\nTo retrieve this document later, you can use:")
    print(f"  get_document_by_id({document_id})")
    print(f"  get_documents_by_filename('{filename}')")
    print("="*60) 