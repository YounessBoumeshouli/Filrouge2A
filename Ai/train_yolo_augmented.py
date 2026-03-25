#!/usr/bin/env python3
"""
Advanced YOLO Training with Data Augmentation
=============================================

Trains YOLO model on the complete dataset with advanced augmentation techniques.
Includes all product categories and optimized training parameters.
"""

import os
import shutil
import yaml
import random
import json
from pathlib import Path
from PIL import Image
import numpy as np

class AdvancedYOLOTrainer:
    def __init__(self, images_root, output_dir):
        self.images_root = Path(images_root)
        self.output_dir = Path(output_dir)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
    def scan_dataset(self):
        """Scan all product folders and their corresponding labels"""
        
        print("🔍 Scanning dataset...")
        
        # Find all product folders
        product_folders = [f for f in self.images_root.iterdir() 
                          if f.is_dir() and f.name.startswith('product_')]
        
        # Find all label folders
        label_folders = [f for f in self.images_root.iterdir() 
                        if f.is_dir() and f.name.startswith('labels_')]
        
        print(f"📁 Found {len(product_folders)} product folders")
        print(f"🏷️ Found {len(label_folders)} label folders")
        
        # Match products with labels
        dataset_info = {}
        total_images = 0
        total_labels = 0
        
        for product_folder in product_folders:
            # Extract product ID and name
            parts = product_folder.name.split('_', 2)
            if len(parts) >= 2:
                product_id = parts[1]
                product_name = parts[2] if len(parts) > 2 else f"Product_{product_id}"
            else:
                continue
            
            # Find corresponding label folder
            label_folder = None
            for lf in label_folders:
                if f'product_{product_id}_' in lf.name:
                    label_folder = lf
                    break
            
            if not label_folder:
                print(f"⚠️ No labels found for {product_folder.name}")
                continue
            
            # Count images and labels
            images = [f for f in product_folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in self.image_extensions]
            labels = [f for f in label_folder.iterdir() 
                     if f.is_file() and f.suffix.lower() == '.txt']
            
            # Count matched pairs
            matched_pairs = 0
            for img in images:
                label_file = label_folder / f"{img.stem}.txt"
                if label_file.exists():
                    matched_pairs += 1
            
            dataset_info[product_id] = {
                'name': product_name,
                'images_folder': product_folder,
                'labels_folder': label_folder,
                'total_images': len(images),
                'total_labels': len(labels),
                'matched_pairs': matched_pairs
            }
            
            total_images += len(images)
            total_labels += len(labels)
            
            print(f"  📦 {product_name}: {matched_pairs} matched pairs")
        
        print(f"\n📊 DATASET SUMMARY:")
        print(f"📸 Total images: {total_images}")
        print(f"🏷️ Total labels: {total_labels}")
        print(f"🎯 Product categories: {len(dataset_info)}")
        
        return dataset_info
    
    def prepare_augmented_dataset(self, dataset_info, train_split=0.8, augment_factor=3):
        """Prepare dataset with augmentation"""
        
        print(f"\n🔄 Preparing augmented dataset...")
        print(f"📊 Train/Val split: {train_split:.0%}/{1-train_split:.0%}")
        print(f"🔀 Augmentation factor: {augment_factor}x")
        
        # Create output directories
        dataset_dir = self.output_dir
        for split in ['train', 'val']:
            (dataset_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (dataset_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        # Create class mapping
        classes = []
        class_to_id = {}
        
        for product_id, info in dataset_info.items():
            class_name = info['name']
            if class_name not in classes:
                classes.append(class_name)
                class_to_id[class_name] = len(classes) - 1
        
        print(f"🏷️ Classes ({len(classes)}):")
        for i, cls in enumerate(classes):
            print(f"  {i}: {cls}")
        
        # Collect all valid image-label pairs
        all_pairs = []
        for product_id, info in dataset_info.items():
            class_id = class_to_id[info['name']]
            
            for img_file in info['images_folder'].iterdir():
                if img_file.suffix.lower() in self.image_extensions:
                    label_file = info['labels_folder'] / f"{img_file.stem}.txt"
                    if label_file.exists():
                        all_pairs.append((img_file, label_file, class_id, info['name']))
        
        print(f"📸 Total valid pairs: {len(all_pairs)}")
        
        # Split into train/val
        random.shuffle(all_pairs)
        split_idx = int(train_split * len(all_pairs))
        train_pairs = all_pairs[:split_idx]
        val_pairs = all_pairs[split_idx:]
        
        print(f"🚂 Train pairs: {len(train_pairs)}")
        print(f"✅ Val pairs: {len(val_pairs)}")
        
        # Process training data with augmentation
        print(f"\n🔀 Processing training data with augmentation...")
        train_count = self.process_split_with_augmentation(
            train_pairs, 'train', dataset_dir, augment_factor
        )
        
        # Process validation data (no augmentation)
        print(f"\n📊 Processing validation data...")
        val_count = self.process_split_with_augmentation(
            val_pairs, 'val', dataset_dir, augment_factor=1
        )
        
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
        
        # Save dataset statistics
        stats = {
            'total_classes': len(classes),
            'class_names': classes,
            'original_pairs': len(all_pairs),
            'train_pairs_original': len(train_pairs),
            'val_pairs_original': len(val_pairs),
            'train_images_final': train_count,
            'val_images_final': val_count,
            'augmentation_factor': augment_factor,
            'train_split': train_split
        }
        
        with open(dataset_dir / 'dataset_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n✅ Dataset preparation complete!")
        print(f"📁 Output: {dataset_dir}")
        print(f"📊 Final counts - Train: {train_count}, Val: {val_count}")
        
        return dataset_dir / 'dataset.yaml', classes, stats
    
    def process_split_with_augmentation(self, pairs, split_name, dataset_dir, augment_factor):
        """Process a data split with augmentation"""
        
        processed_count = 0
        
        for i, (img_file, label_file, class_id, class_name) in enumerate(pairs):
            # Original image (always included)
            self.copy_image_label_pair(
                img_file, label_file, class_id, 
                dataset_dir, split_name, f"{split_name}_{i:04d}_orig"
            )
            processed_count += 1
            
            # Augmented versions (only for training)
            if split_name == 'train' and augment_factor > 1:
                for aug_idx in range(augment_factor - 1):
                    try:
                        self.create_augmented_pair(
                            img_file, label_file, class_id,
                            dataset_dir, split_name, f"{split_name}_{i:04d}_aug{aug_idx + 1}"
                        )
                        processed_count += 1
                    except Exception as e:
                        print(f"⚠️ Augmentation failed for {img_file.name}: {e}")
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(pairs)} pairs...")
        
        return processed_count
    
    def copy_image_label_pair(self, img_file, label_file, class_id, dataset_dir, split, new_name):
        """Copy image and label pair to dataset directory"""
        
        # Copy image
        dst_img = dataset_dir / 'images' / split / f"{new_name}.jpg"
        
        # Convert to JPG if needed
        if img_file.suffix.lower() != '.jpg':
            img = Image.open(img_file)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(dst_img, 'JPEG', quality=90)
        else:
            shutil.copy2(img_file, dst_img)
        
        # Process label
        dst_label = dataset_dir / 'labels' / split / f"{new_name}.txt"
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        with open(dst_label, 'w') as f:
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 5:
                        # Update class ID
                        parts[0] = str(class_id)
                        f.write(' '.join(parts) + '\n')
    
    def create_augmented_pair(self, img_file, label_file, class_id, dataset_dir, split, new_name):
        """Create augmented image and label pair"""
        
        # Load original image
        img = Image.open(img_file)
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        
        # Load original labels
        with open(label_file, 'r') as f:
            lines = f.readlines()
        
        labels = []
        for line in lines:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) >= 5:
                    labels.append([float(x) for x in parts[1:5]])  # x_center, y_center, width, height
        
        # Apply random augmentations
        aug_img, aug_labels = self.apply_augmentations(img, labels)
        
        # Save augmented image
        dst_img = dataset_dir / 'images' / split / f"{new_name}.jpg"
        aug_img.save(dst_img, 'JPEG', quality=90)
        
        # Save augmented labels
        dst_label = dataset_dir / 'labels' / split / f"{new_name}.txt"
        with open(dst_label, 'w') as f:
            for label in aug_labels:
                f.write(f"{class_id} {label[0]:.6f} {label[1]:.6f} {label[2]:.6f} {label[3]:.6f}\n")
    
    def apply_augmentations(self, img, labels):
        """Apply random augmentations to image and labels"""
        
        import random
        from PIL import ImageEnhance, ImageFilter
        
        # Convert to numpy for easier manipulation
        img_array = np.array(img)
        height, width = img_array.shape[:2]
        
        # Random horizontal flip
        if random.random() < 0.5:
            img_array = np.fliplr(img_array)
            # Flip labels
            for label in labels:
                label[0] = 1.0 - label[0]  # Flip x_center
        
        # Convert back to PIL
        img = Image.fromarray(img_array)
        
        # Random brightness adjustment
        if random.random() < 0.7:
            enhancer = ImageEnhance.Brightness(img)
            factor = random.uniform(0.8, 1.2)
            img = enhancer.enhance(factor)
        
        # Random contrast adjustment
        if random.random() < 0.7:
            enhancer = ImageEnhance.Contrast(img)
            factor = random.uniform(0.8, 1.2)
            img = enhancer.enhance(factor)
        
        # Random saturation adjustment
        if random.random() < 0.5:
            enhancer = ImageEnhance.Color(img)
            factor = random.uniform(0.8, 1.2)
            img = enhancer.enhance(factor)
        
        # Random blur (light)
        if random.random() < 0.3:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.0)))
        
        # Random rotation (small angles)
        if random.random() < 0.4:
            angle = random.uniform(-10, 10)
            img = img.rotate(angle, expand=False, fillcolor=(128, 128, 128))
            # Note: For simplicity, we keep labels unchanged for small rotations
            # In production, you'd want to rotate the bounding boxes too
        
        return img, labels

