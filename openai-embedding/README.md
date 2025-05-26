# OpenAI Embedding Generator

This directory contains scripts to generate OpenAI embeddings for documents stored in the PostgreSQL database and store them in the embeddings table for semantic search capabilities.

## Files

- `generate_embeddings.py` - Main script to generate embeddings for all documents
- `update_embedding_schema.py` - Schema update script for text-embedding-3-small (1536 dimensions)
- `update_embedding_schema_large.py` - Schema update script for text-embedding-3-large (3072 dimensions with HNSW)
- `search_example.py` - Example semantic search script
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Prerequisites

### 1. Environment Setup

Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

### 2. Database Setup

Ensure the PostgreSQL Docker container is running from the `/db` folder:
```bash
cd ../db
docker-compose up -d
```

### 3. Python Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Update Database Schema (First Time Only)

Choose one of the following options based on your needs:

#### Option A: text-embedding-3-small (Recommended for most users)
```bash
python update_embedding_schema.py
```

This script will:
- Update the embeddings table to support 1536-dimension vectors
- Use ivfflat indexing (standard and well-tested)
- Clear any existing embeddings (if present)

#### Option B: text-embedding-3-large (Higher quality, requires HNSW)
```bash
python update_embedding_schema_large.py
```

This script will:
- Update the embeddings table to support 3072-dimension vectors
- Use HNSW indexing (better for high-dimensional vectors)
- Clear any existing embeddings (if present)

**Note:** If you choose Option B, you'll also need to update the `EMBEDDING_MODEL` in `generate_embeddings.py` to `"text-embedding-3-large"` and `EMBEDDING_DIMENSION` to `3072`.

### Step 2: Generate Embeddings

Run the main embedding generation script:

```bash
python generate_embeddings.py
```

This script will:
- Connect to the PostgreSQL database
- Retrieve all documents from the `documents` table
- Generate embeddings using OpenAI's `text-embedding-3-small` model (or 3-large if configured)
- Store embeddings in the `embeddings` table
- Skip documents that already have embeddings (duplicate prevention)
- Provide detailed progress and summary information

## Features

### Duplicate Prevention
- Checks if embeddings already exist before generating new ones
- Uses `ON CONFLICT` clause to handle potential race conditions
- Skips processing for documents that already have embeddings

### Error Handling
- Graceful error handling for API failures
- Database transaction rollback on errors
- Detailed error reporting and logging

### Progress Tracking
- Real-time progress updates for each document
- Comprehensive summary at completion
- Clear status indicators (✓, ✗, ⏭️, 🔄)

### Metadata Storage
- Stores rich metadata with each embedding:
  - Original filename
  - File type and size
  - Processing timestamp
  - Content length
  - Embedding model used

## Database Schema

### Documents Table
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

### Embeddings Table
```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content_chunk TEXT NOT NULL,
    embedding vector(1536), -- text-embedding-3-small dimensions (or 3072 for large)
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index)
);
```

## Example Output

```
OpenAI Embedding Generator for PostgreSQL Documents
============================================================
✓ Successfully connected to PostgreSQL database with pgvector support
🚀 Starting embedding generation process...
✓ Found 3 documents with content

📄 Processing document 1: sample.pdf
   🔄 Generating embedding...
   ✓ Embedding stored successfully

📄 Processing document 2: report.pdf
   ⏭️  Embedding already exists, skipping...

📄 Processing document 3: manual.pdf
   🔄 Generating embedding...
   ✓ Embedding stored successfully

============================================================
EMBEDDING GENERATION SUMMARY
============================================================
Total documents found: 3
Embeddings created: 2
Documents skipped (already exist): 1
Errors encountered: 0
============================================================
✓ Successfully generated 2 new embeddings!
ℹ️  Skipped 1 documents that already had embeddings
✓ Database connection closed
```

## Configuration

### Embedding Model
The script uses OpenAI's `text-embedding-3-small` model by default, which provides:
- 1536 dimensions
- High-quality embeddings
- Good balance of performance and cost
- Compatible with standard ivfflat indexing

To use the larger model, modify the `EMBEDDING_MODEL` constant in `generate_embeddings.py`:
```python
EMBEDDING_MODEL = "text-embedding-3-large"  # 3072 dimensions (requires HNSW schema)
EMBEDDING_DIMENSION = 3072
# or
EMBEDDING_MODEL = "text-embedding-ada-002"  # 1536 dimensions (legacy)
```

**Note:** If you change to the 3-large model, you must run `update_embedding_schema_large.py` first.

### Database Configuration
Database connection settings are inherited from `../db/config.py`. The script automatically imports the configuration from the parent db directory.

## Integration with Vector Search

Once embeddings are generated, you can use them for semantic search:

```python
from db.database import DatabaseConnection

db = DatabaseConnection()
db.connect()

# Example: Find similar content
query_embedding = get_embedding("your search query")
similar_docs = db.find_similar_embeddings(
    query_embedding, 
    similarity_threshold=0.8, 
    max_results=5
)
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```
   ✗ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.
   ```
   Solution: Set the `OPENAI_API_KEY` environment variable

2. **Database Connection Error**
   ```
   ✗ Error connecting to database: connection refused
   ```
   Solution: Ensure PostgreSQL container is running (`docker-compose up -d` in `/db` folder)

3. **Schema Dimension Mismatch**
   ```
   ✗ Error inserting embedding: dimension mismatch
   ```
   Solution: Run `update_embedding_schema.py` to update the schema

4. **No Documents Found**
   ```
   No documents found to process
   ```
   Solution: Ensure documents exist in the `documents` table with non-empty content

### Performance Considerations

- **API Rate Limits**: OpenAI has rate limits. The script processes documents sequentially to avoid hitting limits
- **Large Documents**: Very large documents may take longer to process
- **Database Performance**: The vector index improves similarity search performance but may slow down insertions

## Related Scripts

- `../db/database.py` - Core database utilities with vector support
- `../db/example_vector_usage.py` - Examples of vector search operations
- `../openai-pdf/openai-pdf-db.py` - PDF processing and document storage 