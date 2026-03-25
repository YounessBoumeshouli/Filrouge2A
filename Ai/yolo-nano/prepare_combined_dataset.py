#!/usr/bin/env python3
"""
Combined Dataset Preparation
===========================

Combines the main marrakech_dataset (with more images) and the enhanced dataset
(with price_tags category) to create the best possible training dataset.

Usage:
    python prepare_combined_dataset.py
"""

import os
import shutil
from pathlib import Path
import json

def combine_datasets():
    """Combine main and enhanced datasets"""
    print("🔄 Combining datasets for optimal training data...")
    print("=" * 60)
    
    # Paths
    main_dataset = Path("../../marrakech_dataset")
    enhanced_dataset = Path("../../marrakech_dataset_enhanced")
    output_dataset = Path("data/combined_dataset")
    
    # Create output directory
    output_dataset.mkdir(parents=True, exist_ok=True)
    
    # Categories from main dataset (larger numbers)
    main_categories = ['argan', 'crafts', 'jewelry', 'lanterns', 'leather', 'spices', 'textiles']
    
    # Copy from main dataset
    print("📂 Copying from main dataset...")
    for category in main_categories:
        src_path = main_dataset / category
        dst_path = output_dataset / category
        
        if src_path.exists():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
            
            # Count images
            image_count = count_images(dst_path)
            print(f"  ✅ {category}: {image_count} images")
    
    # Add price_tags from enhanced dataset
    print("\\n📂 Adding price_tags from enhanced dataset...")
    price_tags_src = enhanced_dataset / "price_tags"
    price_tags_dst = output_dataset / "price_tags"
    
    if price_tags_src.exists():
        if price_tags_dst.exists():
            shutil.rmtree(price_tags_dst)
        shutil.copytree(price_tags_src, price_tags_dst)
        
        image_count = count_images(price_tags_dst)
        print(f"  ✅ price_tags: {image_count} images")
    
    # Final statistics
    print("\\n" + "=" * 60)
    print("📊 Combined Dataset Statistics:")
    
    total_images = 0
    categories = []
    
    for category_path in output_dataset.iterdir():
        if category_path.is_dir():
            category = category_path.name
            categories.append(category)
            image_count = count_images(category_path)
            total_images += image_count
            print(f"  📂 {category}: {image_count} images")
    
    print(f"\\n📈 Total images: {total_images}")
    print(f"📋 Total categories: {len(categories)}")
    print(f"📁 Output directory: {output_dataset}")
    
    # Save metadata
    metadata = {
        "source_datasets": [str(main_dataset), str(enhanced_dataset)],
        "output_dataset": str(output_dataset),
        "total_images": total_images,
        "categories": sorted(categories),
        "category_counts": {cat: count_images(output_dataset / cat) for cat in categories}
    }
    
    metadata_file = output_dataset / "combination_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📄 Metadata saved: {metadata_file}")
    print("=" * 60)
    
    return str(output_dataset)

def count_images(directory):
    """Count images in a directory (including subdirectories)"""
    count = 0
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif'}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in image_extensions:
                count += 1
    
    return count

def main():
    print("🏺 Combined Dataset Preparation")
    print("=" * 60)
    
    # Combine datasets
    combined_path = combine_datasets()
    
    print("\\n🎯 Next steps:")
    print("1. Run dataset analysis:")
    print(f"   python analyze_dataset.py --dataset {combined_path}")
    print("2. Prepare YOLO dataset:")
    print(f"   python prepare_yolo_dataset.py --source {combined_path} --output data/yolo_dataset")
    print("3. Start training:")
    print("   python train.py --data data/yolo_dataset/dataset.yaml")

if __name__ == "__main__":
    main()