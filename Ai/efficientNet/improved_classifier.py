#!/usr/bin/env python3
"""
Improved prediction system with confidence thresholding and fallback logic
"""

import os
import sys
import json
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf

class ImprovedPriceClassifier:
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
        self.confidence_threshold = 0.3  # Minimum confidence for reliable prediction
        
    def predict_from_base64(self, image_base64):
        """Predict from base64 encoded image with improved confidence handling"""
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            img = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Preprocess - match training preprocessing
            img = img.resize((self.img_size, self.img_size))
            img_array = np.array(img, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            confidence = float(np.max(predictions))
            class_idx = int(np.argmax(predictions))
            
            # Get all predictions sorted by confidence
            all_predictions = {
                self.class_indices[str(i)]: round(float(predictions[0][i]), 3)
                for i in range(len(self.class_indices))
            }
            
            # Check if prediction is reliable
            if confidence < self.confidence_threshold:
                # Low confidence - provide top 3 suggestions instead
                sorted_preds = sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)
                top_3 = sorted_preds[:3]
                
                return {
                    "success": True,
                    "product_type": "uncertain",
                    "confidence": round(confidence, 3),
                    "message": f"Low confidence prediction. Top possibilities: {', '.join([f'{p[0]} ({p[1]})' for p in top_3])}",
                    "top_suggestions": [{"category": p[0], "confidence": p[1]} for p in top_3],
                    "all_predictions": all_predictions
                }
            else:
                # High confidence prediction
                return {
                    "success": True,
                    "product_type": self.class_indices[str(class_idx)],
                    "confidence": round(confidence, 3),
                    "all_predictions": all_predictions
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

# For backward compatibility
class PriceClassifierAPI(ImprovedPriceClassifier):
    pass

def test_improved_classifier():
    """Test the improved classifier"""
    try:
        classifier = ImprovedPriceClassifier()
        
        # Find test images
        test_dirs = [
            os.path.join("..", "..", "Ai", "data", "price", "test"),
            os.path.join("..", "data", "price", "test"),
            "../data/price/test"
        ]
        
        test_dir = None
        for td in test_dirs:
            if os.path.exists(td):
                test_dir = td
                break
                
        if not test_dir:
            print("❌ Test directory not found")
            return
        
        print("🔍 Testing Improved Classifier")
        print("=" * 50)
        
        # Test one image from each class
        for class_name in sorted(os.listdir(test_dir)):
            class_path = os.path.join(test_dir, class_name)
            if os.path.isdir(class_path):
                images = [f for f in os.listdir(class_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    test_image = os.path.join(class_path, images[0])
                    result = classifier.predict_from_file(test_image)
                    
                    print(f"\n📂 {class_name}:")
                    if result["success"]:
                        if result["product_type"] == "uncertain":
                            print(f"  ⚠️  {result['message']}")
                        else:
                            status = "✅" if result["product_type"] == class_name else "❌"
                            print(f"  {status} Predicted: {result['product_type']} ({result['confidence']})")
                    else:
                        print(f"  ❌ Error: {result['error']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_improved_classifier()