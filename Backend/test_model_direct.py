#!/usr/bin/env python3
"""
Direct model test to verify prediction functionality
"""

import os
import sys
import json

# Add AI path
ai_path = os.path.join(os.path.dirname(__file__), '..', 'Ai', 'efficientNet')
sys.path.append(ai_path)

def test_model_loading():
    """Test if the model can be loaded correctly"""
    try:
        from test_api_integration import PriceClassifierAPI
        
        print("🔄 Loading model...")
        api = PriceClassifierAPI()
        print("✅ Model loaded successfully!")
        
        # Check class indices
        print(f"📋 Available classes: {list(api.class_indices.values())}")
        
        return api
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None

def test_prediction(api):
    """Test prediction with available test images"""
    test_dirs = [
        os.path.join("..", "Ai", "data", "price", "test"),
        os.path.join("Ai", "data", "price", "test"),
        os.path.join("..", "marrakech_dataset")
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"🔍 Found test directory: {test_dir}")
            
            # Find first available image
            for class_name in os.listdir(test_dir):
                class_path = os.path.join(test_dir, class_name)
                if os.path.isdir(class_path):
                    images = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    if images:
                        test_image = os.path.join(class_path, images[0])
                        print(f"🖼️  Testing with: {class_name}/{images[0]}")
                        
                        result = api.predict_from_file(test_image)
                        
                        if result["success"]:
                            print("✅ Prediction successful!")
                            print(f"   Predicted: {result['product_type']}")
                            print(f"   Confidence: {result['confidence']}")
                            print("   Top 3 predictions:")
                            sorted_preds = sorted(result['all_predictions'].items(), 
                                                key=lambda x: x[1], reverse=True)[:3]
                            for i, (prod, conf) in enumerate(sorted_preds, 1):
                                print(f"     {i}. {prod}: {conf}")
                        else:
                            print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
                        
                        return result
            
    print("❌ No test images found")
    return None

if __name__ == "__main__":
    print("Direct Model Test")
    print("=" * 50)
    
    # Test model loading
    api = test_model_loading()
    
    if api:
        print("\n" + "=" * 50)
        # Test prediction
        test_prediction(api)
    
    print("\n" + "=" * 50)
    print("Test complete!")