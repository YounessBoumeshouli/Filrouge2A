#!/usr/bin/env python3
"""
Simple YOLO Training Script - No MLflow
======================================

Train YOLO model on custom dataset without MLflow tracking.
"""

import os
import shutil
import yaml
from pathlib import Path
import torch
import random

def prepare_dataset(images_root, output_dir):
    """Prepare dataset in YOLO format from images folder"""
    
    # Create output directories
    dataset_dir = Path(output_dir)
    (dataset_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # Get all product folders
    images_root = Path(images_root)
    product_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('product_')]
    label_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('labels_')]
    
    # Create class mapping
    classes = []
    for folder in product_folders:
        class_name = folder.name.replace('product_', '').split('_', 1)[1] if '_' in folder.name else folder.name
        if class_name not in classes:
            classes.append(class_name)
    
    class_to_id = {cls: idx for idx, cls in enumerate(classes)}
    
    print(f\"Found {len(classes)} classes: {classes}\")
    
    # Process each product folder
    all_files = []
    for product_folder in product_folders:
        product_id = product_folder.name.split('_')[1]
        
        # Find corresponding label folder
        label_folder = None
        for lf in label_folders:
            if f'product_{product_id}_' in lf.name:
                label_folder = lf
                break
        
        if not label_folder:
            print(f\"Warning: No labels found for {product_folder.name}\")
            continue
        
        # Get class name and ID
        class_name = product_folder.name.replace('product_', '').split('_', 1)[1]
        class_id = class_to_id[class_name]
        
        # Process images and labels - match by label files to ensure consistency
        for label_file in label_folder.glob('*.txt'):
            # Find corresponding image file with any supported extension
            img_file = None
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                potential_img = product_folder / f\"{label_file.stem}{ext}\"
                if potential_img.exists():
                    img_file = potential_img
                    break
            
            if img_file and img_file.exists():
                all_files.append((img_file, label_file, class_id))
            else:
                print(f\"Warning: No image found for label {label_file.name} in {product_folder.name}\")
    
    # Split into train/val (80/20)
    random.shuffle(all_files)
    split_idx = int(0.8 * len(all_files))
    train_files = all_files[:split_idx]
    val_files = all_files[split_idx:]
    
    print(f\"Train: {len(train_files)} images, Val: {len(val_files)} images\")
    
    # Copy files to train/val directories
    for files, split in [(train_files, 'train'), (val_files, 'val')]:
        for img_file, label_file, class_id in files:
            try:
                # Verify files exist before copying
                if not img_file.exists():
                    print(f\"Warning: Image file not found: {img_file}\")
                    continue
                if not label_file.exists():
                    print(f\"Warning: Label file not found: {label_file}\")
                    continue
                
                # Copy image with proper extension handling
                dst_img = dataset_dir / 'images' / split / img_file.name
                shutil.copy2(img_file, dst_img)
                
                # Process and copy label
                dst_label = dataset_dir / 'labels' / split / f\"{img_file.stem}.txt\"
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                # Update class IDs in labels and validate format
                with open(dst_label, 'w') as f:
                    for line in lines:
                        line = line.strip()
                        if not line:  # Skip empty lines
                            continue
                        parts = line.split()
                        if len(parts) >= 5:
                            # Replace class ID with our mapping
                            parts[0] = str(class_id)
                            f.write(' '.join(parts) + '\\n')
                        else:
                            print(f\"Warning: Invalid label format in {label_file}: {line}\")
                            
            except Exception as e:
                print(f\"Error processing {img_file}: {e}\")
                continue
    
    # Create dataset.yaml
    dataset_yaml = {
        'path': str(dataset_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes),
        'names': classes
    }
    
    with open(dataset_dir / 'dataset.yaml', 'w') as f:
        yaml.dump(dataset_yaml, f)
    
    print(f\"Dataset prepared in: {dataset_dir}\")
    return dataset_dir / 'dataset.yaml', classes

def train_with_yolo_cli(dataset_yaml, model_save_path, epochs=50):
    \"\"\"Train using YOLO CLI to avoid MLflow issues\"\"\"
    
    # Create the command
    cmd = f\"yolo detect train data={dataset_yaml} model=yolov8n.pt epochs={epochs} imgsz=640 batch=8 device=cpu project=runs/train name=custom_ceramic exist_ok=True\"
    
    print(f\"Running command: {cmd}\")
    
    # Execute the command
    result = os.system(cmd)
    
    if result == 0:
        # Find the trained model
        runs_dir = Path('runs/train')
        if runs_dir.exists():
            # Look for the latest training run
            train_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and 'custom_ceramic' in d.name]
            if train_dirs:
                latest_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
                best_model = latest_dir / 'weights' / 'best.pt'
                if best_model.exists():
                    # Copy to desired location
                    model_save_path = Path(model_save_path)
                    model_save_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(best_model, model_save_path)
                    print(f\"Model saved to: {model_save_path}\")
                    return True
    
    print(\"Training failed or model not found\")
    return False

def main():
    # Configuration
    IMAGES_ROOT = r\"c:\\Users\\boume\\Briefs\\Filrouge2A\\images\"
    DATASET_OUTPUT = r\"c:\\Users\\boume\\Briefs\\Filrouge2A\\Ai\\data\\custom_dataset\"
    MODEL_SAVE_PATH = r\"c:\\Users\\boume\\Briefs\\Filrouge2A\\Ai\\models\\custom_yolo_model.pt\"
    
    EPOCHS = 30  # Reduced for faster training
    
    print(\"Starting simple YOLO training...\")
    print(f\"Images source: {IMAGES_ROOT}\")
    print(f\"Dataset output: {DATASET_OUTPUT}\")
    print(f\"Model save path: {MODEL_SAVE_PATH}\")
    
    # Step 1: Prepare dataset
    print(\"\\n1. Preparing dataset...\")
    dataset_yaml, classes = prepare_dataset(IMAGES_ROOT, DATASET_OUTPUT)
    
    # Step 2: Train model using CLI
    print(f\"\\n2. Training YOLO model for {EPOCHS} epochs...\")
    print(f\"Classes: {classes}\")
    
    success = train_with_yolo_cli(dataset_yaml, MODEL_SAVE_PATH, EPOCHS)
    
    if success:
        print(\"\\nTraining completed successfully!\")
        print(f\"Model saved to: {MODEL_SAVE_PATH}\")
    else:
        print(\"\\nTraining failed. Check the output above for errors.\")

if __name__ == \"__main__\":
    main()