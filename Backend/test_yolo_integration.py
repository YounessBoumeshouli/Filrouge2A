"""
Test YOLO-Nano Backend Integration
"""

import requests
import base64
import json
from pathlib import Path

def test_yolo_endpoints():
    """Test all YOLO endpoints"""
    base_url = "http://localhost:8000/api/yolo"
    
    print("🧪 Testing YOLO-Nano Backend Integration")
    print("=" * 50)
    
    # Test 1: Model Status
    print("\n1. Testing Model Status...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Model Status: {status}")
            print(f"  - Model Loaded: {status.get('model_loaded', False)}")
            print(f"  - Device: {status.get('device', 'unknown')}")
            print(f"  - Classes: {status.get('classes', 0)}")
        else:
            print(f"✗ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Status check error: {e}")
    
    # Test 2: Get Classes
    print("\n2. Testing Get Classes...")
    try:
        response = requests.get(f"{base_url}/classes")
        if response.status_code == 200:
            classes = response.json()
            print(f"✓ Classes Retrieved:")
            print(f"  - Total: {classes.get('total_classes', 0)}")
            print(f"  - Monuments: {len(classes.get('monuments', []))}")
            print(f"  - Products: {len(classes.get('products', []))}")
        else:
            print(f"✗ Classes retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Classes retrieval error: {e}")
    
    # Test 3: Detection with Sample Image
    print("\n3. Testing Object Detection...")
    
    # Create a simple test image (you can replace with actual image)
    test_image_path = Path(__file__).parent / "test_image.jpg"
    
    if not test_image_path.exists():
        print("⚠ No test image found. Creating a placeholder...")
        # You would need to add a test image here
        print("  Please add a test image at:", test_image_path)
        return
    
    try:
        # Read and encode image
        with open(test_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Test detection
        payload = {
            "image": f"data:image/jpeg;base64,{image_data}",
            "conf_threshold": 0.25,
            "iou_threshold": 0.45
        }
        
        response = requests.post(f"{base_url}/detect", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Detection successful:")
            print(f"  - Objects found: {len(result.get('detections', []))}")
            for i, det in enumerate(result.get('detections', [])[:3]):  # Show first 3
                print(f"    {i+1}. {det.get('class_name', 'unknown')} "
                      f"({det.get('confidence', 0):.2f}) "
                      f"[{det.get('category', 'unknown')}]")
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"✗ Detection failed: {response.status_code} - {error_detail}")
            
    except FileNotFoundError:
        print("⚠ Test image not found")
    except Exception as e:
        print(f"✗ Detection error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def create_sample_request():
    """Create a sample request for frontend testing"""
    sample_request = {
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...",  # Truncated
        "conf_threshold": 0.25,
        "iou_threshold": 0.45
    }
    
    print("\n📝 Sample Frontend Request:")
    print("```javascript")
    print("const response = await fetch('http://localhost:8000/api/yolo/detect', {")
    print("  method: 'POST',")
    print("  headers: { 'Content-Type': 'application/json' },")
    print("  body: JSON.stringify({")
    print(f"    image: '{sample_request['image'][:50]}...',")
    print(f"    conf_threshold: {sample_request['conf_threshold']},")
    print(f"    iou_threshold: {sample_request['iou_threshold']}")
    print("  })")
    print("});")
    print("```")

if __name__ == "__main__":
    test_yolo_endpoints()
    create_sample_request()