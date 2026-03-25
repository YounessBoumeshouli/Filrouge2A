#!/usr/bin/env python3
"""
test_api_integration.py
Test API integration for the price classifier
"""

import os
import sys
import json
import base64
from io import BytesIO
from PIL import Image
import tensorflow as tf
import numpy as np

class PriceClassifierAPI:
    def __init__(self, model_path=None, classes_path=None):
        # Get absolute paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "..", "models")
        
        if model_path is None:
            model_path = os.path.join(models_dir, "price_efficientnet_finetuned.h5")
            if not os.path.exists(model_path):
                model_path = os.path.join(models_dir, "price_efficientnet.h5")
        
        if classes_path is None:
            classes_path = os.path.join(models_dir, "price_class_indices.json")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not os.path.exists(classes_path):
            raise FileNotFoundError(f"Classes file not found at {classes_path}")
            
        self.model = tf.keras.models.load_model(model_path)
        with open(classes_path, 'r') as f:
            self.class_indices = json.load(f)
        
        self.img_size = 224
    
    def predict_from_base64(self, image_base64):
        """Predict from base64 encoded image (API format)"""
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            img = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Preprocess - match training preprocessing
            img = img.resize((self.img_size, self.img_size))
            img_array = np.array(img, dtype=np.float32) / 255.0  # Same as training
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            confidence = float(np.max(predictions))
            class_idx = int(np.argmax(predictions))
            
            return {
                "success": True,
                "product_type": self.class_indices[str(class_idx)],
                "confidence": round(confidence, 3),
                "all_predictions": {
                    self.class_indices[str(i)]: round(float(predictions[0][i]), 3)
                    for i in range(len(self.class_indices))
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict_from_file(self, file_path):
        """Predict from file path"""
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return self.predict_from_base64(image_base64)
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def test_api():
    """Test the API integration"""
    api = PriceClassifierAPI()
    print("Price Classifier API Test")
    print("=" * 50)
    
    # Test with different product types
    test_dir = "../data/price/test"
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return
    
    for class_name in sorted(os.listdir(test_dir)):
        class_path = os.path.join(test_dir, class_name)
        if os.path.isdir(class_path):
            images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_image = os.path.join(class_path, images[0])
                result = api.predict_from_file(test_image)
                
                print(f"\nTesting: {class_name}")
                print(f"Image: {images[0]}")
                if result["success"]:
                    print(f"Predicted: {result['product_type']} ({result['confidence']})")
                    print("Top 3 predictions:")
                    sorted_preds = sorted(result['all_predictions'].items(), 
                                        key=lambda x: x[1], reverse=True)[:3]
                    for i, (prod, conf) in enumerate(sorted_preds, 1):
                        print(f"  {i}. {prod}: {conf}")
                else:
                    print(f"Error: {result['error']}")

def simulate_api_request(image_path):
    """Simulate an API request"""
    api = PriceClassifierAPI()
    
    print("Simulating API Request")
    print("=" * 30)
    print(f"POST /api/price/analyze")
    print(f"Image: {os.path.basename(image_path)}")
    
    result = api.predict_from_file(image_path)
    
    print("\nAPI Response:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        simulate_api_request(sys.argv[1])
    else:
        test_api()