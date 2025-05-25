-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table for storing vector embeddings
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content_chunk TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 embedding dimension
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Create index for similarity search
    CONSTRAINT unique_document_chunk UNIQUE (document_id, chunk_index)
);

-- Create index for vector similarity search using cosine distance
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create index for document_id lookups
CREATE INDEX IF NOT EXISTS embeddings_document_id_idx ON embeddings (document_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE embeddings TO postgres;
GRANT ALL PRIVILEGES ON SEQUENCE embeddings_id_seq TO postgres;

-- Add some helpful functions for vector operations
CREATE OR REPLACE FUNCTION cosine_similarity(a vector, b vector)
RETURNS float AS $$
BEGIN
    RETURN 1 - (a <=> b);
END;
$$ LANGUAGE plpgsql;

-- Function to find similar embeddings
CREATE OR REPLACE FUNCTION find_similar_embeddings(
    query_embedding vector,
    similarity_threshold float DEFAULT 0.8,
    max_results integer DEFAULT 10
)
RETURNS TABLE (
    id integer,
    document_id integer,
    content_chunk text,
    similarity float,
    metadata jsonb
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.document_id,
        e.content_chunk,
        cosine_similarity(e.embedding, query_embedding) as similarity,
        e.metadata
    FROM embeddings e
    WHERE cosine_similarity(e.embedding, query_embedding) >= similarity_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql; 