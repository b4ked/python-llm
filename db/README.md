# PostgreSQL Docker Setup with pgvector

This directory contains a PostgreSQL database setup using Docker with pgvector extension for vector similarity search. The database can be accessed by Python scripts throughout the project and supports storing and querying vector embeddings.

## Quick Start

1. **Start the database:**
   ```bash
   cd db
   docker-compose up -d
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the connection:**
   ```bash
   python database.py
   ```

## Database Configuration

- **Host:** localhost
- **Port:** 5432
- **Database:** python_llm_db
- **Username:** postgres
- **Password:** postgres123

## Files

- `docker-compose.yml` - Docker Compose configuration for PostgreSQL with pgvector
- `init/01-init.sql` - Database initialization script with users and documents tables
- `init/02-pgvector.sql` - pgvector extension setup and embeddings table creation
- `config.py` - Database connection configuration
- `database.py` - Python utility functions for database operations including vector operations
- `requirements.txt` - Python dependencies including pgvector support

## Usage from Other Folders

To use the database from Python scripts in other folders (like `openai-pdf/`), you can import the database utilities:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection

# Use the database
db = DatabaseConnection()
if db.connect():
    # Your database operations here
    users = db.execute_query("SELECT * FROM users")
    print(users)
    db.disconnect()
```

## Docker Commands

- **Start database:** `docker-compose up -d`
- **Stop database:** `docker-compose down`
- **View logs:** `docker-compose logs postgres`
- **Access PostgreSQL shell:** `docker exec -it python-llm-postgres psql -U postgres -d python_llm_db`

## Database Schema

The database is initialized with the following tables:

1. **users** - Sample user table with id, username, email, created_at
2. **documents** - Table for storing document metadata (useful for PDF processing)
3. **embeddings** - Table for storing vector embeddings with the following columns:
   - `id` - Primary key
   - `document_id` - Foreign key to documents table
   - `content_chunk` - Text content that was embedded
   - `embedding` - Vector embedding (1536 dimensions for OpenAI ada-002)
   - `chunk_index` - Index of the chunk within the document
   - `metadata` - JSONB field for additional metadata
   - `created_at` - Timestamp

## Vector Operations

The database includes several helper functions for vector operations:

- `cosine_similarity(a, b)` - Calculate cosine similarity between two vectors
- `find_similar_embeddings(query_embedding, threshold, max_results)` - Find similar embeddings using cosine similarity

### Python Vector Operations

The `DatabaseConnection` class includes methods for working with embeddings:

```python
# Insert an embedding
embedding_id = db.insert_embedding(
    document_id=1,
    content_chunk="Your text content here",
    embedding=your_embedding_vector,  # numpy array or list
    chunk_index=0,
    metadata={"source": "pdf", "page": 1}
)

# Find similar embeddings
similar = db.find_similar_embeddings(
    query_embedding=query_vector,
    similarity_threshold=0.8,
    max_results=10
)

# Get all embeddings for a document
embeddings = db.get_embeddings_by_document(document_id=1)
```

## Example Usage

Run the example script to see vector embeddings in action:

```bash
cd db
python example_vector_usage.py
```

This script demonstrates:
- Creating documents and inserting vector embeddings
- Performing similarity searches
- Retrieving embeddings by document

## Environment Variables

You can override the default database configuration by setting these environment variables:

- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: python_llm_db)
- `DB_USER` (default: postgres)
- `DB_PASSWORD` (default: postgres123) 