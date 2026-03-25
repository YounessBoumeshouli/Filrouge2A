#!/usr/bin/env python3
"""
Start server and test prediction system
"""

import subprocess
import time
import requests
import json
import base64
import os
import threading

def start_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting FastAPI server...")
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
            cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_prediction_api():
    """Test the prediction API"""
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Find a test image
    test_dirs = [
        os.path.join("..", "Ai", "data", "price", "test"),
        os.path.join("..", "marrakech_dataset")
    ]
    
    test_image_path = None
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for class_name in os.listdir(test_dir):
                class_path = os.path.join(test_dir, class_name)
                if os.path.isdir(class_path):
                    images = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    if images:
                        test_image_path = os.path.join(class_path, images[0])
                        print(f"📸 Using test image: {class_name}/{images[0]}")
                        break
            if test_image_path:
                break
    
    if not test_image_path:
        print("❌ No test image found")
        return
    
    # Read and encode image
    try:
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Test the API
        api_url = "http://localhost:8000/api/price/analyze"
        response = requests.post(api_url, json={"image": image_base64}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction API Test Successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print(f"🎯 Predicted: {result['product_type']} (confidence: {result['confidence']})")
            else:
                print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not responding")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    print("Server Test & Prediction Verification")
    print("=" * 50)
    
    # Start server in background
    server_process = start_server()
    
    if server_process:
        try:
            # Test the API
            test_prediction_api()
            
            print("\n" + "=" * 50)
            print("✅ Test complete! Server is running on http://localhost:8000")
            print("📖 API Documentation: http://localhost:8000/docs")
            print("🛑 Press Ctrl+C to stop the server")
            
            # Keep server running
            server_process.wait()
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
    else:
        print("❌ Could not start server")