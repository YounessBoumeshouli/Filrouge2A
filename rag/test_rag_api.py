import requests
import json
import time

# Test the RAG API - Updated for new port
BASE_URL = "http://localhost:8002"  # Changed from 8001 to 8002
@pytest.fixture
def question():
    return "What is Marrakech famous for?"
def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        print("Make sure the RAG API is running on port 8002")
        return False

def test_query(question):
    """Test query endpoint"""
    try:
        payload = {
            "query": question,
            "k": 5
        }
        
        print(f"\nTesting query: {question}")
        print("Sending request...")
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/query", json=payload)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer'][:200]}...")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Query test failed: {e}")
        return False

def main():
    print("=== RAG API Test ===")
    print(f"Testing API at: {BASE_URL}")
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Make sure the API is running.")
        return
    
    print("✅ Health check passed")
    
    # Test queries
    test_questions = [
        "Quels sont les traitements pour la diarrhée chez l'enfant?",
        "Comment traiter la toux chez l'enfant?",
        "Quels sont les signes de déshydratation?"
    ]
    
    for question in test_questions:
        success = test_query(question)
        if success:
            print("✅ Query test passed")
        else:
            print("❌ Query test failed")
        print("-" * 50)

if __name__ == "__main__":
    main()