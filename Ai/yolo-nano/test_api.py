#!/usr/bin/env python3
"""
Test YOLO-Nano API Server
=========================

Test the API server to make sure it works correctly.
"""

import requests
import base64
import json
from pathlib import Path

def test_api_server():
    """Test the YOLO-Nano API server"""
    
    api_url = "http://localhost:8000"
    
    print("🧪 Testing YOLO-Nano API Server...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{api_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Model loaded: {data.get('model_loaded', False)}")
            print(f"   Device: {data.get('device', 'unknown')}")
            print(f"   Classes: {len(data.get('classes', []))}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("   Make sure the server is running: python yolo_api_server.py")
        return False
    
    # Test 2: Get classes
    try:
        response = requests.get(f"{api_url}/api/yolo/classes")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Classes endpoint: {data.get('num_classes', 0)} classes")
            print(f"   Classes: {data.get('classes', [])}")
        else:
            print(f"❌ Classes endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Classes endpoint error: {e}")
    
    # Test 3: Model info
    try:
        response = requests.get(f"{api_url}/api/yolo/model-info")
        if response.status_code == 200:
            data = response.json()
            print("✅ Model info endpoint")
            if 'total_params' in data:
                print(f"   Parameters: {data['total_params']:,}")
                print(f"   Model size: {data.get('model_size_mb', 0):.2f} MB")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")
    
    # Test 4: Detection with dummy image (if we have a test image)
    test_image_path = "data/yolo_dataset/val/images"
    test_images = list(Path(test_image_path).glob("*.jpg"))
    
    if test_images:
        try:
            # Load first test image
            image_path = test_images[0]
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Encode to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Make detection request
            detection_request = {
                "image": f"data:image/jpeg;base64,{base64_image}",
                "conf_threshold": 0.25,
                "iou_threshold": 0.45
            }
            
            response = requests.post(
                f"{api_url}/api/yolo/detect",
                json=detection_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Detection test passed")
                print(f"   Success: {data.get('success', False)}")
                print(f"   Detections: {len(data.get('detections', []))}")
                
                # Show first few detections
                for i, det in enumerate(data.get('detections', [])[:3]):
                    print(f"   Detection {i+1}: {det['class_name']} ({det['confidence']:.3f})")
                    
            else:
                print(f"❌ Detection test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Detection test error: {e}")
    else:
        print("⚠️  No test images found - skipping detection test")
    
    print("\n🎉 API testing completed!")
    return True

if __name__ == "__main__":
    test_api_server()