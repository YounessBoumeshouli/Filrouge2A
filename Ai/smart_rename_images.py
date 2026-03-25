#!/usr/bin/env python3
"""
Smart Image Renamer with Label Validation
=========================================

Renames images in product_1_Ceramic Vase folder only if they have corresponding
label files. Preserves existing numbered images and continues from the highest number.
"""

import os
import shutil
from pathlib import Path
import re

class SmartImageRenamer:
    def __init__(self, images_folder, labels_folder):
        self.images_folder = Path(images_folder)
        self.labels_folder = Path(labels_folder)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
    def get_all_images(self):
        """Get all image files in the folder"""
        images = []
        for file in self.images_folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                images.append(file)
        return images
    
    def get_all_labels(self):
        """Get all label files in the labels folder"""
        labels = []
        for file in self.labels_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.txt':
                labels.append(file)
        return labels
    
    def has_corresponding_label(self, image_file):
        """Check if an image has a corresponding label file"""
        image_stem = image_file.stem  # filename without extension
        label_file = self.labels_folder / f"{image_stem}.txt"
        return label_file.exists()
    
    def parse_existing_numbers(self, images):
        """Find existing image_XX files and their numbers"""
        existing_numbers = set()
        pattern = re.compile(r'^image_(\d+)$')
        
        for img in images:
            match = pattern.match(img.stem)  # Use stem to ignore extension
            if match:
                number = int(match.group(1))
                existing_numbers.add(number)
        
        return existing_numbers
    
    def find_files_to_rename(self, images):
        """Find files that don't follow the image_XX pattern AND have labels"""
        pattern = re.compile(r'^image_(\d+)$')
        files_to_rename = []
        
        for img in images:
            # Check if it doesn't follow the pattern
            if not pattern.match(img.stem):
                # Check if it has a corresponding label
                if self.has_corresponding_label(img):
                    files_to_rename.append(img)
                else:
                    print(f"⚠️ Skipping {img.name} - no corresponding label file")
        
        return files_to_rename
    
    def get_next_start_number(self, existing_numbers):
        """Get the next number after the highest existing number"""
        if not existing_numbers:
            return 1  # Start from 1 if no existing numbered images
        return max(existing_numbers) + 1
    
    def rename_images_and_labels(self, dry_run=True):
        """Rename images and their corresponding labels"""
        
        print(f"📁 Images folder: {self.images_folder}")
        print(f"🏷️ Labels folder: {self.labels_folder}")
        print(f"{'🧪 DRY RUN MODE' if dry_run else '✅ ACTUAL RENAME'}")
        print("-" * 70)
        
        # Check if folders exist
        if not self.images_folder.exists():
            print(f"❌ Images folder not found: {self.images_folder}")
            return 0
        
        if not self.labels_folder.exists():
            print(f"❌ Labels folder not found: {self.labels_folder}")
            return 0
        
        # Get all images and labels
        all_images = self.get_all_images()
        all_labels = self.get_all_labels()
        
        print(f"📸 Found {len(all_images)} total images")
        print(f"🏷️ Found {len(all_labels)} total labels")
        
        if not all_images:
            print("❌ No images found!")
            return 0
        
        # Parse existing numbered images
        existing_numbers = self.parse_existing_numbers(all_images)
        print(f"🔢 Found {len(existing_numbers)} images already following pattern")
        
        if existing_numbers:
            sorted_numbers = sorted(existing_numbers)
            print(f"   Existing numbers: {sorted_numbers}")
            start_number = max(existing_numbers) + 1
        else:
            start_number = 1
        
        print(f"🚀 Will start renaming from: image_{start_number}")
        
        # Find files that need renaming (and have labels)
        files_to_rename = self.find_files_to_rename(all_images)
        print(f"🔄 Found {len(files_to_rename)} images to rename (with labels)")
        
        if not files_to_rename:
            print("✅ No images need renaming (all are either properly named or missing labels)!")
            return 0
        
        print(f"\nImages to rename (with their labels):")
        for i, file in enumerate(files_to_rename, 1):
            label_file = self.labels_folder / f"{file.stem}.txt"
            print(f"  {i:2d}. {file.name} + {label_file.name}")
        
        # Perform renaming
        print(f"\n{'Simulating' if dry_run else 'Performing'} renaming:")
        renamed_count = 0
        current_number = start_number
        
        for file in files_to_rename:
            # Determine new names
            new_image_name = f"image_{current_number}{file.suffix}"
            new_label_name = f"image_{current_number}.txt"
            
            new_image_path = self.images_folder / new_image_name
            new_label_path = self.labels_folder / new_label_name
            
            old_label_path = self.labels_folder / f"{file.stem}.txt"
            
            print(f"  📸 {file.name} → {new_image_name}")
            print(f"  🏷️ {old_label_path.name} → {new_label_name}")
            
            if not dry_run:
                try:
                    # Rename image
                    file.rename(new_image_path)
                    
                    # Rename corresponding label
                    if old_label_path.exists():
                        old_label_path.rename(new_label_path)
                        print(f"    ✅ Renamed both image and label")
                    else:
                        print(f"    ⚠️ Label file not found: {old_label_path.name}")
                    
                    renamed_count += 1
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            current_number += 1
        
        print("-" * 70)
        if dry_run:
            print(f"🧪 DRY RUN COMPLETE")
            print(f"📊 Would rename {len(files_to_rename)} image-label pairs")
            print(f"🔢 Would use numbers {start_number} to {current_number - 1}")
        else:
            print(f"✅ RENAMING COMPLETE")
            print(f"📊 Successfully renamed {renamed_count} image-label pairs")
            print(f"🔢 Used numbers {start_number} to {current_number - 1}")
        
        return renamed_count if not dry_run else len(files_to_rename)
    
    def show_final_status(self):
        """Show final status of all images and labels"""
        all_images = self.get_all_images()
        all_labels = self.get_all_labels()
        existing_numbers = self.parse_existing_numbers(all_images)
        
        print(f"\n📊 FINAL STATUS:")
        print(f"📸 Total images: {len(all_images)}")
        print(f"🏷️ Total labels: {len(all_labels)}")
        print(f"🔢 Properly numbered images: {len(existing_numbers)}")
        
        if existing_numbers:
            sorted_numbers = sorted(existing_numbers)
            print(f"🔢 Number range: {min(sorted_numbers)} to {max(sorted_numbers)}")
        
        # Check for orphaned files
        orphaned_images = []
        orphaned_labels = []
        
        for img in all_images:
            if not self.has_corresponding_label(img):
                orphaned_images.append(img.name)
        
        for label in all_labels:
            image_exists = False
            for ext in self.image_extensions:
                if (self.images_folder / f"{label.stem}{ext}").exists():
                    image_exists = True
                    break
            if not image_exists:
                orphaned_labels.append(label.name)
        
        if orphaned_images:
            print(f"⚠️ Images without labels: {len(orphaned_images)}")
            for img in orphaned_images[:5]:  # Show first 5
                print(f"   - {img}")
            if len(orphaned_images) > 5:
                print(f"   ... and {len(orphaned_images) - 5} more")
        
        if orphaned_labels:
            print(f"⚠️ Labels without images: {len(orphaned_labels)}")
            for lbl in orphaned_labels[:5]:  # Show first 5
                print(f"   - {lbl}")
            if len(orphaned_labels) > 5:
                print(f"   ... and {len(orphaned_labels) - 5} more")

