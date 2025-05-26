# OpenAI PDF Database Integration

This directory contains scripts for extracting text from PDF files using OpenAI and storing the results in a PostgreSQL database.

## Files

- `openai-pdf.py` - Original script that extracts PDF text and saves to a text file
- `openai-pdf-db.py` - **NEW** Enhanced script that extracts PDF text and stores it in PostgreSQL database
- `test_db_functions.py` - Test script to demonstrate database helper functions
- `database_example.py` - Example database operations (existing)

## Prerequisites

1. **OpenAI API Key**: Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **PostgreSQL Database**: Ensure the PostgreSQL Docker container is running from the `/db` folder:
   ```bash
   cd ../db
   docker-compose up -d
   ```

3. **Python Dependencies**: Install required packages:
   ```bash
   pip install openai psycopg2-binary sqlalchemy pgvector
   ```

## Usage

### Extract PDF and Store in Database

```bash
python openai-pdf-db.py /path/to/your/document.pdf
```

This script will:
1. Upload the PDF to OpenAI
2. Extract all text content using GPT-4o with file search
3. Store the extracted text in the `documents` table
4. Display a summary with the database ID

### Test Database Functions

```bash
python test_db_functions.py
```

This will demonstrate:
- Listing all documents in the database
- Retrieving a specific document by ID
- Searching for documents by filename

## Database Schema

The script uses the `documents` table with the following structure:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    file_type VARCHAR(50)
);
```

## Helper Functions

The `openai-pdf-db.py` script includes several helper functions:

### `store_document_in_db(filename, content, file_size, file_type="pdf")`
Stores a document in the database and returns the document ID.

### `get_document_by_id(doc_id)`
Retrieves a document by its database ID.

### `get_documents_by_filename(filename)`
Retrieves all documents with a specific filename (useful for finding duplicates).

### `list_all_documents()`
Lists all documents in the database with basic information.

## Example Output

```
⇢ Uploading PDF …
⇢ Ensuring Assistant exists …
using existing assistant
⇢ Creating thread and run …
⇢ Waiting for file search to finish …
   status: in_progress …
   status: completed …
⇢ Storing extracted text in database …
✓ Document 'sample.pdf' stored successfully in database with ID: 5
✓ PDF text extraction and database storage completed successfully!
  - File: sample.pdf
  - Size: 245,760 bytes
  - Text length: 12,543 characters
  - Database ID: 5

============================================================
EXTRACTION SUMMARY
============================================================
PDF File: /path/to/sample.pdf
Database ID: 5
Text Length: 12,543 characters
File Size: 245,760 bytes

To retrieve this document later, you can use:
  get_document_by_id(5)
  get_documents_by_filename('sample.pdf')
============================================================
```

## Features

- **Duplicate Detection**: Warns if a document with the same filename already exists
- **Error Handling**: Graceful error handling with rollback on database failures
- **Fallback**: Saves to text file if database storage fails
- **Transaction Safety**: Uses proper database transactions with commit/rollback
- **Detailed Logging**: Provides clear status messages throughout the process

## Integration with Vector Search

The database is set up with pgvector support. You can extend this script to also create embeddings for the extracted text and store them in the `embeddings` table for semantic search capabilities.

## Troubleshooting

1. **Database Connection Issues**: Ensure the PostgreSQL container is running and accessible
2. **OpenAI API Issues**: Check your API key and quota
3. **File Not Found**: Ensure the PDF file path is correct and the file exists
4. **Permission Issues**: Make sure the script has read access to the PDF file

## Related Scripts

- See `../db/database.py` for core database utilities
- See `../db/example_vector_usage.py` for vector embedding examples
- See `database_example.py` for additional database operation examples 