#!/usr/bin/env python3
"""
test_model.py
Test the trained price classifier model
"""

import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf

def load_model_and_classes():
    """Load the trained model and class indices"""
    model_path = "../models/price_efficientnet_finetuned.h5"
    classes_path = "../models/price_class_indices.json"
    
    if not os.path.exists(model_path):
        model_path = "../models/price_efficientnet.h5"
        print("Using Phase 1 model (fine-tuned model not found)")
    
    model = tf.keras.models.load_model(model_path)
    
    with open(classes_path, 'r') as f:
        class_indices = json.load(f)
    
    return model, class_indices

def preprocess_image(image_path, img_size=224):
    """Preprocess image for prediction"""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((img_size, img_size))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_image(model, class_indices, image_path):
    """Predict product category for an image"""
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array, verbose=0)
    
    confidence = float(np.max(predictions))
    class_idx = int(np.argmax(predictions))
    class_name = class_indices[str(class_idx)]
    
    # Get top 3 predictions
    top_indices = np.argsort(predictions[0])[::-1][:3]
    top_predictions = []
    for idx in top_indices:
        top_predictions.append({
            'class': class_indices[str(idx)],
            'confidence': float(predictions[0][idx])
        })
    
    return {
        'predicted_class': class_name,
        'confidence': confidence,
        'top_predictions': top_predictions
    }

def test_random_images():
    """Test with random images from test set"""
    test_dir = "../data/price/test"
    if not os.path.exists(test_dir):
        print(f"Test directory not found: {test_dir}")
        return
    
    model, class_indices = load_model_and_classes()
    print(f"Model loaded. Classes: {list(class_indices.values())}")
    print("-" * 60)
    
    # Test one image from each class
    for class_name in os.listdir(test_dir):
        class_path = os.path.join(test_dir, class_name)
        if os.path.isdir(class_path):
            images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_image = os.path.join(class_path, images[0])
                result = predict_image(model, class_indices, test_image)
                
                print(f"True class: {class_name}")
                print(f"Predicted: {result['predicted_class']} ({result['confidence']:.3f})")
                print("Top 3 predictions:")
                for i, pred in enumerate(result['top_predictions'], 1):
                    print(f"  {i}. {pred['class']}: {pred['confidence']:.3f}")
                print("-" * 60)

def test_single_image(image_path):
    """Test a single image"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    model, class_indices = load_model_and_classes()
    result = predict_image(model, class_indices, image_path)
    
    print(f"Image: {image_path}")
    print(f"Predicted: {result['predicted_class']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print("\nTop 3 predictions:")
    for i, pred in enumerate(result['top_predictions'], 1):
        print(f"  {i}. {pred['class']}: {pred['confidence']:.3f}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific image
        test_single_image(sys.argv[1])
    else:
        # Test random images from test set
        test_random_images()