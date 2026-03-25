import os
import shutil
import yaml
from pathlib import Path
import random

def prepare_dataset(images_root, output_dir):
    # Create output directories
    dataset_dir = Path(output_dir)
    (dataset_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (dataset_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # Get all product folders
    images_root = Path(images_root)
    product_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('product_')]
    label_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('labels_')]
    
    # Create class mapping
    classes = []
    for folder in product_folders:
        class_name = folder.name.replace('product_', '').split('_', 1)[1] if '_' in folder.name else folder.name
        if class_name not in classes:
            classes.append(class_name)
    
    class_to_id = {cls: idx for idx, cls in enumerate(classes)}
    print(f"Found {len(classes)} classes: {classes}")
    
    # Process each product folder
    all_files = []
    for product_folder in product_folders:
        product_id = product_folder.name.split('_')[1]
        
        # Find corresponding label folder
        label_folder = None
        for lf in label_folders:
            if f'product_{product_id}_' in lf.name:
                label_folder = lf
                break
        
        if not label_folder:
            print(f"Warning: No labels found for {product_folder.name}")
            continue
        
        # Get class name and ID
        class_name = product_folder.name.replace('product_', '').split('_', 1)[1]
        class_id = class_to_id[class_name]
        
        # Process images and labels
        for label_file in label_folder.glob('*.txt'):
            img_file = None
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                potential_img = product_folder / f"{label_file.stem}{ext}"
                if potential_img.exists():
                    img_file = potential_img
                    break
            
            if img_file and img_file.exists():
                all_files.append((img_file, label_file, class_id))
    
    # Split into train/val (80/20)
    random.shuffle(all_files)
    split_idx = int(0.8 * len(all_files))
    train_files = all_files[:split_idx]
    val_files = all_files[split_idx:]
    
    print(f"Train: {len(train_files)} images, Val: {len(val_files)} images")
    
    # Copy files to train/val directories
    for files, split in [(train_files, 'train'), (val_files, 'val')]:
        for img_file, label_file, class_id in files:
            try:
                # Copy image
                dst_img = dataset_dir / 'images' / split / img_file.name
                shutil.copy2(img_file, dst_img)
                
                # Process and copy label
                dst_label = dataset_dir / 'labels' / split / f"{img_file.stem}.txt"
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                with open(dst_label, 'w') as f:
                    for line in lines:
                        line = line.strip()
                        if line:
                            parts = line.split()
                            if len(parts) >= 5:
                                parts[0] = str(class_id)
                                f.write(' '.join(parts) + '\n')
                            
            except Exception as e:
                print(f"Error processing {img_file}: {e}")
                continue
    
    # Create dataset.yaml
    dataset_yaml = {
        'path': str(dataset_dir.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes),
        'names': classes
    }
    
    with open(dataset_dir / 'dataset.yaml', 'w') as f:
        yaml.dump(dataset_yaml, f)
    
    print(f"Dataset prepared in: {dataset_dir}")
    return dataset_dir / 'dataset.yaml', classes

def main():
    # Configuration
    IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"
    DATASET_OUTPUT = r"c:\Users\boume\Briefs\Filrouge2A\Ai\data\custom_dataset"
    MODEL_SAVE_PATH = r"c:\Users\boume\Briefs\Filrouge2A\Ai\models\custom_yolo_model.pt"
    
    print("Starting YOLO dataset preparation...")
    
    # Prepare dataset
    dataset_yaml, classes = prepare_dataset(IMAGES_ROOT, DATASET_OUTPUT)
    
    print(f"\nDataset ready! Now run:")
    print(f"yolo detect train data={dataset_yaml} model=yolov8n.pt epochs=30 imgsz=640 batch=8 device=cpu project=runs/train name=custom_ceramic exist_ok=True")
    
    print(f"\nAfter training, copy the best model from runs/train/custom_ceramic/weights/best.pt to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()