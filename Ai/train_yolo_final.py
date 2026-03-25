#!/usr/bin/env python3
"""
Final YOLO Training Solution
===========================

A robust solution that completely bypasses MLflow issues and trains YOLO successfully.
"""

import os
import sys
import shutil
import yaml
import random
from pathlib import Path
from PIL import Image
import subprocess

def completely_disable_mlflow():
    """Completely disable MLflow tracking"""
    
    # Set all possible environment variables
    mlflow_vars = [
        'MLFLOW_TRACKING_URI',
        'MLFLOW_DISABLE',
        'MLFLOW_TRACKING_DISABLED',
        'DISABLE_MLFLOW',
        'MLFLOW_EXPERIMENT_NAME',
        'MLFLOW_RUN_ID'
    ]
    
    for var in mlflow_vars:
        os.environ[var] = ''
    
    # Try to disable MLflow callbacks
    try:
        import ultralytics.utils.callbacks.mlflow as mlflow_cb
        # Replace all functions with dummy functions
        for attr in dir(mlflow_cb):
            if callable(getattr(mlflow_cb, attr)) and not attr.startswith('_'):
                setattr(mlflow_cb, attr, lambda *args, **kwargs: None)
    except:
        pass

def prepare_minimal_dataset(images_root, output_dir):
    """Prepare a minimal dataset for training"""
    
    print("🔄 Preparing dataset...")
    
    images_root = Path(images_root)
    output_dir = Path(output_dir)
    
    # Create directories
    for split in ['train', 'val']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Find all valid pairs
    all_pairs = []
    classes = []
    
    product_folders = [f for f in images_root.iterdir() 
                      if f.is_dir() and f.name.startswith('product_')]
    
    for product_folder in product_folders:
        parts = product_folder.name.split('_', 2)
        if len(parts) < 2:
            continue
            
        product_id = parts[1]
        class_name = parts[2] if len(parts) > 2 else f"Product_{product_id}"
        
        if class_name not in classes:
            classes.append(class_name)
        class_id = classes.index(class_name)
        
        # Find labels folder
        label_folder = None
        for folder in images_root.iterdir():
            if folder.is_dir() and f'labels_product_{product_id}_' in folder.name:
                label_folder = folder
                break
        
        if not label_folder:
            continue
        
        # Collect pairs
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        for img_file in product_folder.iterdir():
            if img_file.suffix.lower() in image_extensions:
                label_file = label_folder / f"{img_file.stem}.txt"
                if label_file.exists():
                    all_pairs.append((img_file, label_file, class_id))
    
    print(f"📊 Found {len(all_pairs)} pairs, {len(classes)} classes")
    
    # Split and copy files
    random.shuffle(all_pairs)
    split_idx = int(0.8 * len(all_pairs))
    train_pairs = all_pairs[:split_idx]
    val_pairs = all_pairs[split_idx:]
    
    # Copy files
    for pairs, split in [(train_pairs, 'train'), (val_pairs, 'val')]:
        for i, (img_file, label_file, class_id) in enumerate(pairs):
            # Copy image
            dst_img = output_dir / 'images' / split / f"{split}_{i:04d}.jpg"
            img = Image.open(img_file)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(dst_img, 'JPEG', quality=90)
            
            # Copy label
            dst_label = output_dir / 'labels' / split / f"{split}_{i:04d}.txt"
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            with open(dst_label, 'w') as f:
                for line in lines:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 5:
                            parts[0] = str(class_id)
                            f.write(' '.join(parts) + '\n')
    
    # Create dataset.yaml
    dataset_config = {
        'path': str(output_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes),
        'names': classes
    }
    
    with open(output_dir / 'dataset.yaml', 'w') as f:
        yaml.dump(dataset_config, f)
    
    print(f"✅ Dataset ready: {len(train_pairs)} train, {len(val_pairs)} val")
    return output_dir / 'dataset.yaml', classes

def train_with_subprocess(dataset_yaml, model_path, epochs=50):
    """Train using subprocess to completely isolate from MLflow"""
    
    print(f"🚀 Training with subprocess isolation...")
    
    # Create a temporary training script
    train_script = Path("temp_train.py")
    
    script_content = f'''
import os
import sys
from pathlib import Path

# Completely disable MLflow
os.environ['MLFLOW_TRACKING_URI'] = ''
os.environ['MLFLOW_DISABLE'] = '1'

try:
    from ultralytics import YOLO
    
    # Initialize model
    model = YOLO('yolov8n.pt')
    
    # Train with minimal parameters
    results = model.train(
        data=r"{dataset_yaml}",
        epochs={epochs},
        imgsz=640,
        batch=4,
        device='cpu',
        project='runs/train',
        name='ceramic_final',
        exist_ok=True,
        save=True,
        verbose=False,
        plots=False
    )
    
    print("Training completed successfully!")
    
except Exception as e:
    print(f"Training error: {{e}}")
    sys.exit(1)
'''
    
    with open(train_script, 'w') as f:
        f.write(script_content)
    
    try:
        # Run training in subprocess
        env = os.environ.copy()
        env['MLFLOW_TRACKING_URI'] = ''
        env['MLFLOW_DISABLE'] = '1'
        
        result = subprocess.run([
            sys.executable, str(train_script)
        ], env=env, capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            # Find and copy trained model
            runs_dir = Path('runs/train')
            if runs_dir.exists():
                train_dirs = [d for d in runs_dir.iterdir() 
                             if d.is_dir() and 'ceramic_final' in d.name]
                if train_dirs:
                    latest_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
                    best_model = latest_dir / 'weights' / 'best.pt'
                    
                    if best_model.exists():
                        model_path = Path(model_path)
                        model_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(best_model, model_path)
                        print(f"✅ Model saved to: {model_path}")
                        return True
        
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ Training timed out")
        return False
    except Exception as e:
        print(f"❌ Subprocess error: {e}")
        return False
    finally:
        # Clean up
        if train_script.exists():
            train_script.unlink()

def create_simple_trainer():
    """Create a very simple training script that avoids all MLflow issues"""
    
    script_content = '''
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
'''
    
    with open("simple_trainer.py", 'w') as f:
        f.write(script_content)
    
    print("📝 Created simple_trainer.py")

def main():
    # Configuration
    IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"
    OUTPUT_DIR = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\ceramic_simple"
    MODEL_PATH = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\ceramic_yolo_final.pt"
    
    print("🏺 Final YOLO Training Solution")
    print("=" * 50)
    
    try:
        # Disable MLflow completely
        completely_disable_mlflow()
        
        # Prepare dataset
        print("\n📊 STEP 1: PREPARING DATASET")
        dataset_yaml, classes = prepare_minimal_dataset(IMAGES_ROOT, OUTPUT_DIR)
        
        # Try training with subprocess
        print("\n🚀 STEP 2: TRAINING MODEL")
        success = train_with_subprocess(dataset_yaml, MODEL_PATH, epochs=30)
        
        if success:
            print(f"\n🎉 TRAINING SUCCESSFUL!")
            print(f"💾 Model: {MODEL_PATH}")
            print(f"🏷️ Classes ({len(classes)}):")
            for i, cls in enumerate(classes):
                print(f"   {i}: {cls}")
        else:
            print(f"\n❌ Training failed with subprocess method")
            print(f"📝 Creating simple trainer script as backup...")
            create_simple_trainer()
            print(f"💡 Try running: python simple_trainer.py")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()