#!/usr/bin/env python3
"""
Robust YOLO Training with Custom Augmentation
=============================================

A simplified but robust approach to training YOLO with custom augmentation.
Handles MLflow issues and provides comprehensive data augmentation.
"""

import os
import shutil
import yaml
import random
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

def disable_mlflow():
    """Disable MLflow to avoid tracking issues"""
    os.environ['MLFLOW_TRACKING_URI'] = ''
    os.environ['DISABLE_MLFLOW'] = '1'
    os.environ['MLFLOW_DISABLE'] = '1'

class SimpleYOLOTrainer:
    def __init__(self, images_root, output_dir):
        self.images_root = Path(images_root)
        self.output_dir = Path(output_dir)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        
    def collect_all_data(self):
        """Collect all image-label pairs from all product folders"""
        
        print("🔍 Collecting dataset...")
        
        # Find product and label folders
        product_folders = [f for f in self.images_root.iterdir() 
                          if f.is_dir() and f.name.startswith('product_')]
        
        all_pairs = []
        classes = []
        
        for product_folder in product_folders:
            # Extract product info
            parts = product_folder.name.split('_', 2)
            if len(parts) < 2:
                continue
                
            product_id = parts[1]
            class_name = parts[2] if len(parts) > 2 else f"Product_{product_id}"
            
            # Add to classes if new
            if class_name not in classes:
                classes.append(class_name)
            class_id = classes.index(class_name)
            
            # Find corresponding labels folder
            label_folder = None
            for folder in self.images_root.iterdir():
                if folder.is_dir() and f'labels_product_{product_id}_' in folder.name:
                    label_folder = folder
                    break
            
            if not label_folder:
                print(f"⚠️ No labels for {product_folder.name}")
                continue
            
            # Collect image-label pairs
            for img_file in product_folder.iterdir():
                if img_file.suffix.lower() in self.image_extensions:
                    label_file = label_folder / f"{img_file.stem}.txt"
                    if label_file.exists():
                        all_pairs.append((img_file, label_file, class_id))
        
        print(f"📊 Found {len(all_pairs)} image-label pairs")
        print(f"🏷️ Found {len(classes)} classes:")
        for i, cls in enumerate(classes):
            print(f"   {i}: {cls}")
        
        return all_pairs, classes
    
    def create_augmented_dataset(self, all_pairs, classes, train_split=0.8, augment_count=2):
        """Create augmented dataset with train/val split"""
        
        print("\n🔄 Creating augmented dataset...")
        print(f"📊 Original pairs: {len(all_pairs)}")
        print(f"🔀 Augmentations per image: {augment_count}")
        
        # Create directories
        for split in ['train', 'val']:
            (self.output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        # Split data
        random.shuffle(all_pairs)
        split_idx = int(train_split * len(all_pairs))
        train_pairs = all_pairs[:split_idx]
        val_pairs = all_pairs[split_idx:]
        
        print(f"🚂 Train: {len(train_pairs)} pairs")
        print(f"✅ Val: {len(val_pairs)} pairs")
        
        # Process training data with augmentation
        train_count = 0
        for i, (img_file, label_file, class_id) in enumerate(train_pairs):
            # Original image
            self.save_image_label_pair(
                img_file, label_file, class_id, 'train', f"train_{i:04d}_orig"
            )
            train_count += 1
            
            # Augmented versions
            for aug_idx in range(augment_count):
                try:
                    self.save_augmented_pair(
                        img_file, label_file, class_id, 'train', f"train_{i:04d}_aug{aug_idx}"
                    )
                    train_count += 1
                except Exception as e:
                    print(f"⚠️ Aug failed for {img_file.name}: {e}")
            
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(train_pairs)} train images...")
        
        # Process validation data (no augmentation)
        val_count = 0
        for i, (img_file, label_file, class_id) in enumerate(val_pairs):
            self.save_image_label_pair(
                img_file, label_file, class_id, 'val', f"val_{i:04d}"
            )
            val_count += 1
        
        # Create dataset.yaml
        dataset_config = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(classes),
            'names': classes
        }
        
        with open(self.output_dir / 'dataset.yaml', 'w') as f:
            yaml.dump(dataset_config, f)
        
        print("✅ Dataset created!")
        print(f"🚂 Train images: {train_count}")
        print(f"✅ Val images: {val_count}")
        
        return self.output_dir / 'dataset.yaml'
    
    def save_image_label_pair(self, img_file, label_file, class_id, split, name):
        """Save original image-label pair"""
        
        # Save image as JPG
        dst_img = self.output_dir / 'images' / split / f"{name}.jpg"
        img = Image.open(img_file)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        img.save(dst_img, 'JPEG', quality=90)
        
        # Save label with updated class ID
        dst_label = self.output_dir / 'labels' / split / f"{name}.txt"
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
    
    def save_augmented_pair(self, img_file, label_file, class_id, split, name):
        """Save augmented image-label pair"""
        
        # Load image
        img = Image.open(img_file)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        
        # Load labels
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        labels = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    labels.append([float(x) for x in parts[1:5]])
        
        # Apply augmentations
        aug_img, aug_labels = self.augment_image_labels(img, labels)
        
        # Save augmented image
        dst_img = self.output_dir / 'images' / split / f"{name}.jpg"
        aug_img.save(dst_img, 'JPEG', quality=90)
        
        # Save augmented labels
        dst_label = self.output_dir / 'labels' / split / f"{name}.txt"
        with open(dst_label, 'w') as f:
            for label in aug_labels:
                f.write(f"{class_id} {label[0]:.6f} {label[1]:.6f} {label[2]:.6f} {label[3]:.6f}\n")
    
    def augment_image_labels(self, img, labels):
        """Apply random augmentations"""
        
        # Convert to array for flipping
        img_array = np.array(img)
        
        # Random horizontal flip
        if random.random() < 0.5:
            img_array = np.fliplr(img_array)
            # Flip bounding boxes
            for label in labels:
                label[0] = 1.0 - label[0]  # Flip x_center
        
        img = Image.fromarray(img_array)
        
        # Random brightness (70% chance)
        if random.random() < 0.7:
            enhancer = ImageEnhance.Brightness(img)
            factor = random.uniform(0.7, 1.3)
            img = enhancer.enhance(factor)
        
        # Random contrast (70% chance)
        if random.random() < 0.7:
            enhancer = ImageEnhance.Contrast(img)
            factor = random.uniform(0.8, 1.2)
            img = enhancer.enhance(factor)
        
        # Random saturation (50% chance)
        if random.random() < 0.5:
            enhancer = ImageEnhance.Color(img)
            factor = random.uniform(0.8, 1.2)
            img = enhancer.enhance(factor)
        
        # Random blur (30% chance)
        if random.random() < 0.3:
            radius = random.uniform(0.5, 1.5)
            img = img.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # Random noise (20% chance)
        if random.random() < 0.2:
            img_array = np.array(img)
            noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
            img_array = np.clip(img_array.astype(int) + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_array)
        
        return img, labels

