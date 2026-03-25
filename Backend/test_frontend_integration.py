#!/usr/bin/env python3
"""
test_frontend_integration.py
Test the complete frontend-backend-model integration
"""

import requests
import base64
import json
import os

def test_api_endpoint():
    """Test the FastAPI endpoint with a sample image"""
    
    # Test image path (use one from the test set)
    test_image_path = os.path.join("..", "Ai", "data", "price", "test", "spices", "000004.jpg")
    
    # Try alternative paths if the first doesn't exist
    if not os.path.exists(test_image_path):
        # Try from current directory
        test_image_path = os.path.join("Ai", "data", "price", "test", "spices", "000004.jpg")
        
    if not os.path.exists(test_image_path):
        # Find any test image
        test_dir = os.path.join("..", "Ai", "data", "price", "test")
        if not os.path.exists(test_dir):
            test_dir = os.path.join("Ai", "data", "price", "test")
            
        if os.path.exists(test_dir):
            for class_name in os.listdir(test_dir):
                class_path = os.path.join(test_dir, class_name)
                if os.path.isdir(class_path):
                    images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    if images:
                        test_image_path = os.path.join(class_path, images[0])
                        break
    
    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        return
    
    # Read and encode image
    with open(test_image_path, 'rb') as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Test the API endpoint
    api_url = "http://localhost:8000/api/price/analyze"
    
    try:
        # Test with base64 data
        response = requests.post(api_url, json={"image": image_base64})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Integration Test Successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Validate response format
            if result.get("success") and "product_type" in result and "confidence" in result:
                print("✅ Response format is correct for frontend integration")
            else:
                print("⚠️  Response format may need adjustment for frontend")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test Error: {e}")

def test_frontend_format():
    """Test the expected frontend format"""
    
    # Expected frontend format
    expected_format = {
        "success": True,
        "product_type": "spices",
        "confidence": 0.135,
        "all_predictions": {
            "argan": 0.124,
            "crafts": 0.130,
            "jewelry": 0.102,
            "lanterns": 0.130,
            "leather": 0.131,
            "price_tags": 0.115,
            "spices": 0.135,
            "textiles": 0.132
        }
    }
    
    print("Expected Frontend Format:")
    print(json.dumps(expected_format, indent=2))

if __name__ == "__main__":
    print("Testing Frontend-Backend-Model Integration")
    print("=" * 50)
    
    print("\n1. Testing API Endpoint...")
    test_api_endpoint()
    
    print("\n2. Expected Frontend Format:")
    test_frontend_format()
    
    print("\n" + "=" * 50)
    print("Integration Test Complete!")
    print("\nTo test the full stack:")
    print("1. Start the FastAPI backend: uvicorn main:app --reload")
    print("2. Start the React frontend: npm start")
    print("3. Upload an image in the PriceHelper page")