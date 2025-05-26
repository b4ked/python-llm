# Python LLM Tools

A comprehensive toolkit for text extraction, embedding generation, and semantic search using OpenAI APIs with PostgreSQL vector database storage.

## 🚀 Features

- **PDF Text Extraction**: Extract text from PDFs using OpenAI's GPT-4o with file search capabilities
- **Vector Embeddings**: Generate and store OpenAI embeddings for semantic search
- **PostgreSQL Integration**: Store documents and embeddings in a PostgreSQL database with pgvector support
- **Batch Processing**: Process multiple documents with automated workflows
- **Semantic Search**: Perform similarity searches using vector embeddings

## 📁 Repository Structure

```
├── openai-pdf/          # PDF text extraction tools
├── openai-embedding/    # Embedding generation and search
├── db/                  # PostgreSQL database setup with pgvector
└── openai-img/          # Image processing tools (placeholder)
```

## 🛠 Components

### PDF Processing (`openai-pdf/`)
- Extract text from PDF files using OpenAI's GPT-4o
- Store extracted content in PostgreSQL database
- Batch processing capabilities with shell scripts
- Duplicate detection and error handling

### Embedding Generation (`openai-embedding/`)
- Generate vector embeddings using OpenAI's text-embedding models
- Support for both `text-embedding-3-small` (1536d) and `text-embedding-3-large` (3072d)
- Semantic search functionality with similarity thresholds
- Automatic chunking and metadata storage

### Database (`db/`)
- PostgreSQL Docker container with pgvector extension
- Pre-configured schemas for documents and embeddings
- Vector similarity search functions
- Python utilities for database operations

## 🚀 Quick Start

1. **Start the database:**
   ```bash
   cd db && docker-compose up -d
   ```

2. **Set OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Extract text from PDF:**
   ```bash
   cd openai-pdf
   python openai-pdf-db.py /path/to/document.pdf
   ```

4. **Generate embeddings:**
   ```bash
   cd openai-embedding
   python update_embedding_schema.py  # First time only
   python generate_embeddings.py
   ```

5. **Perform semantic search:**
   ```bash
   python search_example.py
   ```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.7+
- OpenAI API key
- Required Python packages (see individual `requirements.txt` files)

## 🔧 Configuration

- Database connection settings in `db/config.py`
- Embedding model selection in `openai-embedding/generate_embeddings.py`
- Batch processing options in `openai-pdf/process_all_pdfs.sh`

## 📖 Documentation

Each component includes detailed README files:
- [PDF Processing Guide](openai-pdf/README-DB.md)
- [Embedding Generation Guide](openai-embedding/README.md)
- [Database Setup Guide](db/README.md)

## 🎯 Use Cases

- Document analysis and content extraction
- Building semantic search systems
- Creating knowledge bases from PDF documents
- Research paper analysis and similarity matching
- Content recommendation systems