def train_with_cli(dataset_yaml, model_path, epochs=80):
    """Train using command line to avoid MLflow issues"""
    
    print("\n🚀 Training YOLO model...")
    print(f"📊 Dataset: {dataset_yaml}")
    print(f"🔄 Epochs: {epochs}")
    
    # Disable MLflow
    disable_mlflow()
    
    # Create command
    cmd = f"""yolo detect train \
data="{dataset_yaml}" \
model=yolov8n.pt \
epochs={epochs} \
imgsz=640 \
batch=8 \
device=cpu \
hsv_h=0.015 \
hsv_s=0.7 \
hsv_v=0.4 \
degrees=15 \
translate=0.1 \
scale=0.9 \
fliplr=0.5 \
mosaic=1.0 \
mixup=0.1 \
project=runs/train \
name=ceramic_augmented \
exist_ok=True \
save=True \
patience=20"""
    
    print(f"🔧 Command: {cmd}")
    
    # Execute training
    result = os.system(cmd)
    
    if result == 0:
        # Find and copy trained model
        runs_dir = Path('runs/train')
        if runs_dir.exists():
            train_dirs = [d for d in runs_dir.iterdir() 
                         if d.is_dir() and 'ceramic_augmented' in d.name]
            if train_dirs:
                latest_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
                best_model = latest_dir / 'weights' / 'best.pt'
                
                if best_model.exists():
                    model_path = Path(model_path)
                    model_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(best_model, model_path)
                    print(f"✅ Model saved to: {model_path}")
                    return True
    
    print("❌ Training failed")
    return False

def main():
    # Configuration
    IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"
    OUTPUT_DIR = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\ceramic_augmented"
    MODEL_PATH = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\ceramic_yolo_augmented.pt"
    
    EPOCHS = 80
    AUGMENT_COUNT = 2  # 2 augmented versions per original image
    TRAIN_SPLIT = 0.8
    
    print("🏺 YOLO Training with Custom Augmentation")
    print("=" * 60)
    
    try:
        # Initialize trainer
        trainer = SimpleYOLOTrainer(IMAGES_ROOT, OUTPUT_DIR)
        
        # Collect data
        print("\n📊 STEP 1: COLLECTING DATA")
        all_pairs, classes = trainer.collect_all_data()
        
        if not all_pairs:
            print("❌ No data found!")
            return
        
        # Create augmented dataset
        print("\n🔄 STEP 2: CREATING AUGMENTED DATASET")
        dataset_yaml = trainer.create_augmented_dataset(
            all_pairs, classes, TRAIN_SPLIT, AUGMENT_COUNT
        )
        
        # Train model
        print("\n🚀 STEP 3: TRAINING MODEL")
        success = train_with_cli(dataset_yaml, MODEL_PATH, EPOCHS)
        
        if success:
            print("\n🎉 TRAINING COMPLETED!")
            print(f"💾 Model: {MODEL_PATH}")
            print(f"📊 Classes: {len(classes)}")
            for i, cls in enumerate(classes):
                print(f"   {i}: {cls}")
        else:
            print(f"\n❌ Training failed!")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()