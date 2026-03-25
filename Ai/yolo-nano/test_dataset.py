#!/usr/bin/env python3
"""
Test Dataset Loading
===================

Quick test to verify the dataset loads correctly before training.
"""

import sys
from pathlib import Path
import torch
from torch.utils.data import DataLoader

# Add utils to path
sys.path.append(str(Path(__file__).parent / 'utils'))

from utils.datasets import YOLODataset

def test_dataset():
    print("Testing YOLO Dataset Loading...")
    
    # Test paths
    train_path = "data/yolo_dataset/train"
    val_path = "data/yolo_dataset/val"
    
    print(f"Train path: {train_path}")
    print(f"Val path: {val_path}")
    
    try:
        # Create datasets
        train_dataset = YOLODataset(
            train_path,
            img_size=416,
            augment=True
        )
        
        val_dataset = YOLODataset(
            val_path,
            img_size=416,
            augment=False
        )
        
        print(f"✓ Train dataset: {len(train_dataset)} images")
        print(f"✓ Val dataset: {len(val_dataset)} images")
        
        # Test loading a single sample
        if len(train_dataset) > 0:
            image, targets = train_dataset[0]
            print(f"✓ Sample image shape: {image.shape}")
            print(f"✓ Sample targets shape: {targets.shape}")
            print(f"✓ Sample targets: {targets}")
        
        # Test dataloader
        train_loader = DataLoader(
            train_dataset,
            batch_size=2,
            shuffle=False,
            num_workers=0
        )
        
        print("✓ Testing dataloader...")
        for batch_idx, (images, targets) in enumerate(train_loader):
            print(f"✓ Batch {batch_idx}: images {images.shape}, targets {targets.shape}")
            if batch_idx >= 2:  # Test first 3 batches
                break
        
        print("✅ Dataset loading test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Dataset loading test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_dataset()