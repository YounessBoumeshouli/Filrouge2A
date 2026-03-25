#!/usr/bin/env python3
"""
Test script to verify all imports work correctly for the RAG API
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

def test_imports():
    print("Testing imports...")
    
    try:
        print("✓ Testing FastAPI...")
        from fastapi import FastAPI
        
        print("✓ Testing Pydantic...")
        from pydantic import BaseModel
        
        print("✓ Testing core exceptions...")
        from app.core.exceptions import AppException, app_exception_handler, global_exception_handler
        
        print("✓ Testing assistant service...")
        from app.services.assistant_service import generate
        
        print("✓ Testing retriever...")
        from app.rag.retriever import hybrid_search
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_data_files():
    print("\nTesting data files...")
    
    data_dir = os.path.join('backend', 'app', 'data')
    
    # Check text chunks
    text_chunks_path = os.path.join(data_dir, 'text_chunks.json')
    if os.path.exists(text_chunks_path):
        print("✓ text_chunks.json found")
    else:
        print("❌ text_chunks.json not found")
        return False
    
    # Check chroma db
    chroma_db_path = os.path.join(data_dir, 'chroma_db')
    if os.path.exists(chroma_db_path):
        print("✓ chroma_db directory found")
    else:
        print("❌ chroma_db directory not found")
        return False
    
    print("✅ All data files found!")
    return True

if __name__ == "__main__":
    print("=== RAG API Import Test ===")
    
    imports_ok = test_imports()
    data_ok = test_data_files()
    
    if imports_ok and data_ok:
        print("\n🎉 All tests passed! RAG API should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")