#!/usr/bin/env python3
"""
Dataset Diagnostic Script
========================

Check the integrity of your dataset before training.
"""

from pathlib import Path
import os

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
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:\n                potential_img = product_folder / f\"{label_file.stem}{ext}\"\n                if potential_img.exists():\n                    img_found = True\n                    matched += 1\n                    break\n            \n            if not img_found:\n                issues.append(f\"No image found for label {label_file.name} in {product_folder.name}\")\n        \n        matched_pairs += matched\n        print(f\"  Matched pairs: {matched}\")\n        \n        # Check label format\n        for label_file in labels:\n            try:\n                with open(label_file, 'r') as f:\n                    lines = f.readlines()\n                for i, line in enumerate(lines):\n                    line = line.strip()\n                    if not line:\n                        continue\n                    parts = line.split()\n                    if len(parts) < 5:\n                        issues.append(f\"Invalid label format in {label_file.name} line {i+1}: {line}\")\n                    else:\n                        # Check if coordinates are valid (0-1 range)\n                        try:\n                            coords = [float(x) for x in parts[1:5]]\n                            if not all(0 <= x <= 1 for x in coords):\n                                issues.append(f\"Invalid coordinates in {label_file.name} line {i+1}: {line}\")\n                        except ValueError:\n                            issues.append(f\"Non-numeric coordinates in {label_file.name} line {i+1}: {line}\")\n            except Exception as e:\n                issues.append(f\"Error reading {label_file.name}: {e}\")\n        \n        print()\n    \n    print(\"=\" * 50)\n    print(\"SUMMARY\")\n    print(\"=\" * 50)\n    print(f\"Total images: {total_images}\")\n    print(f\"Total labels: {total_labels}\")\n    print(f\"Matched pairs: {matched_pairs}\")\n    print(f\"Issues found: {len(issues)}\")\n    \n    if issues:\n        print(\"\\nISSUES:\")\n        for issue in issues[:20]:  # Show first 20 issues\n            print(f\"  - {issue}\")\n        if len(issues) > 20:\n            print(f\"  ... and {len(issues) - 20} more issues\")\n    else:\n        print(\"\\nNo issues found! Dataset looks good.\")\n    \n    return len(issues) == 0\n\ndef main():\n    IMAGES_ROOT = r\"c:\\Users\\boume\\Briefs\\Filrouge2A\\images\"\n    \n    print(\"Checking dataset integrity...\")\n    print(f\"Images root: {IMAGES_ROOT}\")\n    print()\n    \n    is_valid = check_dataset(IMAGES_ROOT)\n    \n    if is_valid:\n        print(\"\\n✅ Dataset is ready for training!\")\n    else:\n        print(\"\\n❌ Dataset has issues that need to be fixed before training.\")\n\nif __name__ == \"__main__\":\n    main()