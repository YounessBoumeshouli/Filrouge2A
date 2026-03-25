#!/usr/bin/env python3
"""
Updated YOLO Dataset Preparation for New Marrakech Structure
===========================================================

Handles the updated dataset structure with:
- Mixed split/non-split categories
- Subcategories (spices, jewelry types)
- Large dataset (23K+ images)

Usage:
    python prepare_updated_dataset.py --source ../../marrakech_dataset --output data/yolo_dataset
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

class UpdatedYOLOPreparator:
    def __init__(self, source_dir, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Dataset statistics
        self.class_counts = Counter()
        self.total_images = 0
        self.class_to_id = {}
        self.id_to_class = {}
        
        # Categories that already have splits
        self.pre_split_categories = ['JEWELERY', 'lantern', 'material_fabric', 'textile']
        
        # Spice subcategories (treat as one class or separate?)
        self.spice_subcategories = [
            'black pepper', 'cardamom', 'cinnamon', 'cloves', 'coriander', 
            'cumin', 'ginger', 'nutmeg', 'paprika', 'saffron', 'turmeric'
        ]
    
    def analyze_structure(self):
        """Analyze the updated dataset structure"""
        print("🔍 Analyzing updated dataset structure...")
        print(f"📁 Source directory: {self.source_dir}")
        
        categories = []
        for item in self.source_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                categories.append(item.name)
        
        categories.sort()
        print(f"📊 Found categories: {categories}")
        
        # Analyze each category
        for i, category in enumerate(categories):
            category_path = self.source_dir / category
            
            if category == 'spices':
                # Handle spices as one category (combining subcategories)
                self.class_to_id['spices'] = len(self.class_to_id)
                self.id_to_class[len(self.id_to_class)] = 'spices'
                image_count = self._count_images_in_category(category_path)
                self.class_counts['spices'] = image_count
                print(f"  📂 spices: {image_count} images (11 subcategories combined)")
            else:
                self.class_to_id[category] = len(self.class_to_id)
                self.id_to_class[len(self.id_to_class)] = category
                image_count = self._count_images_in_category(category_path)
                self.class_counts[category] = image_count
                print(f"  📂 {category}: {image_count} images")
            
            self.total_images += image_count
        
        print(f"📈 Total images: {self.total_images}")
        return list(self.class_to_id.keys())
    
    def _count_images_in_category(self, category_path):
        """Count images in a category"""
        count = 0
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    count += 1
        
        return count
    
    def _get_images_with_splits(self, category_path, category_name):
        """Get images from pre-split categories"""
        splits = {'train': [], 'val': [], 'test': []}
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        # Look for data/train, data/val, data/test structure
        data_path = category_path / 'data'
        if data_path.exists():
            for split in ['train', 'val', 'test']:
                split_path = data_path / split
                if split_path.exists():
                    for root, dirs, files in os.walk(split_path):
                        for file in files:
                            if Path(file).suffix.lower() in image_extensions:
                                full_path = Path(root) / file
                                splits[split].append(full_path)
        
        return splits
    
    def _get_all_images_in_category(self, category_path):
        """Get all image paths in a category (for non-split categories)"""
        images = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    images.append(Path(root) / file)
        
        return images
    
    def create_splits(self, categories):
        """Create train/val/test splits handling pre-split and non-split categories"""
        print(f"📊 Creating dataset splits...")
        
        splits = {'train': [], 'val': [], 'test': []}
        
        for category in categories:
            category_path = self.source_dir / category
            class_id = self.class_to_id[category]
            
            if category in self.pre_split_categories:
                # Use existing splits
                print(f"  📂 {category}: Using existing train/val/test splits")
                existing_splits = self._get_images_with_splits(category_path, category)
                
                for split_name, images in existing_splits.items():
                    for img_path in images:
                        splits[split_name].append((img_path, category, class_id))
                
                print(f"     🚂 Train: {len(existing_splits['train'])}")
                print(f"     ✅ Val: {len(existing_splits['val'])}")
                print(f"     🧪 Test: {len(existing_splits['test'])}")
            
            else:
                # Create new splits
                print(f"  📂 {category}: Creating new splits")
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
                
                # Add to splits
                for img_path in train_images:
                    splits['train'].append((img_path, category, class_id))
                for img_path in val_images:
                    splits['val'].append((img_path, category, class_id))
                for img_path in test_images:
                    splits['test'].append((img_path, category, class_id))
                
                print(f"     🚂 Train: {len(train_images)}")
                print(f"     ✅ Val: {len(val_images)}")
                print(f"     🧪 Test: {len(test_images)}")
        
        # Print total splits
        print(f"\\n📊 Total splits:")
        print(f"  🚂 Train: {len(splits['train'])} images")
        print(f"  ✅ Val: {len(splits['val'])} images")
        print(f"  🧪 Test: {len(splits['test'])} images")
        
        return splits
    
    def create_yolo_structure(self, splits):
        """Create YOLO dataset structure"""
        print(f"🏗️  Creating YOLO dataset structure...")
        
        # Create output directories
        for split in ['train', 'val', 'test']:
            (self.output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Process each split
        for split_name, split_data in splits.items():
            print(f"  📁 Processing {split_name} split ({len(split_data)} images)...")
            
            for i, (img_path, category, class_id) in enumerate(split_data):
                if i % 1000 == 0 and i > 0:
                    print(f"    📥 Processed {i}/{len(split_data)} images...")
                
                # Generate new filename
                new_filename = f"{category}_{i:06d}{img_path.suffix}"
                
                # Copy image
                dst_img_path = self.output_dir / split_name / 'images' / new_filename
                try:
                    shutil.copy2(img_path, dst_img_path)
                except Exception as e:
                    print(f"    ⚠️  Error copying {img_path}: {e}")
                    continue
                
                # Create YOLO label
                label_filename = new_filename.replace(img_path.suffix, '.txt')
                dst_label_path = self.output_dir / split_name / 'labels' / label_filename
                
                # Full image bounding box (for classification/detection)
                with open(dst_label_path, 'w') as f:
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
            'categories': categories,
            'pre_split_categories': self.pre_split_categories
        }
        
        stats_path = self.output_dir / 'dataset_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"  📄 Dataset stats: {stats_path}")
        
        return config_path, mapping_path, stats_path
    
    def prepare_dataset(self):
        """Main dataset preparation workflow"""
        print("🚀 Starting updated YOLO dataset preparation...")
        print("=" * 60)
        
        # Analyze structure
        categories = self.analyze_structure()
        
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
        print("🎉 Updated dataset preparation completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Total images: {self.total_images}")
        print(f"📋 Categories: {len(categories)}")
        print(f"🏷️  Categories: {', '.join(categories)}")
        print("=" * 60)
        
        return config_files

def main():
    parser = argparse.ArgumentParser(description='Prepare updated Marrakech dataset for YOLO-Nano')
    parser.add_argument('--source', type=str, default='../../marrakech_dataset',
                       help='Source dataset directory')
    parser.add_argument('--output', type=str, default='data/yolo_dataset',
                       help='Output directory for YOLO dataset')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducible splits')
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print("🏺 Updated YOLO-Nano Dataset Preparation")
    print("=" * 60)
    print(f"📁 Source: {args.source}")
    print(f"📁 Output: {args.output}")
    print(f"🎲 Random seed: {args.seed}")
    print("=" * 60)
    
    try:
        preparator = UpdatedYOLOPreparator(
            source_dir=args.source,
            output_dir=args.output
        )
        
        config_files = preparator.prepare_dataset()
        
        print("\\n🎯 Next steps:")
        print("1. Review the generated dataset structure")
        print("2. Start training with: python train.py --data data/yolo_dataset/dataset.yaml")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()