def train_yolo_model(dataset_yaml, model_save_path, epochs=100, img_size=640):
    """Train YOLO model with optimized parameters"""
    
    print(f"\n🚀 Starting YOLO training...")
    print(f"📊 Dataset: {dataset_yaml}")
    print(f"💾 Model save path: {model_save_path}")
    print(f"🔄 Epochs: {epochs}")
    print(f"📐 Image size: {img_size}")
    
    # Set environment variables to avoid MLflow issues
    os.environ['MLFLOW_TRACKING_URI'] = ''
    os.environ['DISABLE_MLFLOW'] = '1'
    
    try:
        from ultralytics import YOLO
        
        # Initialize model
        model = YOLO('yolov8n.pt')  # Start with nano for speed
        
        # Training parameters with augmentation
        results = model.train(
            data=str(dataset_yaml),
            epochs=epochs,
            imgsz=img_size,
            batch=16,  # Adjust based on your GPU memory
            device='cuda' if os.system('nvidia-smi') == 0 else 'cpu',
            
            # Augmentation parameters (built-in YOLO augmentations)
            hsv_h=0.015,      # HSV-Hue augmentation
            hsv_s=0.7,        # HSV-Saturation augmentation  
            hsv_v=0.4,        # HSV-Value augmentation
            degrees=10.0,     # Rotation degrees
            translate=0.1,    # Translation fraction
            scale=0.5,        # Scaling factor
            shear=0.0,        # Shear degrees
            perspective=0.0,  # Perspective transformation
            flipud=0.0,       # Vertical flip probability
            fliplr=0.5,       # Horizontal flip probability
            mosaic=1.0,       # Mosaic augmentation probability
            mixup=0.1,        # MixUp augmentation probability
            copy_paste=0.1,   # Copy-paste augmentation probability
            
            # Training parameters
            lr0=0.01,         # Initial learning rate
            lrf=0.01,         # Final learning rate fraction
            momentum=0.937,   # SGD momentum
            weight_decay=0.0005,  # Weight decay
            warmup_epochs=3.0,    # Warmup epochs
            warmup_momentum=0.8,  # Warmup momentum
            warmup_bias_lr=0.1,   # Warmup bias learning rate
            
            # Other parameters
            project='runs/train',
            name='ceramic_products_augmented',
            exist_ok=True,
            save=True,
            save_period=10,
            val=True,
            plots=True,
            verbose=True
        )
        
        # Save model to specified location
        model_save_path = Path(model_save_path)
        model_save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Find and copy the best model
        runs_dir = Path('runs/train')
        train_dirs = [d for d in runs_dir.iterdir() 
                     if d.is_dir() and 'ceramic_products_augmented' in d.name]
        
        if train_dirs:
            latest_dir = max(train_dirs, key=lambda x: x.stat().st_mtime)
            best_model = latest_dir / 'weights' / 'best.pt'
            
            if best_model.exists():
                shutil.copy2(best_model, model_save_path)
                print(f"✅ Model saved to: {model_save_path}")
                
                # Also save training results
                results_dir = model_save_path.parent / 'training_results'
                if results_dir.exists():
                    shutil.rmtree(results_dir)
                shutil.copytree(latest_dir, results_dir)
                print(f"📊 Training results saved to: {results_dir}")
                
                return True
        
        print("⚠️ Training completed but model not found")
        return False
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def main():
    # Configuration
    IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"
    OUTPUT_DIR = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\augmented_dataset"
    MODEL_SAVE_PATH = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\ceramic_products_augmented.pt"
    
    # Training parameters
    EPOCHS = 100
    IMG_SIZE = 640
    AUGMENT_FACTOR = 3  # 3x augmentation
    TRAIN_SPLIT = 0.8   # 80% train, 20% val
    
    print("🏺 Advanced YOLO Training with Data Augmentation")
    print("=" * 70)
    print(f"📁 Images source: {IMAGES_ROOT}")
    print(f"📊 Output dataset: {OUTPUT_DIR}")
    print(f"💾 Model save path: {MODEL_SAVE_PATH}")
    print(f"🔀 Augmentation factor: {AUGMENT_FACTOR}x")
    print(f"🚂 Train/Val split: {TRAIN_SPLIT:.0%}/{1-TRAIN_SPLIT:.0%}")
    
    try:
        # Initialize trainer
        trainer = AdvancedYOLOTrainer(IMAGES_ROOT, OUTPUT_DIR)
        
        # Step 1: Scan dataset
        print(f"\n" + "="*70)
        print("STEP 1: SCANNING DATASET")
        print("="*70)
        dataset_info = trainer.scan_dataset()
        
        if not dataset_info:
            print("❌ No valid dataset found!")
            return
        
        # Step 2: Prepare augmented dataset
        print(f"\n" + "="*70)
        print("STEP 2: PREPARING AUGMENTED DATASET")
        print("="*70)
        dataset_yaml, classes, stats = trainer.prepare_augmented_dataset(
            dataset_info, TRAIN_SPLIT, AUGMENT_FACTOR
        )
        
        print(f"\n📊 DATASET STATISTICS:")
        print(f"🏷️ Classes: {stats['total_classes']}")
        print(f"📸 Original pairs: {stats['original_pairs']}")
        print(f"🚂 Final train images: {stats['train_images_final']}")
        print(f"✅ Final val images: {stats['val_images_final']}")
        print(f"🔀 Augmentation factor: {stats['augmentation_factor']}x")
        
        # Step 3: Train model
        print(f"\n" + "="*70)
        print("STEP 3: TRAINING YOLO MODEL")
        print("="*70)
        
        success = train_yolo_model(
            dataset_yaml, MODEL_SAVE_PATH, EPOCHS, IMG_SIZE
        )
        
        if success:
            print(f"\n🎉 TRAINING COMPLETED SUCCESSFULLY!")
            print(f"💾 Model: {MODEL_SAVE_PATH}")
            print(f"📊 Dataset: {OUTPUT_DIR}")
            print(f"🏷️ Classes: {len(classes)}")
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