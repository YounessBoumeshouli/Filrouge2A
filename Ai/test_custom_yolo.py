#!/usr/bin/env python3
"""
Custom YOLO Model Inference Script
=================================

Test the trained custom YOLO model on new images.
"""

import cv2
import torch
from ultralytics import YOLO
from pathlib import Path
import numpy as np

def test_model(model_path, test_image_path, output_dir="results"):
    """Test the trained model on an image"""
    
    # Load the trained model
    model = YOLO(model_path)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Run inference
    results = model(test_image_path)
    
    # Process results
    for i, result in enumerate(results):
        # Get image
        img = result.orig_img.copy()
        
        # Draw bounding boxes
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            
            for box, conf, cls in zip(boxes, confidences, classes):
                x1, y1, x2, y2 = box.astype(int)
                
                # Draw rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add label
                label = f"{model.names[int(cls)]}: {conf:.2f}"
                cv2.putText(img, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save result
        output_path = output_dir / f"result_{i}.jpg"
        cv2.imwrite(str(output_path), img)
        print(f"Result saved to: {output_path}")
    
    return results

def main():
    # Configuration
    MODEL_PATH = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\custom_yolo_model.pt"
    TEST_IMAGE = r"c:\Users\boume\Briefs\Filrouge2A\images\product_1_Ceramic Vase\image_1.jpg"
    OUTPUT_DIR = r"c:\Users\boume\Briefs\Filrouge2A\Ai\inference_results"
    
    print("Testing custom YOLO model...")
    print(f"Model: {MODEL_PATH}")
    print(f"Test image: {TEST_IMAGE}")
    
    # Check if model exists
    if not Path(MODEL_PATH).exists():
        print(f"Error: Model not found at {MODEL_PATH}")
        print("Please train the model first using train_custom_yolo.py")
        return
    
    # Check if test image exists
    if not Path(TEST_IMAGE).exists():
        print(f"Error: Test image not found at {TEST_IMAGE}")
        return
    
    # Run inference
    results = test_model(MODEL_PATH, TEST_IMAGE, OUTPUT_DIR)
    
    print("Inference completed!")
    print(f"Results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()