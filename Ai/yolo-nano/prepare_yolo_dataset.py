#!/usr/bin/env python3
"""
Dataset Preparation for YOLO-Nano
=================================

Prepares the Marrakech dataset for YOLO-Nano training by:
1. Analyzing current dataset structure
2. Creating train/val/test splits
3. Generating YOLO format annotations
4. Creating dataset configuration files

Usage:
    python prepare_yolo_dataset.py --source marrakech_dataset_enhanced --output data/yolo_dataset
"""

import os
import sys
import json
import argparse
import shutil
import random
from pathlib import Path
from collections import defaultdict, Counter
import yaml

class YOLODatasetPreparator:
    def __init__(self, source_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Ensure ratios sum to 1
        total = train_ratio + val_ratio + test_ratio
        if abs(total - 1.0) > 0.001:
            print(f"⚠️  Warning: Ratios sum to {total}, normalizing...")
            self.train_ratio /= total
            self.val_ratio /= total
            self.test_ratio /= total
        
        # Dataset statistics
        self.class_counts = Counter()
        self.total_images = 0
        self.class_to_id = {}
        self.id_to_class = {}
        
    def analyze_dataset(self):
        """Analyze the current dataset structure"""
        print("🔍 Analyzing dataset structure...")
        print(f"📁 Source directory: {self.source_dir}")
        
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        # Find all categories
        categories = []
        for item in self.source_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories.append(item.name)
        
        categories.sort()
        print(f"📊 Found categories: {categories}")
        
        # Count images in each category
        for i, category in enumerate(categories):
            self.class_to_id[category] = i
            self.id_to_class[i] = category
            
            category_path = self.source_dir / category
            image_count = self._count_images_in_category(category_path)
            self.class_counts[category] = image_count
            self.total_images += image_count
            
            print(f"  📂 {category}: {image_count} images")
        
        print(f"📈 Total images: {self.total_images}")
        print(f"📋 Total categories: {len(categories)}")
        
        return categories
    
    def _count_images_in_category(self, category_path):
        """Count images in a category (handles subdirectories)"""
        count = 0
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    count += 1
        
        return count
    
    def _get_all_images_in_category(self, category_path):
        """Get all image paths in a category"""
        images = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    images.append(Path(root) / file)
        
        return images
    
    def create_splits(self, categories):
        """Create train/val/test splits"""
        print(f"📊 Creating dataset splits...")
        print(f"  🚂 Train: {self.train_ratio:.1%}")
        print(f"  ✅ Validation: {self.val_ratio:.1%}")
        print(f"  🧪 Test: {self.test_ratio:.1%}")
        
        splits = {'train': [], 'val': [], 'test': []}
        
        for category in categories:
            category_path = self.source_dir / category
            images = self._get_all_images_in_category(category_path)
            
            if not images:
                print(f"⚠️  Warning: No images found in {category}")
                continue
            
            # Shuffle images
            random.shuffle(images)
            
            # Calculate split indices
            n_images = len(images)
            n_train = int(n_images * self.train_ratio)
            n_val = int(n_images * self.val_ratio)
            
            # Split images
            train_images = images[:n_train]
            val_images = images[n_train:n_train + n_val]
            test_images = images[n_train + n_val:]
            
            # Add to splits with category info
            for img_path in train_images:
                splits['train'].append((img_path, category, self.class_to_id[category]))
            for img_path in val_images:
                splits['val'].append((img_path, category, self.class_to_id[category]))
            for img_path in test_images:
                splits['test'].append((img_path, category, self.class_to_id[category]))
            
            print(f"  📂 {category}: {len(train_images)} train, {len(val_images)} val, {len(test_images)} test")
        
        return splits
    
    def create_yolo_structure(self, splits):
        """Create YOLO dataset structure"""
        print(f"🏗️  Creating YOLO dataset structure...")
        
        # Create output directories
        for split in ['train', 'val', 'test']:
            (self.output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Copy images and create labels
        for split_name, split_data in splits.items():
            print(f"  📁 Processing {split_name} split ({len(split_data)} images)...")
            
            for i, (img_path, category, class_id) in enumerate(split_data):
                # Generate new filename
                new_filename = f"{category}_{i:05d}{img_path.suffix}"
                
                # Copy image
                dst_img_path = self.output_dir / split_name / 'images' / new_filename
                shutil.copy2(img_path, dst_img_path)
                
                # Create YOLO label (for classification, we create a simple format)
                # For object detection, you would need bounding box annotations
                label_filename = new_filename.replace(img_path.suffix, '.txt')
                dst_label_path = self.output_dir / split_name / 'labels' / label_filename
                
                # For classification: just the class ID
                # For detection: class_id x_center y_center width height (normalized)
                # Since we don't have bounding boxes, we'll create full-image annotations
                with open(dst_label_path, 'w') as f:
                    # Full image bounding box (normalized coordinates)
                    f.write(f"{class_id} 0.5 0.5 1.0 1.0\\n")
        
        print("✅ YOLO structure created successfully!")
    
    def create_config_files(self, categories):
        """Create YOLO configuration files"""
        print("📝 Creating configuration files...")
        
        # Dataset YAML configuration
        dataset_config = {
            'path': str(self.output_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(categories),
            'names': categories
        }
        
        config_path = self.output_dir / 'dataset.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(dataset_config, f, default_flow_style=False)
        
        print(f"  📄 Dataset config: {config_path}")
        
        # Class mapping JSON
        class_mapping = {
            'class_to_id': self.class_to_id,
            'id_to_class': self.id_to_class,
            'num_classes': len(categories),
            'categories': categories
        }
        
        mapping_path = self.output_dir / 'class_mapping.json'
        with open(mapping_path, 'w') as f:
            json.dump(class_mapping, f, indent=2)
        
        print(f"  📄 Class mapping: {mapping_path}")
        
        # Dataset statistics
        stats = {
            'total_images': self.total_images,
            'num_classes': len(categories),
            'class_counts': dict(self.class_counts),
            'splits': {
                'train_ratio': self.train_ratio,
                'val_ratio': self.val_ratio,
                'test_ratio': self.test_ratio
            },
            'categories': categories
        }
        
        stats_path = self.output_dir / 'dataset_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"  📄 Dataset stats: {stats_path}")
        
        return config_path, mapping_path, stats_path
    
    def prepare_dataset(self):
        """Main dataset preparation workflow"""
        print("🚀 Starting YOLO dataset preparation...")
        print("=" * 60)
        
        # Analyze current dataset
        categories = self.analyze_dataset()
        
        if not categories:
            raise ValueError("No categories found in source directory")
        
        print("\\n" + "=" * 60)
        
        # Create splits
        splits = self.create_splits(categories)
        
        print("\\n" + "=" * 60)
        
        # Create YOLO structure
        self.create_yolo_structure(splits)
        
        print("\\n" + "=" * 60)
        
        # Create config files
        config_files = self.create_config_files(categories)
        
        print("\\n" + "=" * 60)
        print("🎉 Dataset preparation completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Total images: {self.total_images}")
        print(f"📋 Categories: {len(categories)}")
        print("=" * 60)
        
        return config_files

def main():
    parser = argparse.ArgumentParser(description='Prepare Marrakech dataset for YOLO-Nano')
    parser.add_argument('--source', type=str, default='../../marrakech_dataset_enhanced',
                       help='Source dataset directory')
    parser.add_argument('--output', type=str, default='data/yolo_dataset',
                       help='Output directory for YOLO dataset')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                       help='Training set ratio')
    parser.add_argument('--val-ratio', type=float, default=0.2,
                       help='Validation set ratio')
    parser.add_argument('--test-ratio', type=float, default=0.1,
                       help='Test set ratio')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducible splits')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print("🏺 YOLO-Nano Dataset Preparation")
    print("=" * 60)
    print(f"📁 Source: {args.source}")
    print(f"📁 Output: {args.output}")
    print(f"🎲 Random seed: {args.seed}")
    print("=" * 60)
    
    try:
        preparator = YOLODatasetPreparator(
            source_dir=args.source,
            output_dir=args.output,
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=args.test_ratio
        )
        
        config_files = preparator.prepare_dataset()
        
        print("\\n🎯 Next steps:")
        print("1. Review the generated dataset structure")
        print("2. Update YOLO-Nano config with the dataset.yaml path")
        print("3. Start training with: python train.py --data data/yolo_dataset/dataset.yaml")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()