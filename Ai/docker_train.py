#!/usr/bin/env python3
"""
Docker YOLO Training Script
===========================

Optimized YOLO training script for Docker container environment.
"""

import shutil
from pathlib import Path
import torch

# Disable MLflow completely
os.environ['MLFLOW_TRACKING_URI'] = ''
os.environ['MLFLOW_DISABLE'] = '1'
os.environ['MLFLOW_TRACKING_DISABLED'] = '1'

def train_yolo_docker():
    """Train YOLO model in Docker environment"""
    
    print("🐳 YOLO Training in Docker Container")
    print("=" * 50)
    
    try:
        from ultralytics import YOLO
        
        # Check if dataset exists
        dataset_path = Path('/app/data/dataset.yaml')
        if not dataset_path.exists():
            print("❌ Dataset not found at /app/data/dataset.yaml")
            print("Please mount your dataset directory to /app/data")
            return False
        
        print(f"📊 Dataset found: {dataset_path}")
        
        # Check device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️ Using device: {device}")
        
        # Initialize model
        print("🔄 Loading YOLO model...")
        model = YOLO('yolov8n.pt')
        
        # Training parameters
        training_params = {
            'data': str(dataset_path),
            'epochs': 50,
            'imgsz': 640,
            'batch': 8 if device == 'cuda' else 4,
            'device': device,
            'project': '/app/runs/train',
            'name': 'ceramic_docker',
            'exist_ok': True,
            'save': True,
            'verbose': True,
            'plots': True,
            'val': True,
            
            # Augmentation parameters
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 10,
            'translate': 0.1,
            'scale': 0.5,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.1,
            'copy_paste': 0.1,
            
            # Training optimization
            'patience': 20,
            'save_period': 10,
            'workers': 4,
            'seed': 42
        }
        
        print("🚀 Starting training with parameters:")
        for key, value in training_params.items():
            print(f"   {key}: {value}")
        
        # Start training
        print("\n🔥 Training started...")
        model.train(**training_params)
        
        # Save model to mounted volume
        model_save_path = Path('/app/models/ceramic_yolo_trained.pt')
        model_save_path.parent.mkdir(exist_ok=True)
        
        # Find and copy best model
        runs_dir = Path('/app/runs/train')
        train_dirs = [d for d in runs_dir.iterdir() 
                     if d.is_dir() and 'ceramic_docker' in d.name]
        
        if train_dirs:
            latest_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
            best_model = latest_dir / 'weights' / 'best.pt'
            
            if best_model.exists():
                shutil.copy2(best_model, model_save_path)
                print(f"✅ Model saved to: {model_save_path}")
                
                # Also copy training results
                results_dir = Path('/app/models/training_results')
                if results_dir.exists():
                    shutil.rmtree(results_dir)
                shutil.copytree(latest_dir, results_dir)
                print(f"📊 Training results saved to: {results_dir}")
                
                return True
        
        print("⚠️ Training completed but model not found")
        return False
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🐳 Docker YOLO Training Container")
    print("=" * 50)
    
    # Check mounted volumes
    data_dir = Path('/app/data')
    models_dir = Path('/app/models')
    
    print(f"📁 Data directory: {data_dir}")
    print(f"💾 Models directory: {models_dir}")
    
    if data_dir.exists():
        files = list(data_dir.iterdir())
        print(f"📊 Data files: {len(files)}")
        for f in files[:5]:  # Show first 5 files
            print(f"   - {f.name}")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more")
    else:
        print("❌ Data directory not mounted!")
        return
    
    # Create models directory
    models_dir.mkdir(exist_ok=True)
    
    # Start training
    success = train_yolo_docker()
    
    if success:
        print("\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print("📁 Check /app/models/ for trained model")
    else:
        print("\n❌ Training failed!")

if __name__ == "__main__":
    main()