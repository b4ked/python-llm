# Python LLM Tools

A comprehensive toolkit for text extraction, embedding generation, and semantic search using OpenAI APIs with PostgreSQL vector database storage.

## 🚀 Features

- **PDF Text Extraction**: Extract text from PDFs using OpenAI's GPT-4o with file search capabilities
- **Vector Embeddings**: Generate and store OpenAI embeddings for semantic search
- **PostgreSQL Integration**: Store documents and embeddings in a PostgreSQL database with pgvector support
- **Batch Processing**: Process multiple documents with automated workflows
- **Semantic Search**: Perform similarity searches using vector embeddings
- **RAG Chatbot**: Interactive chatbot with Retrieval-Augmented Generation using GPT-4o and pgvector

## 📁 Repository Structure

```
├── openai-pdf/          # PDF text extraction tools
├── openai-embedding/    # Embedding generation and search
├── openai-chat/         # RAG chatbot with GPT-4o integration
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

### RAG Chatbot (`openai-chat/`)
- Interactive chatbot with Retrieval-Augmented Generation (RAG)
- Uses GPT-4o for intelligent responses based on your knowledge base
- Semantic search integration with pgvector for context retrieval
- Detailed file reference tracking and citation capabilities
- Configurable similarity thresholds and conversation history

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

6. **Start the RAG chatbot:**
   ```bash
   cd openai-chat
   python chatbot.py
   ```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.7+
- OpenAI API key
- Required Python packages (see individual `requirements.txt` files)

## 💬 Complete RAG Workflow

The repository provides a complete pipeline from document processing to intelligent chatbot:

1. **Document Ingestion** (`openai-pdf/`): Extract text from PDF documents
2. **Embedding Generation** (`openai-embedding/`): Create vector embeddings for semantic search
3. **Database Storage** (`db/`): Store documents and embeddings in PostgreSQL with pgvector
4. **Interactive Chat** (`openai-chat/`): Query your knowledge base with natural language

### Example Workflow:
```bash
# 1. Start database
cd db && docker-compose up -d

# 2. Process documents
cd ../openai-pdf
python openai-pdf-db.py /path/to/your/documents/*.pdf

# 3. Generate embeddings
cd ../openai-embedding
python generate_embeddings.py

# 4. Start chatbot
cd ../openai-chat
python chatbot.py
```

## 🔧 Configuration

- Database connection settings in `db/config.py`
- Embedding model selection in `openai-embedding/generate_embeddings.py`
- Batch processing options in `openai-pdf/process_all_pdfs.sh`
- Chatbot parameters (similarity threshold, max documents) in `openai-chat/chatbot.py`

## 📖 Documentation

Each component includes detailed README files:
- [PDF Processing Guide](openai-pdf/README-DB.md)
- [Embedding Generation Guide](openai-embedding/README.md)
- [RAG Chatbot Guide](openai-chat/README.md)
- [Database Setup Guide](db/README.md)

## 🎯 Use Cases

- Document analysis and content extraction
- Building semantic search systems
- Creating knowledge bases from PDF documents
- Research paper analysis and similarity matching
- Content recommendation systems
- **Interactive Q&A systems**: Ask questions about your documents and get intelligent, context-aware answers
- **Customer support chatbots**: Build chatbots that can answer questions based on your documentation
- **Research assistance**: Query large document collections for specific information with source citations
