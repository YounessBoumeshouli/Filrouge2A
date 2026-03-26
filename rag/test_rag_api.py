import requests

# import json
import time
import pytest

# Test the RAG API - Updated for new port
BASE_URL = "http://localhost:8002"  # Changed from 8001 to 8002



def is_server_running():
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        return True
    except Exception:
        return False

pytestmark = pytest.mark.skipif(
    not is_server_running(),
    reason="RAG API server not running on port 8002"
)

@pytest.fixture
def question():
    return "What is Marrakech famous for?"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "health" in data.get("status", "")



def test_query(question):
    """Test query endpoint"""
    payload = {"query": question, "k": 5}

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/query", json=payload)
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 10  # should respond within 10 seconds

    result = response.json()
    assert "answer" in result
    assert len(result["answer"]) > 0


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
        "Quels sont les signes de déshydratation?",
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
