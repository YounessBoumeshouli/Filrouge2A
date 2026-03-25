#!/usr/bin/env python3
"""
Quick Dataset Analysis
=====================

Analyzes the current Marrakech dataset structure and provides statistics.

Usage:
    python analyze_dataset.py --dataset ../../marrakech_dataset_enhanced
"""

import os
import argparse
from pathlib import Path
from collections import Counter
import json

def analyze_dataset(dataset_path):
    """Analyze dataset structure and provide statistics"""
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        print(f"❌ Dataset path not found: {dataset_path}")
        return
    
    print(f"🔍 Analyzing dataset: {dataset_path}")
    print("=" * 60)
    
    # Find categories
    categories = []
    for item in dataset_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            categories.append(item.name)
    
    categories.sort()
    
    print(f"📊 Found {len(categories)} categories:")
    
    total_images = 0
    category_stats = {}
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif'}
    
    for category in categories:
        category_path = dataset_path / category
        
        # Count images (including subdirectories)
        image_count = 0
        subdirs = []
        
        for root, dirs, files in os.walk(category_path):
            # Track subdirectories
            if root != str(category_path):
                rel_path = Path(root).relative_to(category_path)
                if str(rel_path) not in subdirs:
                    subdirs.append(str(rel_path))
            
            # Count image files
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_count += 1
        
        category_stats[category] = {
            'image_count': image_count,
            'subdirectories': subdirs
        }
        
        total_images += image_count
        
        # Display category info
        print(f"  📂 {category}: {image_count} images")
        if subdirs:
            print(f"     └── Subdirectories: {', '.join(subdirs)}")
    
    print("=" * 60)
    print(f"📈 Total images: {total_images}")
    print(f"📋 Total categories: {len(categories)}")
    
    # Check for imbalanced classes
    print("\\n📊 Class Distribution:")
    counts = [stats['image_count'] for stats in category_stats.values()]
    min_count = min(counts)
    max_count = max(counts)
    avg_count = sum(counts) / len(counts)
    
    print(f"  📉 Minimum: {min_count} images")
    print(f"  📊 Average: {avg_count:.1f} images")
    print(f"  📈 Maximum: {max_count} images")
    
    if max_count > 3 * min_count:
        print("  ⚠️  Warning: Significant class imbalance detected!")
        print("     Consider data augmentation for smaller classes.")
    
    # Recommendations
    print("\\n💡 Recommendations:")
    
    # Check if any category needs more data
    for category, stats in category_stats.items():
        if stats['image_count'] < 100:
            print(f"  📈 {category}: Consider adding more images (current: {stats['image_count']})")
    
    # Check for train/val/test splits
    has_splits = False
    for category in categories:
        category_path = dataset_path / category
        subdirs = [d.name for d in category_path.iterdir() if d.is_dir()]
        if any(split in subdirs for split in ['train', 'val', 'test']):
            has_splits = True
            break
    
    if not has_splits:
        print("  🔄 Dataset needs to be split into train/val/test")
        print("     Run: python prepare_yolo_dataset.py")
    
    # Save analysis results
    analysis_results = {
        'dataset_path': str(dataset_path),
        'total_images': total_images,
        'num_categories': len(categories),
        'categories': categories,
        'category_stats': category_stats,
        'distribution': {
            'min_count': min_count,
            'max_count': max_count,
            'avg_count': avg_count
        },
        'has_splits': has_splits
    }
    
    output_file = dataset_path / 'dataset_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\\n📄 Analysis saved to: {output_file}")
    
    return analysis_results

def main():
    parser = argparse.ArgumentParser(description='Analyze Marrakech dataset structure')
    parser.add_argument('--dataset', type=str, default='../../marrakech_dataset_enhanced',
                       help='Path to dataset directory')
    
    args = parser.parse_args()
    
    print("🏺 Marrakech Dataset Analysis")
    print("=" * 60)
    
    analyze_dataset(args.dataset)

if __name__ == "__main__":
    main()