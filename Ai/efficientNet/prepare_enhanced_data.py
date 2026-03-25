#!/usr/bin/env python3
"""
Prepare enhanced dataset from scraped images
"""

import os
import shutil
import random
import json
from pathlib import Path
from PIL import Image

class DatasetPreparer:
    def __init__(self, source_dir="../../marrakech_dataset_enhanced", target_dir="../data/price_enhanced"):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.categories = ["argan", "crafts", "jewelry", "lanterns", "leather", "price_tags", "spices", "textiles"]
    
    def validate_image(self, image_path):
        """Validate if image is usable"""
        try:
            with Image.open(image_path) as img:
                # Check minimum size
                if img.size[0] < 100 or img.size[1] < 100:
                    return False
                
                # Check if image is not corrupted
                img.verify()
                return True
        except:
            return False
    
    def collect_valid_images(self):
        """Collect all valid images from scraped data"""
        print("🔍 Collecting and validating images...")
        
        valid_images = {}
        total_valid = 0
        
        for category in self.categories:
            valid_images[category] = []
            category_path = os.path.join(self.source_dir, category)
            
            if not os.path.exists(category_path):
                print(f"⚠️  Category {category} not found, skipping...")
                continue
            
            # Collect from all sources (bing, google, unsplash)
            for source in ['bing', 'google', 'unsplash']:
                source_path = os.path.join(category_path, source)
                if os.path.exists(source_path):
                    for img_file in os.listdir(source_path):
                        if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            img_path = os.path.join(source_path, img_file)
                            if self.validate_image(img_path):
                                valid_images[category].append(img_path)
            
            print(f"  {category}: {len(valid_images[category])} valid images")
            total_valid += len(valid_images[category])
        
        print(f"📊 Total valid images: {total_valid}")
        return valid_images
    
    def create_splits(self, valid_images, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
        """Create train/val/test splits"""
        print("\n📂 Creating train/val/test splits...")
        
        # Create directories
        for split in ['train', 'val', 'test']:
            for category in self.categories:
                split_dir = os.path.join(self.target_dir, split, category)
                os.makedirs(split_dir, exist_ok=True)
        
        split_stats = {}
        
        for category, images in valid_images.items():
            if not images:
                continue
            
            # Shuffle images
            random.shuffle(images)
            
            # Calculate split sizes
            total = len(images)
            train_size = int(total * train_ratio)
            val_size = int(total * val_ratio)
            
            # Split images
            train_images = images[:train_size]
            val_images = images[train_size:train_size + val_size]
            test_images = images[train_size + val_size:]
            
            # Copy images to respective directories
            splits = {
                'train': train_images,
                'val': val_images,
                'test': test_images
            }
            
            split_stats[category] = {}
            
            for split_name, split_images in splits.items():
                split_dir = os.path.join(self.target_dir, split_name, category)
                
                for i, src_path in enumerate(split_images):
                    # Create new filename
                    ext = os.path.splitext(src_path)[1]
                    dst_filename = f"{i:06d}{ext}"
                    dst_path = os.path.join(split_dir, dst_filename)
                    
                    # Copy image
                    shutil.copy2(src_path, dst_path)
                
                split_stats[category][split_name] = len(split_images)
                print(f"  {category} {split_name}: {len(split_images)} images")
        
        return split_stats
    
    def create_enhanced_dataset(self):
        """Create enhanced dataset from scraped images"""
        print("🚀 Creating Enhanced Dataset")
        print("=" * 50)
        
        # Collect valid images
        valid_images = self.collect_valid_images()
        
        # Check if we have enough images
        min_images_per_category = 50
        insufficient_categories = []
        
        for category, images in valid_images.items():
            if len(images) < min_images_per_category:
                insufficient_categories.append(f"{category}: {len(images)}")
        
        if insufficient_categories:
            print("\n⚠️  Categories with insufficient images:")
            for cat_info in insufficient_categories:
                print(f"    {cat_info}")
            print(f"  Minimum recommended: {min_images_per_category} per category")
        
        # Create splits
        split_stats = self.create_splits(valid_images)
        
        # Save statistics
        stats = {
            'split_stats': split_stats,
            'total_by_category': {cat: len(imgs) for cat, imgs in valid_images.items()},
            'total_images': sum(len(imgs) for imgs in valid_images.values())
        }
        
        with open(os.path.join(self.target_dir, 'dataset_stats.json'), 'w') as f:
            json.dump(stats, f, indent=2)
        
        print("\n✅ Enhanced dataset created!")
        print(f"📊 Dataset statistics saved to: {os.path.join(self.target_dir, 'dataset_stats.json')}")
        
        return stats

def main():
    preparer = DatasetPreparer()
    stats = preparer.create_enhanced_dataset()
    
    print("\n📈 Dataset Summary:")
    print("=" * 30)
    
    total_train = sum(stats['split_stats'][cat].get('train', 0) for cat in stats['split_stats'])
    total_val = sum(stats['split_stats'][cat].get('val', 0) for cat in stats['split_stats'])
    total_test = sum(stats['split_stats'][cat].get('test', 0) for cat in stats['split_stats'])
    
    print(f"Training images: {total_train}")
    print(f"Validation images: {total_val}")
    print(f"Test images: {total_test}")
    print(f"Total images: {stats['total_images']}")
    
    print("\nNext steps:")
    print("1. Review the dataset quality")
    print("2. Run training: python pipeline.py")

if __name__ == "__main__":
    main()