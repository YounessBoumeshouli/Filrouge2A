#!/usr/bin/env python3
"""
Fix Label Files
===============

Fixes label files that have literal \\n instead of actual newlines.
"""

import os
from pathlib import Path

def fix_label_files(dataset_dir):
    """Fix label files with literal \\n characters"""
    dataset_path = Path(dataset_dir)
    
    splits = ['train', 'val', 'test']
    total_fixed = 0
    
    for split in splits:
        labels_dir = dataset_path / split / 'labels'
        if not labels_dir.exists():
            continue
            
        print(f"Fixing {split} labels...")
        split_fixed = 0
        
        for label_file in labels_dir.glob('*.txt'):
            try:
                # Read the file
                with open(label_file, 'r') as f:
                    content = f.read()
                
                # Check if it has literal \\n
                if '\\n' in content:
                    # Replace literal \\n with actual newlines
                    fixed_content = content.replace('\\n', '\n')
                    
                    # Write back the fixed content
                    with open(label_file, 'w') as f:
                        f.write(fixed_content)
                    
                    split_fixed += 1
                    
            except Exception as e:
                print(f"Error fixing {label_file}: {e}")
        
        print(f"  Fixed {split_fixed} files in {split}")
        total_fixed += split_fixed
    
    print(f"Total files fixed: {total_fixed}")

if __name__ == "__main__":
    dataset_dir = "data/yolo_dataset"
    print("🔧 Fixing label files...")
    fix_label_files(dataset_dir)
    print("✅ Label files fixed!")