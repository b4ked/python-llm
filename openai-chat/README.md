# RAG Chatbot with pgvector and GPT-4o

An intelligent chatbot that uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses by searching through your document embeddings stored in PostgreSQL with pgvector.

## Features

- 🔍 **Semantic Search**: Uses pgvector to find relevant documents based on vector similarity
- 🤖 **GPT-4o Integration**: Leverages OpenAI's latest GPT-4o model for response generation
- 📚 **Context-Aware**: Provides responses based on your specific knowledge base
- 💬 **Interactive Chat**: User-friendly interactive chat interface
- ⚙️ **Configurable**: Adjustable similarity thresholds and context document limits
- 📊 **Conversation History**: Tracks chat history and context usage
- 🔧 **Programmatic API**: Can be used both interactively and programmatically
- 📁 **Detailed File References**: Shows specific filenames, relevance scores, and content previews
- 📋 **Source Citations**: AI responses include clear citations to source documents

## Prerequisites

1. **Database Setup**: You need a PostgreSQL database with pgvector extension and embeddings generated
2. **Environment Variables**: Required environment variables for OpenAI API and database connection
3. **Dependencies**: Python packages listed in `requirements.txt`

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in your project root with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=python_llm_db
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   ```

3. **Generate Embeddings** (if not done already):
   ```bash
   cd ../openai-embedding
   python generate_embeddings.py
   ```

## Usage

### Interactive Chat Mode

Start an interactive chat session:

```bash
python chatbot.py
```

**Interactive Commands**:
- Type your questions naturally
- `history` - View conversation history
- `settings` - Adjust search parameters
- `quit`, `exit`, `bye`, or `q` - End the chat

### Programmatic Usage

```python
from chatbot import RAGChatbot

# Initialize chatbot
chatbot = RAGChatbot(similarity_threshold=0.7, max_context_docs=5)

# Connect to database
if chatbot.connect_to_database():
    try:
        # Ask a question
        response = chatbot.chat("What are the main features of machine learning?")
        print(response)
    finally:
        chatbot.disconnect_from_database()
```

### Example Usage Script

Run the example script to see different usage patterns:

```bash
python example_usage.py
```

## Configuration Options

### Similarity Threshold
- **Range**: 0.0 - 1.0
- **Default**: 0.3 (optimized for medical documents)
- **Description**: Minimum similarity score for documents to be considered relevant
- **Lower values**: More documents, potentially less relevant
- **Higher values**: Fewer documents, more precise matches

### Max Context Documents
- **Range**: 1 - 10
- **Default**: 10
- **Description**: Maximum number of relevant documents to include in context
- **More documents**: Richer context but longer prompts
- **Fewer documents**: Focused context, faster processing

## How It Works

1. **User Input**: User asks a question
2. **Embedding Generation**: Question is converted to a vector embedding using OpenAI's `text-embedding-3-small`
3. **Similarity Search**: pgvector finds the most similar document chunks in the database
4. **Context Construction**: Relevant documents are formatted into context
5. **Response Generation**: GPT-4o generates a response using the context and question
6. **Output**: User receives a context-aware response with detailed document citations and file references

## Architecture

```
User Question
     ↓
Generate Embedding (OpenAI)
     ↓
Search Similar Documents (pgvector)
     ↓
Construct Context
     ↓
Generate Response (GPT-4o)
     ↓
Return Answer with Citations
```

## Database Schema

The chatbot expects the following database structure:

```sql
-- Embeddings table
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255),
    content_chunk TEXT,
    embedding vector(1536),  -- for text-embedding-3-small
    chunk_index INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

## Error Handling

The chatbot includes comprehensive error handling for:
- Database connection failures
- OpenAI API errors
- Missing embeddings
- Invalid user input
- Network issues

## Enhanced File Reference Features

The chatbot now provides detailed information about source documents:

### During Search
- **File Discovery**: Shows all files found during semantic search
- **Relevance Scores**: Displays similarity scores for each document
- **Content Previews**: Shows snippet previews of relevant content
- **Chunk Information**: Indicates which part of the document (page/chunk) is being referenced

### In Responses
- **Source Citations**: AI responses include specific document names
- **Reference List**: Numbered list of all sources used in each response
- **Conversation History**: Tracks which files were referenced in each exchange

### Example Output
```
📋 Reference Files Found:
   📄 1. medical_guidelines.pdf (Chunk 3)
      🎯 Relevance Score: 0.847
      📝 Preview: This document discusses treatment protocols for...

📚 References used in this response:
   [1] medical_guidelines.pdf (Chunk 3) (Relevance: 0.847)
   [2] patient_handbook.docx (Page 15) (Relevance: 0.723)
```

## Performance Tips

1. **Optimize Similarity Threshold**: Start with 0.3 and adjust based on your data
2. **Limit Context Documents**: Use 5-10 documents for optimal balance
3. **Database Indexing**: Ensure proper pgvector indexes are created
4. **Embedding Model**: Using `text-embedding-3-small` to match your existing embeddings (1536 dimensions)

## Troubleshooting

### Common Issues

1. **"No embeddings found in database"**
   - Run `generate_embeddings.py` first to create embeddings from your documents

2. **"Failed to connect to database"**
   - Check your database connection parameters in `.env`
   - Ensure PostgreSQL is running and accessible

3. **"Error generating embedding"**
   - Verify your OpenAI API key is valid and has sufficient credits
   - Check your internet connection

4. **"No relevant documents found"**
   - Lower the similarity threshold
   - Check if your question relates to the content in your knowledge base

### Debug Mode

For debugging, you can modify the chatbot to print more detailed information:

```python
# In chatbot.py, add debug prints
print(f"Query embedding length: {len(query_embedding)}")
print(f"Search results: {len(results)}")
print(f"Context length: {len(context)} characters")
```

## Contributing

Feel free to enhance the chatbot with additional features:
- Conversation memory across sessions
- Multi-language support
- Custom prompt templates
- Response caching
- Streaming responses

## License

This project is part of the python-llm workspace and follows the same licensing terms. 