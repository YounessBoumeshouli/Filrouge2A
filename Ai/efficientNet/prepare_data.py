import os
import shutil
from pathlib import Path
import json

def prepare_dataset(source_dir, output_dir, train_split=0.7, val_split=0.15):
    """
    Organize images into train/val/test directories by class
    """
    os.makedirs(output_dir, exist_ok=True)
    
    classes = {}
    
    # Scan source directory
    for class_name in os.listdir(source_dir):
        class_path = os.path.join(source_dir, class_name)
        if not os.path.isdir(class_path):
            continue
        
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not images:
            continue
        
        classes[class_name] = len(images)
        
        # Create directories
        for split in ['train', 'val', 'test']:
            split_dir = os.path.join(output_dir, split, class_name)
            os.makedirs(split_dir, exist_ok=True)
        
        # Split images
        train_count = int(len(images) * train_split)
        val_count = int(len(images) * val_split)
        
        for i, img in enumerate(images):
            src = os.path.join(class_path, img)
            
            if i < train_count:
                dst = os.path.join(output_dir, 'train', class_name, img)
            elif i < train_count + val_count:
                dst = os.path.join(output_dir, 'val', class_name, img)
            else:
                dst = os.path.join(output_dir, 'test', class_name, img)
            
            shutil.copy2(src, dst)
    
    # Save dataset info
    info = {
        "classes": classes,
        "total_images": sum(classes.values()),
        "splits": {
            "train": train_split,
            "val": val_split,
            "test": 1 - train_split - val_split
        }
    }
    
    with open(os.path.join(output_dir, 'dataset_info.json'), 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"Dataset prepared: {info['total_images']} images")
    print(f"Classes: {list(classes.keys())}")
    
    return info

if __name__ == "__main__":
    source = "../data/marrakech_raw"
    output = "../data/marrakech"
    
    if os.path.exists(source):
        prepare_dataset(source, output)
    else:
        print(f"Source directory {source} not found.")