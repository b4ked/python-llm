#!/usr/bin/env python3
"""
example_usage.py

Example script showing how to use the image text extraction functionality programmatically.
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add the db directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

def load_image_extractor():
    """Load the image extraction module"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("openai_img_db", 
                                                 os.path.join(current_dir, "openai-img-db.py"))
    if spec and spec.loader:
        openai_img_db = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openai_img_db)
        return openai_img_db
    else:
        raise ImportError("Could not load openai-img-db.py module")

def example_extract_and_store(image_path):
    """
    Example function showing how to extract text from an image and store it in the database
    """
    try:
        # Load the image extraction module
        img_extractor = load_image_extractor()
        
        # Check if the image file exists
        if not Path(image_path).is_file():
            print(f"Error: Image file not found: {image_path}")
            return False
        
        print(f"Processing image: {image_path}")
        
        # Extract text from the image
        extracted_text = img_extractor.extract_text_from_image(image_path)
        print("Text extraction completed successfully")
        
        # Get file information
        file_path = Path(image_path)
        filename = file_path.name
        file_size = file_path.stat().st_size
        
        # Store in database
        document_id = img_extractor.store_document_in_db(filename, extracted_text, file_size, "image")
        
        if document_id:
            print(f"Document stored successfully with ID: {document_id}")
            
            # Show preview of extracted text
            lines = extracted_text.split('\n')
            if len(lines) > 0:
                print(f"Title: {lines[0]}")
            
            if len(extracted_text) > 200:
                print(f"Preview: {extracted_text[:200]}...")
            else:
                print(f"Full content: {extracted_text}")
            
            return document_id
        else:
            print("Failed to store document in database")
            return False
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def example_batch_process(image_directory):
    """
    Example function showing how to process multiple images in a directory
    """
    try:
        img_extractor = load_image_extractor()
        
        image_dir = Path(image_directory)
        if not image_dir.is_dir():
            print(f"Error: Directory not found: {image_directory}")
            return []
        
        # Supported image extensions
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
        
        # Find all image files
        image_files = []
        for ext in supported_extensions:
            image_files.extend(image_dir.glob(f"*{ext}"))
            image_files.extend(image_dir.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"No supported image files found in {image_directory}")
            return []
        
        print(f"Found {len(image_files)} image files to process")
        
        results = []
        for i, image_file in enumerate(image_files, 1):
            print(f"\nProcessing {i}/{len(image_files)}: {image_file.name}")
            
            try:
                # Extract text
                extracted_text = img_extractor.extract_text_from_image(str(image_file))
                
                # Store in database
                document_id = img_extractor.store_document_in_db(
                    image_file.name, 
                    extracted_text, 
                    image_file.stat().st_size, 
                    "image"
                )
                
                if document_id:
                    results.append({
                        'filename': image_file.name,
                        'document_id': document_id,
                        'text_length': len(extracted_text),
                        'success': True
                    })
                    print(f"✓ Successfully processed {image_file.name}")
                else:
                    results.append({
                        'filename': image_file.name,
                        'document_id': None,
                        'text_length': 0,
                        'success': False,
                        'error': 'Database storage failed'
                    })
                    print(f"✗ Failed to store {image_file.name}")
                    
            except Exception as e:
                results.append({
                    'filename': image_file.name,
                    'document_id': None,
                    'text_length': 0,
                    'success': False,
                    'error': str(e)
                })
                print(f"✗ Error processing {image_file.name}: {e}")
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        print(f"\nBatch processing completed: {successful}/{len(results)} files processed successfully")
        
        return results
        
    except Exception as e:
        print(f"Error in batch processing: {e}")
        return []

def example_query_documents():
    """
    Example function showing how to query processed documents from the database
    """
    try:
        img_extractor = load_image_extractor()
        
        # Get all documents
        documents = img_extractor.list_all_documents()
        
        if not documents:
            print("No documents found in database")
            return
        
        print(f"Found {len(documents)} documents in database:")
        print("-" * 80)
        
        for doc in documents:
            print(f"ID: {doc['id']}")
            print(f"Filename: {doc['filename']}")
            print(f"Type: {doc['file_type']}")
            print(f"Size: {doc['file_size']} bytes")
            print(f"Processed: {doc['processed_at']}")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error querying documents: {e}")

def main():
    """
    Main function demonstrating various usage examples
    """
    print("OpenAI Image Text Extraction - Usage Examples")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running this example")
        return
    
    print("\nAvailable examples:")
    print("1. Extract text from a single image")
    print("2. Batch process images in a directory")
    print("3. Query processed documents from database")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                image_path = input("Enter the path to your image file: ").strip()
                if image_path:
                    example_extract_and_store(image_path)
                else:
                    print("Please provide a valid image path")
                    
            elif choice == "2":
                directory_path = input("Enter the path to your image directory: ").strip()
                if directory_path:
                    example_batch_process(directory_path)
                else:
                    print("Please provide a valid directory path")
                    
            elif choice == "3":
                example_query_documents()
                
            elif choice == "4":
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 