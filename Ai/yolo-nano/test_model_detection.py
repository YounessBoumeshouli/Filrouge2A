#!/usr/bin/env python3
"""
Test YOLO Model Detection
========================

Direct test of the YOLO model to see what it's actually detecting.
"""

import requests
import base64
import json
from pathlib import Path

def test_model_detection():
    """Test the model with actual images"""
    
    api_url = "http://localhost:8001"
    
    print("🧪 Testing YOLO Model Detection...")
    print("=" * 60)
    
    # Test with validation images
    val_images_path = Path("data/yolo_dataset/val/images")
    test_images = list(val_images_path.glob("*.jpg"))[:5]  # Test first 5 images
    
    if not test_images:
        print("❌ No validation images found!")
        return
    
    print(f"📁 Found {len(test_images)} test images")
    
    for i, image_path in enumerate(test_images):
        print(f"\n🖼️  Testing Image {i+1}: {image_path.name}")
        print("-" * 40)
        
        try:
            # Load and encode image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Test YOLO detection
            detection_request = {
                "image": f"data:image/jpeg;base64,{base64_image}",
                "conf_threshold": 0.1,  # Lower threshold to see more detections
                "iou_threshold": 0.45
            }
            
            response = requests.post(
                f"{api_url}/api/yolo/detect",
                json=detection_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ API Response: {data.get('success', False)}")
                print(f"📊 Detections: {len(data.get('detections', []))}")
                
                # Show all detections
                detections = data.get('detections', [])
                if detections:
                    print("🎯 Detected Objects:")
                    for j, det in enumerate(detections):
                        print(f"   {j+1}. {det['class_name']}: {det['confidence']:.3f}")
                        print(f"      BBox: [{det['bbox'][0]:.1f}, {det['bbox'][1]:.1f}, {det['bbox'][2]:.1f}, {det['bbox'][3]:.1f}]")
                else:
                    print("❌ No objects detected")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {image_path.name}: {e}")
    
    # Test model status
    print(f"\n🔍 Model Status Check...")
    print("-" * 40)
    try:
        response = requests.get(f"{api_url}/api/debug/model-status")
        if response.status_code == 200:
            data = response.json()
            print(f"Model Loaded: {data.get('model_loaded', False)}")
            print(f"Device: {data.get('device', 'unknown')}")
            print(f"Classes: {data.get('classes', [])}")
            print(f"Training Mode: {data.get('model_training', 'unknown')}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")

if __name__ == "__main__":
    test_model_detection()