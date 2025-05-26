#!/usr/bin/env python3
"""
test_image_extraction.py

Test script for the image text extraction functionality.
This script tests the database connection and helper functions.
"""

import sys
import os

# Add the db directory to the path so we can import database utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

from database import DatabaseConnection

def test_database_connection():
    """Test the database connection"""
    print("Testing database connection...")
    db = DatabaseConnection()
    
    if db.connect():
        print("✓ Database connection successful")
        
        # Test basic query
        try:
            result = db.execute_query("SELECT COUNT(*) as count FROM documents")
            if result:
                count = result[0]['count']
                print(f"✓ Found {count} documents in database")
            else:
                print("✓ Documents table exists but query returned no results")
        except Exception as e:
            print(f"✗ Error querying documents table: {e}")
        
        db.disconnect()
        return True
    else:
        print("✗ Database connection failed")
        return False

def test_openai_api_key():
    """Test if OpenAI API key is set"""
    print("Testing OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        # Don't print the full key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ OpenAI API key is set: {masked_key}")
        return True
    else:
        print("✗ OpenAI API key is not set")
        print("  Please set the OPENAI_API_KEY environment variable")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        import psycopg2
        print("✓ psycopg2 module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import psycopg2: {e}")
        return False
    
    try:
        # Import the module by adding current directory to path
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import the main script as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_img_db", 
                                                     os.path.join(current_dir, "openai-img-db.py"))
        if spec and spec.loader:
            openai_img_db = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(openai_img_db)
            print("✓ Image extraction functions imported successfully")
        else:
            print("✗ Could not load openai-img-db.py module")
            return False
    except Exception as e:
        print(f"✗ Failed to import image extraction functions: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("OpenAI Image Text Extraction - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection Test", test_database_connection),
        ("OpenAI API Key Test", test_openai_api_key),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The system is ready for image text extraction.")
    else:
        print("✗ Some tests failed. Please check the configuration and dependencies.")
        sys.exit(1)

if __name__ == "__main__":
    main() 