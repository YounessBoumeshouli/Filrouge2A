#!/usr/bin/env python3
"""
Data quality checker and improver for better model accuracy
"""

import os
import shutil
from PIL import Image
import numpy as np
from collections import defaultdict

def check_data_quality(data_dir="../data/price"):
    """Check and report data quality issues"""
    print("🔍 Checking data quality...")
    
    issues = []
    stats = defaultdict(int)
    
    for split in ['train', 'val', 'test']:
        split_path = os.path.join(data_dir, split)
        if not os.path.exists(split_path):
            issues.append(f"Missing {split} directory")
            continue
            
        for class_name in os.listdir(split_path):
            class_path = os.path.join(split_path, class_name)
            if not os.path.isdir(class_path):
                continue
                
            images = [f for f in os.listdir(class_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            stats[f"{split}_{class_name}"] = len(images)
            
            # Check for minimum images
            if len(images) < 10:
                issues.append(f"Too few images in {split}/{class_name}: {len(images)}")
            
            # Check image quality
            corrupted = 0
            for img_file in images[:5]:  # Sample check
                try:
                    img_path = os.path.join(class_path, img_file)
                    img = Image.open(img_path)
                    img.verify()
                except:
                    corrupted += 1
            
            if corrupted > 0:
                issues.append(f"Corrupted images in {split}/{class_name}: {corrupted}/5 sampled")
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    for key, count in sorted(stats.items()):
        print(f"  {key}: {count} images")
    
    # Print issues
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No major issues found")
    
    return len(issues) == 0

def improve_dataset():
    """Improve dataset by copying from marrakech_dataset"""
    source_dir = "../../marrakech_dataset"
    target_dir = "../data/price"
    
    if not os.path.exists(source_dir):
        print("❌ Source dataset not found")
        return False
    
    print("🔄 Improving dataset...")
    
    # Create directories
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(target_dir, split), exist_ok=True)
    
    # Process each class
    for class_name in os.listdir(source_dir):
        class_path = os.path.join(source_dir, class_name)
        if not os.path.isdir(class_path):
            continue
        
        print(f"📂 Processing {class_name}...")
        
        # Collect all images
        all_images = []
        for subdir in ['bing', 'google']:
            subdir_path = os.path.join(class_path, subdir)
            if os.path.exists(subdir_path):
                images = [os.path.join(subdir_path, f) for f in os.listdir(subdir_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                all_images.extend(images)
        
        # Filter valid images
        valid_images = []
        for img_path in all_images:
            try:
                img = Image.open(img_path)
                if img.size[0] > 50 and img.size[1] > 50:  # Minimum size
                    valid_images.append(img_path)
            except:
                continue
        
        if len(valid_images) < 20:
            print(f"  ⚠️  Only {len(valid_images)} valid images for {class_name}")
            continue
        
        # Split data: 70% train, 15% val, 15% test
        np.random.shuffle(valid_images)
        n_train = int(0.7 * len(valid_images))
        n_val = int(0.15 * len(valid_images))
        
        splits = {
            'train': valid_images[:n_train],
            'val': valid_images[n_train:n_train+n_val],
            'test': valid_images[n_train+n_val:]
        }
        
        # Copy images to splits
        for split, images in splits.items():
            split_class_dir = os.path.join(target_dir, split, class_name)
            os.makedirs(split_class_dir, exist_ok=True)
            
            for i, src_path in enumerate(images):
                ext = os.path.splitext(src_path)[1]
                dst_path = os.path.join(split_class_dir, f"{i:06d}{ext}")
                shutil.copy2(src_path, dst_path)
        
        print(f"  ✅ {class_name}: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['test'])} test")
    
    return True

if __name__ == "__main__":
    print("Data Quality Improvement")
    print("=" * 50)
    
    # Check current quality
    is_good = check_data_quality()
    
    if not is_good:
        print("\n🔧 Improving dataset...")
        if improve_dataset():
            print("\n✅ Dataset improved!")
            check_data_quality()
        else:
            print("\n❌ Failed to improve dataset")
    else:
        print("\n✅ Dataset quality is good!")