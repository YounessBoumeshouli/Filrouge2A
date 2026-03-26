#!/usr/bin/env python3
"""
Dataset Diagnostic Script
========================

Check the integrity of your dataset before training.
"""

from pathlib import Path

def check_dataset(images_root):
    """Check dataset integrity and report issues"""
    
    images_root = Path(images_root)
    
    # Get all product and label folders
    product_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('product_')]
    label_folders = [f for f in images_root.iterdir() if f.is_dir() and f.name.startswith('labels_')]
    
    print(f"Found {len(product_folders)} product folders")
    print(f"Found {len(label_folders)} label folders")
    print()
    
    total_images = 0
    total_labels = 0
    matched_pairs = 0
    issues = []
    
    for product_folder in product_folders:
        product_id = product_folder.name.split('_')[1]
        
        # Find corresponding label folder
        label_folder = None
        for lf in label_folders:
            if f'product_{product_id}_' in lf.name:
                label_folder = lf
                break
        
        if not label_folder:
            issues.append(f"No labels found for {product_folder.name}")
            continue
        
        print(f"Checking {product_folder.name} <-> {label_folder.name}")
        
        # Get all images
        images = []
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            images.extend(list(product_folder.glob(f'*{ext}')))
        
        # Get all labels
        labels = list(label_folder.glob('*.txt'))
        
        print(f"  Images: {len(images)}")
        print(f"  Labels: {len(labels)}")
        
        total_images += len(images)
        total_labels += len(labels)
        
        # Check for matching pairs
        matched = 0
        for label_file in labels:
            # Find corresponding image
            img_found = False
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                potential_img = product_folder / f"{label_file.stem}{ext}"
                if potential_img.exists():
                    img_found = True
                    matched += 1
                    break
            
            if not img_found:
                issues.append(f"No image found for label {label_file.name} in {product_folder.name}")
        
        matched_pairs += matched
        print(f"  Matched pairs: {matched}")
        
        # Check label format
        for label_file in labels:
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) < 5:
                        issues.append(f"Invalid label format in {label_file.name} line {i+1}: {line}")
                    else:
                        # Check if coordinates are valid (0-1 range)
                        try:
                            coords = [float(x) for x in parts[1:5]]
                            if not all(0 <= x <= 1 for x in coords):
                                issues.append(f"Invalid coordinates in {label_file.name} line {i+1}: {line}")
                        except ValueError:
                            issues.append(f"Non-numeric coordinates in {label_file.name} line {i+1}: {line}")
            except Exception as e:
                issues.append(f"Error reading {label_file.name}: {e}")
        
        print()
    
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total images: {total_images}")
    print(f"Total labels: {total_labels}")
    print(f"Matched pairs: {matched_pairs}")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\nISSUES:")
        for issue in issues[:20]:  # Show first 20 issues
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more issues")
    else:
        print("\nNo issues found! Dataset looks good.")
    
    return len(issues) == 0

def main():
    # IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"

    IMAGES_ROOT = Path(__file__).parent / "images"

    print("Checking dataset integrity...")
    print(f"Images root: {IMAGES_ROOT}")
    print()
    
    is_valid = check_dataset(IMAGES_ROOT)
    
    if is_valid:
        print("\n✅ Dataset is ready for training!")
    else:
        print("\n❌ Dataset has issues that need to be fixed before training.")

if __name__ == "__main__":
    main()