"""
Prepare dataset in YOLO format
"""

import os
import shutil
from pathlib import Path
import json
import random

def prepare_yolo_dataset(source_dir, output_dir, train_ratio=0.8, val_ratio=0.1):
    """
    Prepare dataset in YOLO format
    
    Args:
        source_dir: Source directory with images organized by class
        output_dir: Output directory for YOLO format
        train_ratio: Ratio for training set
        val_ratio: Ratio for validation set
    """
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Create output directories
    for split in ['train', 'val', 'test']:
        (output_path / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Class mapping
    classes = {
        'argan': 0, 'crafts': 1, 'jewelry': 2, 'lanterns': 3,
        'leather': 4, 'spices': 5, 'textiles': 6,
        'jemaa_el_fnaa': 7, 'koutoubia_mosque': 8, 'bahia_palace': 9,
        'saadian_tombs': 10, 'ben_youssef_madrasa': 11, 'majorelle_garden': 12,
        'menara_gardens': 13, 'el_badi_palace': 14, 'agdal_gardens': 15,
        'marrakech_medina': 16
    }
    
    # Collect all images
    all_images = []
    for class_name, class_id in classes.items():
        class_dir = source_path / class_name
        if class_dir.exists():
            for source_file in class_dir.rglob('*.jpg'):
                all_images.append((source_file, class_id, class_name))
            for source_file in class_dir.rglob('*.png'):
                all_images.append((source_file, class_id, class_name))
    
    # Shuffle and split
    random.shuffle(all_images)
    total = len(all_images)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    
    train_images = all_images[:train_count]
    val_images = all_images[train_count:train_count + val_count]
    test_images = all_images[train_count + val_count:]
    
    # Copy images and create labels
    for split, images in [('train', train_images), ('val', val_images), ('test', test_images)]:
        for src_file, class_id, class_name in images:
            # Copy image
            dst_file = output_path / split / 'images' / src_file.name
            shutil.copy2(src_file, dst_file)
            
            # Create label file (simple format: class_id x_center y_center width height)
            # For now, create a full-image bounding box
            label_file = output_path / split / 'labels' / (src_file.stem + '.txt')
            with open(label_file, 'w') as f:
                # Full image bounding box (normalized)
                f.write(f'{class_id} 0.5 0.5 1.0 1.0\n')
    
    # Create dataset.yaml
    dataset_yaml = f"""path: {output_path}
train: train/images
val: val/images
test: test/images

nc: 17
names: {list(classes.keys())}
"""
    
    with open(output_path / 'dataset.yaml', 'w') as f:
        f.write(dataset_yaml)
    
    print(f"Dataset prepared:")
    print(f"  Train: {len(train_images)} images")
    print(f"  Val: {len(val_images)} images")
    print(f"  Test: {len(test_images)} images")
    print(f"  Output: {output_path}")

if __name__ == '__main__':
    # Prepare dataset from marrakech_dataset_enhanced
    source = '../../marrakech_dataset_enhanced'
    output = './data'
    
    prepare_yolo_dataset(source, output)
