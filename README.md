# Python LLM Tools

A comprehensive toolkit for text extraction, embedding generation, and semantic search using OpenAI APIs with PostgreSQL vector database storage.

## 🚀 Features

- **PDF Text Extraction**: Extract text from PDFs using OpenAI's GPT-4o with file search capabilities
- **Image Text Extraction**: Extract text from images using OpenAI's GPT-4o Vision API
- **Vector Embeddings**: Generate and store OpenAI embeddings for semantic search
- **PostgreSQL Integration**: Store documents and embeddings in a PostgreSQL database with pgvector support
- **Batch Processing**: Process multiple documents and images with automated workflows
- **Semantic Search**: Perform similarity searches using vector embeddings
- **RAG Chatbot**: Interactive chatbot with Retrieval-Augmented Generation using GPT-4o and pgvector

## 📁 Repository Structure

```
├── openai-pdf/          # PDF text extraction tools
├── openai-img/          # Image text extraction tools
├── openai-embedding/    # Embedding generation and search
├── openai-chat/         # RAG chatbot with GPT-4o integration
└── db/                  # PostgreSQL database setup with pgvector
```

## 🛠 Components

### PDF Processing (`openai-pdf/`)
- Extract text from PDF files using OpenAI's GPT-4o
- Store extracted content in PostgreSQL database
- Batch processing capabilities with shell scripts
- Duplicate detection and error handling

### Image Processing (`openai-img/`)
- Extract text from images using OpenAI's GPT-4o Vision API
- Support for multiple image formats (JPG, PNG, GIF, BMP, WebP, TIFF)
- Store extracted content in PostgreSQL database
- Batch processing with duplicate detection
- Automatic Python environment detection (conda/anaconda preferred)

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

3. **Extract text from documents:**
   ```bash
   # From PDF
   cd openai-pdf
   python openai-pdf-db.py /path/to/document.pdf
   
   # From images
   cd ../openai-img
   python openai-img-db.py /path/to/image.jpg
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

1. **Document Ingestion**: Extract text from various sources
   - **PDFs** (`openai-pdf/`): Extract text from PDF documents
   - **Images** (`openai-img/`): Extract text from images (screenshots, scanned documents, etc.)
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

# 3. Process images (optional)
cd ../openai-img
./batch_process_images.sh /path/to/your/images

# 4. Generate embeddings
cd ../openai-embedding
python generate_embeddings.py

# 5. Start chatbot
cd ../openai-chat
python chatbot.py
```

## 🔄 Batch Processing

Both PDF and image processing support efficient batch operations:

### PDF Batch Processing
```bash
cd openai-pdf
./process_all_pdfs.sh  # Processes all PDFs in reports/ directory
```

### Image Batch Processing
```bash
cd openai-img
./batch_process_images.sh /path/to/images  # Processes all images in specified directory
./batch_process_images.sh                  # Processes all images in /img directory (default)
```

**Features:**
- Automatic duplicate detection (skips already processed files)
- Progress tracking with colored output
- Detailed logging with timestamps
- Error handling and recovery
- Summary reports
- Automatic Python environment detection

## 🔧 Configuration

- Database connection settings in `db/config.py`
- Embedding model selection in `openai-embedding/generate_embeddings.py`
- PDF batch processing options in `openai-pdf/process_all_pdfs.sh`
- Image batch processing options in `openai-img/batch_process_images.sh`
- Chatbot parameters (similarity threshold, max documents) in `openai-chat/chatbot.py`

## 📖 Documentation

Each component includes detailed README files:
- [PDF Processing Guide](openai-pdf/README-DB.md)
- [Image Processing Guide](openai-img/README.md)
- [Embedding Generation Guide](openai-embedding/README.md)
- [RAG Chatbot Guide](openai-chat/README.md)
- [Database Setup Guide](db/README.md)

## 🎯 Use Cases

- **Document analysis and content extraction**: Extract text from PDFs and images
- **Building semantic search systems**: Search across your document collection using natural language
- **Creating knowledge bases**: Build searchable repositories from various document types
- **Research paper analysis**: Analyze and find similarities between research documents
- **Content recommendation systems**: Recommend related content based on semantic similarity
- **Interactive Q&A systems**: Ask questions about your documents and get intelligent, context-aware answers
- **Customer support chatbots**: Build chatbots that can answer questions based on your documentation
- **Research assistance**: Query large document collections for specific information with source citations
- **Image text extraction**: Extract text from screenshots, scanned documents, receipts, and other images
- **Multi-format document processing**: Handle both digital PDFs and image-based documents in a unified workflow
