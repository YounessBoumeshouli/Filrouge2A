
import os
import torch
from ultralytics import YOLO

# Disable MLflow completely
os.environ['MLFLOW_TRACKING_URI'] = ''
os.environ['MLFLOW_DISABLE'] = '1'

def train_simple():
    try:
        print("Loading YOLO model...")
        model = YOLO('yolov8n.pt')
        
        print("Starting training...")
        results = model.train(
            data='data/ceramic_simple/dataset.yaml',
            epochs=30,
            imgsz=640,
            batch=4,
            device='cpu',
            project='runs/train',
            name='ceramic_simple',
            exist_ok=True,
            save=True,
            verbose=True
        )
        
        print("Training completed!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = train_simple()
    if success:
        print("✅ Training successful!")
    else:
        print("❌ Training failed!")
