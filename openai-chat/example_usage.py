#!/usr/bin/env python3
"""
Example usage of the RAG Chatbot
Demonstrates both programmatic usage and batch processing
"""

from chatbot import RAGChatbot

def single_question_example():
    """Example of asking a single question programmatically"""
    print("🔍 Single Question Example")
    print("="*50)
    
    # Initialize chatbot
    chatbot = RAGChatbot(similarity_threshold=0.7, max_context_docs=3)
    
    # Connect to database
    if not chatbot.connect_to_database():
        print("❌ Failed to connect to database")
        return
    
    try:
        # Ask a question
        question = "What are the main features of machine learning?"
        response = chatbot.chat(question)
        
        if response:
            print(f"\n✅ Successfully got response for: '{question}'")
        else:
            print(f"\n❌ Failed to get response for: '{question}'")
    
    finally:
        chatbot.disconnect_from_database()

def batch_questions_example():
    """Example of processing multiple questions in batch"""
    print("\n📋 Batch Questions Example")
    print("="*50)
    
    # Initialize chatbot
    chatbot = RAGChatbot(similarity_threshold=0.6, max_context_docs=5)
    
    # Connect to database
    if not chatbot.connect_to_database():
        print("❌ Failed to connect to database")
        return
    
    # List of questions to process
    questions = [
        "How does data processing work?",
        "What are the best practices for database design?",
        "Explain the concept of user interface design",
        "What are the benefits of using embeddings?"
    ]
    
    try:
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n📝 Processing question {i}/{len(questions)}")
            response = chatbot.chat(question)
            results.append({
                "question": question,
                "response": response,
                "success": response is not None
            })
        
        # Summary
        successful = sum(1 for r in results if r["success"])
        print(f"\n📊 Batch Processing Summary:")
        print(f"   Total questions: {len(questions)}")
        print(f"   Successful responses: {successful}")
        print(f"   Failed responses: {len(questions) - successful}")
        
        return results
    
    finally:
        chatbot.disconnect_from_database()

def custom_settings_example():
    """Example of using custom settings"""
    print("\n⚙️ Custom Settings Example")
    print("="*50)
    
    # Initialize chatbot with custom settings
    chatbot = RAGChatbot(
        similarity_threshold=0.8,  # Higher threshold for more precise matches
        max_context_docs=2         # Fewer documents for focused context
    )
    
    # Connect to database
    if not chatbot.connect_to_database():
        print("❌ Failed to connect to database")
        return
    
    try:
        print(f"🔧 Using custom settings:")
        print(f"   Similarity threshold: {chatbot.similarity_threshold}")
        print(f"   Max context documents: {chatbot.max_context_docs}")
        
        # Ask a specific question
        question = "What is the purpose of vector embeddings in search?"
        response = chatbot.chat(question)
        
        if response:
            print(f"\n✅ Got response with custom settings")
        
    finally:
        chatbot.disconnect_from_database()

def main():
    """Run all examples"""
    print("🚀 RAG Chatbot Usage Examples")
    print("="*60)
    
    # Run examples
    single_question_example()
    batch_questions_example()
    custom_settings_example()
    
    print("\n🎉 All examples completed!")
    print("\nTo start an interactive chat session, run:")
    print("   python chatbot.py")

if __name__ == "__main__":
    main() 