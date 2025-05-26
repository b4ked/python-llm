#!/usr/bin/env python3
"""
Intelligent Chatbot with RAG (Retrieval-Augmented Generation)
Uses pgvector to find relevant document embeddings and GPT-4o for response generation.
"""

import os
import sys
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db'))
from database import DatabaseConnection

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"  # Match the model used for existing embeddings (1536 dimensions)
CHAT_MODEL = "gpt-4o"  # Using GPT-4o as requested
DEFAULT_SIMILARITY_THRESHOLD = 0.3  # Optimized for your medical documents (typical scores 0.3-0.4)
DEFAULT_MAX_CONTEXT_DOCS = 10
MAX_CONTEXT_LENGTH = 8000  # Maximum characters for context


class RAGChatbot:
    """Retrieval-Augmented Generation Chatbot"""
    
    def __init__(self, similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD, 
                 max_context_docs: int = DEFAULT_MAX_CONTEXT_DOCS):
        self.similarity_threshold = similarity_threshold
        self.max_context_docs = max_context_docs
        self.db = DatabaseConnection()
        self.conversation_history = []
        
    def connect_to_database(self) -> bool:
        """Establish database connection"""
        if not self.db.connect():
            print("❌ Failed to connect to database")
            return False
        return True
    
    def disconnect_from_database(self):
        """Close database connection"""
        self.db.disconnect()
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a given text using OpenAI API"""
        try:
            response = openai.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None
    
    def search_relevant_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search for documents relevant to the query using vector similarity"""
        print(f"🔍 Searching for relevant documents...")
        
        # Generate embedding for the query
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            print("❌ Failed to generate query embedding")
            return []
        
        # Search for similar documents
        try:
            results = self.db.find_similar_embeddings(
                query_embedding, 
                similarity_threshold=self.similarity_threshold, 
                max_results=self.max_context_docs
            )
            
            if not results:
                print("📭 No relevant documents found")
                print(f"   (Using similarity threshold: {self.similarity_threshold})")
                print("   💡 Try lowering the threshold in settings or check if your documents contain relevant content")
                return []
            
            print(f"✅ Found {len(results)} relevant document(s)")
            # Show similarity scores for debugging
            for i, doc in enumerate(results, 1):
                similarity = doc.get('similarity', 0)
                print(f"   📄 Document {i}: Similarity {similarity:.3f}")
            return results
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def construct_context(self, relevant_docs: List[Dict[str, Any]]) -> str:
        """Construct context from relevant documents"""
        if not relevant_docs:
            return ""
        
        context_parts = []
        total_length = 0
        
        for i, doc in enumerate(relevant_docs, 1):
            # Extract metadata for better context
            metadata = doc.get('metadata', {})
            if isinstance(metadata, str):
                import json
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            # Create document header
            filename = metadata.get('filename', f'Document {doc.get("document_id", "Unknown")}')
            similarity = doc.get('similarity', 0)
            
            doc_header = f"Document {i}: {filename} (Relevance: {similarity:.2f})"
            doc_content = doc.get('content_chunk', '')
            
            # Format the document
            formatted_doc = f"{doc_header}\n{'-' * len(doc_header)}\n{doc_content}\n"
            
            # Check if adding this document would exceed the context length
            if total_length + len(formatted_doc) > MAX_CONTEXT_LENGTH:
                break
            
            context_parts.append(formatted_doc)
            total_length += len(formatted_doc)
        
        return "\n".join(context_parts)
    
    def construct_prompt(self, user_query: str, context: str) -> List[Dict[str, str]]:
        """Construct the conversation prompt for GPT-4o"""
        system_message = """You are an intelligent assistant with access to a knowledge base. 
Use the provided context documents to answer questions accurately and comprehensively. 
If the context doesn't contain enough information to fully answer the question, say so clearly.
Always cite which documents you're referencing when possible.
Be helpful, accurate, and conversational."""
        
        if context:
            user_content = f"""Context Documents:
{context}

Question: {user_query}

Please answer the question using the context provided above. If you reference information from the context, please mention which document it came from."""
        else:
            user_content = f"""Question: {user_query}

Note: No relevant context documents were found in the knowledge base. Please provide a general response based on your training knowledge, but mention that you don't have specific context documents to reference."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]
        
        return messages
    
    def generate_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Generate response using GPT-4o"""
        try:
            print("🤖 Generating response with GPT-4o...")
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None
    
    def chat(self, user_query: str) -> Optional[str]:
        """Main chat function that handles the complete RAG pipeline"""
        print(f"\n{'='*60}")
        print(f"User: {user_query}")
        print(f"{'='*60}")
        
        # Search for relevant documents
        relevant_docs = self.search_relevant_documents(user_query)
        
        # Construct context from relevant documents
        context = self.construct_context(relevant_docs)
        
        if context:
            print(f"📚 Using context from {len(relevant_docs)} document(s)")
        else:
            print("📝 No relevant context found, using general knowledge")
        
        # Construct prompt
        messages = self.construct_prompt(user_query, context)
        
        # Generate response
        response = self.generate_response(messages)
        
        if response:
            print(f"\n🤖 Assistant: {response}")
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_query,
                "assistant": response,
                "context_docs": len(relevant_docs)
            })
        else:
            print("❌ Failed to generate response")
        
        return response
    
    def interactive_chat(self):
        """Start an interactive chat session"""
        print("🤖 RAG Chatbot with pgvector and GPT-4o")
        print("="*60)
        print("Ask me anything! I'll search through the knowledge base to provide accurate answers.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'history' to see conversation history.")
        print("Type 'settings' to adjust search parameters.")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for chatting! Goodbye!")
                    break
                
                if user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                if user_input.lower() == 'settings':
                    self.adjust_settings()
                    continue
                
                if not user_input:
                    print("Please enter a question or message.")
                    continue
                
                # Process the chat
                self.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
    
    def show_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("📭 No conversation history yet.")
            return
        
        print(f"\n📚 Conversation History ({len(self.conversation_history)} exchanges)")
        print("="*60)
        
        for i, exchange in enumerate(self.conversation_history, 1):
            print(f"\n{i}. User: {exchange['user'][:100]}{'...' if len(exchange['user']) > 100 else ''}")
            print(f"   Assistant: {exchange['assistant'][:100]}{'...' if len(exchange['assistant']) > 100 else ''}")
            print(f"   Context docs used: {exchange['context_docs']}")
    
    def adjust_settings(self):
        """Allow user to adjust search parameters"""
        print(f"\n⚙️ Current Settings:")
        print(f"   Similarity threshold: {self.similarity_threshold}")
        print(f"   Max context documents: {self.max_context_docs}")
        
        try:
            new_threshold = input(f"\nEnter new similarity threshold (0.0-1.0, current: {self.similarity_threshold}): ").strip()
            if new_threshold:
                threshold = float(new_threshold)
                if 0.0 <= threshold <= 1.0:
                    self.similarity_threshold = threshold
                    print(f"✅ Similarity threshold updated to {threshold}")
                else:
                    print("❌ Threshold must be between 0.0 and 1.0")
            
            new_max_docs = input(f"Enter max context documents (1-10, current: {self.max_context_docs}): ").strip()
            if new_max_docs:
                max_docs = int(new_max_docs)
                if 1 <= max_docs <= 10:
                    self.max_context_docs = max_docs
                    print(f"✅ Max context documents updated to {max_docs}")
                else:
                    print("❌ Max documents must be between 1 and 10")
                    
        except ValueError:
            print("❌ Invalid input. Settings unchanged.")


def main():
    """Main function"""
    print("🚀 Starting RAG Chatbot...")
    
    # Initialize chatbot
    chatbot = RAGChatbot()
    
    # Connect to database
    if not chatbot.connect_to_database():
        print("❌ Cannot start chatbot without database connection")
        return 1
    
    try:
        # Check if we have embeddings in the database
        result = chatbot.db.execute_query("SELECT COUNT(*) as count FROM embeddings")
        if result and result[0]['count'] > 0:
            print(f"✅ Found {result[0]['count']} embeddings in knowledge base")
        else:
            print("⚠️ No embeddings found in database")
            print("   The chatbot will work but won't have access to your knowledge base.")
            print("   Run generate_embeddings.py first to create embeddings from your documents.")
        
        # Start interactive chat
        chatbot.interactive_chat()
        
    finally:
        # Clean up
        chatbot.disconnect_from_database()
    
    return 0


if __name__ == "__main__":
    exit(main()) 