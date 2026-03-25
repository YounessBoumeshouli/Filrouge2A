#!/usr/bin/env python3
"""
Combine existing dataset with newly scraped data for maximum training benefit
"""

import os
import shutil
import json
from pathlib import Path

def combine_datasets():
    """Combine existing and enhanced datasets"""
    
    existing_dir = "../data/price"
    enhanced_dir = "../data/price_enhanced" 
    combined_dir = "../data/price_combined"
    
    print("🔄 Combining datasets...")
    print(f"  Existing: {existing_dir}")
    print(f"  Enhanced: {enhanced_dir}")
    print(f"  Combined: {combined_dir}")
    
    # Create combined directory structure
    for split in ['train', 'val', 'test']:
        for category in ['argan', 'crafts', 'jewelry', 'lanterns', 'leather', 'price_tags', 'spices', 'textiles']:
            os.makedirs(os.path.join(combined_dir, split, category), exist_ok=True)
    
    stats = {'train': {}, 'val': {}, 'test': {}}
    
    for split in ['train', 'val', 'test']:
        for category in ['argan', 'crafts', 'jewelry', 'lanterns', 'leather', 'price_tags', 'spices', 'textiles']:
            combined_count = 0
            
            # Copy from existing dataset
            existing_path = os.path.join(existing_dir, split, category)
            if os.path.exists(existing_path):
                for img_file in os.listdir(existing_path):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        src = os.path.join(existing_path, img_file)
                        dst = os.path.join(combined_dir, split, category, f"orig_{img_file}")
                        shutil.copy2(src, dst)
                        combined_count += 1
            
            # Copy from enhanced dataset
            enhanced_path = os.path.join(enhanced_dir, split, category)
            if os.path.exists(enhanced_path):
                for img_file in os.listdir(enhanced_path):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        src = os.path.join(enhanced_path, img_file)
                        dst = os.path.join(combined_dir, split, category, f"new_{img_file}")
                        shutil.copy2(src, dst)
                        combined_count += 1
            
            stats[split][category] = combined_count
            print(f"  {split}/{category}: {combined_count} images")
    
    # Save combined stats
    total_stats = {
        'combined_stats': stats,
        'total_by_split': {
            split: sum(stats[split].values()) for split in stats
        },
        'total_images': sum(sum(stats[split].values()) for split in stats)
    }
    
    with open(os.path.join(combined_dir, 'combined_stats.json'), 'w') as f:
        json.dump(total_stats, f, indent=2)
    
    print(f"\n📊 Combined Dataset Summary:")
    print(f"  Training: {total_stats['total_by_split']['train']} images")
    print(f"  Validation: {total_stats['total_by_split']['val']} images") 
    print(f"  Test: {total_stats['total_by_split']['test']} images")
    print(f"  Total: {total_stats['total_images']} images")
    
    return combined_dir

if __name__ == "__main__":
    combined_dir = combine_datasets()
    print(f"\n✅ Combined dataset created at: {combined_dir}")
    print("\nNext: Train with combined data for best results!")