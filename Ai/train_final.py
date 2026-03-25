import os
import sys
from pathlib import Path
from ultralytics import YOLO

# Disable MLflow by removing the callback
def disable_mlflow():
    try:
        from ultralytics.utils import callbacks
        # Remove MLflow callback if it exists
        if hasattr(callbacks, 'mlflow'):
            delattr(callbacks, 'mlflow')
        
        # Also try to disable it in the callbacks module
        import ultralytics.utils.callbacks.mlflow as mlflow_cb
        # Replace all callback functions with dummy functions
        for attr_name in dir(mlflow_cb):
            if callable(getattr(mlflow_cb, attr_name)) and not attr_name.startswith('_'):
                setattr(mlflow_cb, attr_name, lambda *args, **kwargs: None)
    except:
        pass

def train_yolo():
    # Disable MLflow
    disable_mlflow()
    
    # Set environment variables
    os.environ['MLFLOW_TRACKING_URI'] = ''
    os.environ['DISABLE_MLFLOW'] = '1'
    
    # Configuration
    dataset_yaml = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\custom_dataset\dataset.yaml"
    model_save_path = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\custom_yolo_model.pt"
    
    print("Starting YOLO training...")
    print(f"Dataset: {dataset_yaml}")
    print(f"Model save path: {model_save_path}")
    
    try:
        # Initialize model
        model = YOLO('yolov8n.pt')
        
        # Train with minimal settings
        results = model.train(
            data=dataset_yaml,
            epochs=20,  # Reduced for faster training
            imgsz=640,
            batch=4,    # Smaller batch size
            device='cpu',
            project='runs/train',
            name='ceramic_model',
            exist_ok=True,
            verbose=False,  # Reduce output
            plots=False,    # Disable plots
            save=True
        )
        
        # Copy model to desired location
        best_model = Path('runs/train/ceramic_model/weights/best.pt')
        if best_model.exists():
            import shutil
            Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(best_model, model_save_path)
            print(f"✅ Model saved to: {model_save_path}")
            return True
        else:
            print("❌ Training completed but model not found")
            return False
            
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

if __name__ == "__main__":
    success = train_yolo()
    if success:
        print("\n🎉 Training completed successfully!")
    else:
        print("\n💥 Training failed!")