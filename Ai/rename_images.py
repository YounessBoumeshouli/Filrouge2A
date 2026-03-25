#!/usr/bin/env python3
"""
Image Renamer for Product Dataset
=================================

Renames all images in the product_51 folder to follow the image_XX.jpg pattern
starting from image_20.jpg, while preserving existing numbered images.
"""

import os
import shutil
from pathlib import Path
import re

class ImageRenamer:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
    def get_all_images(self):
        """Get all image files in the folder"""
        images = []
        for file in self.folder_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                images.append(file)
        return images
    
    def parse_existing_numbers(self, images):
        """Find existing image_XX.jpg files and their numbers"""
        existing_numbers = set()
        pattern = re.compile(r'^image_(\d+)\.(jpg|jpeg|png|webp|bmp|tiff)$', re.IGNORECASE)
        
        for img in images:
            match = pattern.match(img.name)
            if match:
                number = int(match.group(1))
                existing_numbers.add(number)
        
        return existing_numbers
    
    def find_files_to_rename(self, images):
        """Find files that don't follow the image_XX.jpg pattern"""
        pattern = re.compile(r'^image_(\d+)\.(jpg|jpeg|png|webp|bmp|tiff)$', re.IGNORECASE)
        files_to_rename = []
        
        for img in images:
            if not pattern.match(img.name):
                files_to_rename.append(img)
        
        return files_to_rename
    
    def get_next_available_number(self, existing_numbers, start_from=20):
        """Get the next available number starting from start_from"""
        current = start_from
        while current in existing_numbers:
            current += 1
        return current
    
    def rename_images(self, start_number=20, dry_run=True):
        """Rename images to follow the pattern"""
        
        print(f"📁 Processing folder: {self.folder_path}")
        print(f"🔢 Starting from: image_{start_number}.jpg")
        print(f"{'🧪 DRY RUN MODE' if dry_run else '✅ ACTUAL RENAME'}")
        print("-" * 60)
        
        # Get all images
        all_images = self.get_all_images()
        print(f"📸 Found {len(all_images)} total images")
        
        if not all_images:
            print("❌ No images found in the folder!")
            return
        
        # Parse existing numbered images
        existing_numbers = self.parse_existing_numbers(all_images)
        print(f"🏷️ Found {len(existing_numbers)} images already following pattern")
        if existing_numbers:
            sorted_numbers = sorted(existing_numbers)
            print(f"   Existing numbers: {sorted_numbers}")
        
        # Find files that need renaming
        files_to_rename = self.find_files_to_rename(all_images)
        print(f"🔄 Found {len(files_to_rename)} images to rename")
        
        if not files_to_rename:
            print("✅ All images already follow the correct pattern!")
            return
        
        print("\nFiles to rename:")
        for i, file in enumerate(files_to_rename, 1):
            print(f"  {i:2d}. {file.name}")
        
        # Perform renaming
        print(f"\n{'Simulating' if dry_run else 'Performing'} renaming:")
        renamed_count = 0
        current_number = start_number
        
        for file in files_to_rename:
            # Find next available number
            while current_number in existing_numbers:
                current_number += 1
            
            # Determine new name (always save as .jpg)
            new_name = f"image_{current_number}.jpg"
            new_path = self.folder_path / new_name
            
            print(f"  {file.name} → {new_name}")
            
            if not dry_run:
                try:
                    # If the file is not already .jpg, convert it
                    if file.suffix.lower() != '.jpg':
                        from PIL import Image
                        img = Image.open(file)
                        if img.mode in ('RGBA', 'P', 'LA'):
                            img = img.convert('RGB')
                        img.save(new_path, 'JPEG', quality=90)
                        file.unlink()  # Remove original
                        print(f"    ✅ Converted and renamed")
                    else:
                        # Just rename
                        file.rename(new_path)
                        print(f"    ✅ Renamed")
                    
                    renamed_count += 1
                    existing_numbers.add(current_number)
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            current_number += 1
        
        print("-" * 60)
        if dry_run:
            print(f"🧪 DRY RUN COMPLETE")
            print(f"📊 Would rename {len(files_to_rename)} files")
            print(f"🔢 Would use numbers {start_number} to {current_number - 1}")
        else:
            print(f"✅ RENAMING COMPLETE")
            print(f"📊 Successfully renamed {renamed_count} files")
            print(f"🔢 Used numbers {start_number} to {current_number - 1}")
        
        return renamed_count if not dry_run else len(files_to_rename)
    
    def show_final_status(self):
        """Show final status of all images"""
        all_images = self.get_all_images()
        existing_numbers = self.parse_existing_numbers(all_images)
        
        print(f"\n📊 FINAL STATUS:")
        print(f"📸 Total images: {len(all_images)}")
        print(f"🏷️ Properly named: {len(existing_numbers)}")
        
        if existing_numbers:
            sorted_numbers = sorted(existing_numbers)
            print(f"🔢 Number range: {min(sorted_numbers)} to {max(sorted_numbers)}")
            
            # Check for gaps
            expected_range = set(range(min(sorted_numbers), max(sorted_numbers) + 1))
            gaps = expected_range - existing_numbers
            if gaps:
                print(f"⚠️ Missing numbers: {sorted(gaps)}")
            else:
                print(f"✅ No gaps in numbering")

def main():
    # Configuration
    FOLDER_PATH = r"c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca"
    START_NUMBER = 20
    
    print("🏺 Image Renamer for Product_51 Ceramic Cake Stands")
    print("=" * 60)
    
    # Check if folder exists
    if not Path(FOLDER_PATH).exists():
        print(f"❌ Folder not found: {FOLDER_PATH}")
        return
    
    # Initialize renamer
    renamer = ImageRenamer(FOLDER_PATH)
    
    # First, show current status
    print("📋 CURRENT STATUS:")
    all_images = renamer.get_all_images()
    existing_numbers = renamer.parse_existing_numbers(all_images)
    files_to_rename = renamer.find_files_to_rename(all_images)
    
    print(f"📸 Total images: {len(all_images)}")
    print(f"🏷️ Already properly named: {len(existing_numbers)}")
    print(f"🔄 Need renaming: {len(files_to_rename)}")
    
    if files_to_rename:
        print(f"\nFiles that need renaming:")
        for i, file in enumerate(files_to_rename, 1):
            print(f"  {i:2d}. {file.name}")
    
    if not files_to_rename:
        print("\n✅ All images already follow the correct pattern!")
        renamer.show_final_status()
        return
    
    # Perform dry run first
    print(f"\n" + "="*60)
    print("🧪 PERFORMING DRY RUN...")
    renamer.rename_images(start_number=START_NUMBER, dry_run=True)
    
    # Ask for confirmation
    print(f"\n" + "="*60)
    response = input("❓ Proceed with actual renaming? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n✅ PERFORMING ACTUAL RENAMING...")
        renamed_count = renamer.rename_images(start_number=START_NUMBER, dry_run=False)
        
        # Show final status
        renamer.show_final_status()
        
        print(f"\n🎉 Renaming completed!")
        print(f"📁 Folder: {FOLDER_PATH}")
        print(f"📊 Renamed: {renamed_count} files")
        
    else:
        print("\n⏹️ Renaming cancelled by user")

if __name__ == "__main__":
    main()