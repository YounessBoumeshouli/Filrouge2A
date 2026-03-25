#!/usr/bin/env python3
"""
Test script for the updated Marrakech RAG system
"""

import requests
import json
import time

# Test the RAG API with Marrakech queries
BASE_URL = "http://localhost:8002"

def test_marrakech_queries():
    """Test various Marrakech-related queries"""
    
    test_queries = [
        "Tell me about Jemaa el-Fna",
        "What can I find in Souk Semmarine?",
        "How much do babouches cost?",
        "Where is Bahia Palace and what can I see there?",
        "What are the best souks for carpets?",
        "Tell me about Majorelle Garden",
        "What spices can I buy in Marrakech?",
        "How do I bargain in the souks?",
        "What is the Koutoubia Mosque?",
        "Where can I see traditional metalwork?"
    ]
    
    print("=== Testing Marrakech RAG System ===")
    print(f"API Base URL: {BASE_URL}")
    print()
    
    # Test health first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ RAG API is running")
        else:
            print("❌ RAG API health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to RAG API: {e}")
        print("Make sure the RAG API is running on port 8002")
        return
    
    print("\n" + "="*60)
    print("TESTING MARRAKECH QUERIES")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json={
                "query": query,
                "k": 3
            }, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer provided')
                
                print(f"⏱️  Response time: {end_time - start_time:.2f}s")
                print(f"📝 Answer: {answer[:300]}...")
                if len(answer) > 300:
                    print("    [Answer truncated for display]")
                print("✅ Success")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ If you see detailed answers about Marrakech places, souks, and attractions,")
    print("   the RAG system has been successfully updated!")
    print("❌ If you see medical information or errors, the update may have failed.")

if __name__ == "__main__":
    test_marrakech_queries()