def main():
    # Configuration
    IMAGES_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_1_Ceramic Vase"
    LABELS_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\labels_product_1_Ceramic Vase"
    
    print("🏺 Smart Image Renamer for Product_1 Ceramic Vase")
    print("=" * 70)
    
    # Initialize renamer
    renamer = SmartImageRenamer(IMAGES_FOLDER, LABELS_FOLDER)
    
    # Show current status
    print("📋 CURRENT STATUS:")
    all_images = renamer.get_all_images()
    all_labels = renamer.get_all_labels()
    existing_numbers = renamer.parse_existing_numbers(all_images)
    files_to_rename = renamer.find_files_to_rename(all_images)
    
    print(f"📸 Total images: {len(all_images)}")
    print(f"🏷️ Total labels: {len(all_labels)}")
    print(f"🔢 Already properly named: {len(existing_numbers)}")
    print(f"🔄 Need renaming (with labels): {len(files_to_rename)}")
    
    if existing_numbers:
        sorted_numbers = sorted(existing_numbers)
        print(f"🔢 Existing numbers: {sorted_numbers}")
        next_number = max(existing_numbers) + 1
        print(f"🚀 Next available number: {next_number}")
    
    if not files_to_rename:
        print("\n✅ No images need renaming!")
        renamer.show_final_status()
        return
    
    # Perform dry run first
    print(f"\n" + "="*70)
    print("🧪 PERFORMING DRY RUN...")
    renamer.rename_images_and_labels(dry_run=True)
    
    # Ask for confirmation
    print(f"\n" + "="*70)
    response = input("❓ Proceed with actual renaming? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n✅ PERFORMING ACTUAL RENAMING...")
        renamed_count = renamer.rename_images_and_labels(dry_run=False)
        
        # Show final status
        renamer.show_final_status()
        
        print(f"\n🎉 Renaming completed!")
        print(f"📁 Images folder: {IMAGES_FOLDER}")
        print(f"🏷️ Labels folder: {LABELS_FOLDER}")
        print(f"📊 Renamed: {renamed_count} image-label pairs")
        
    else:
        print("\n⏹️ Renaming cancelled by user")

if __name__ == "__main__":
    main()