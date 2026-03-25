#!/usr/bin/env python3
"""
Tagine Image Renamer
===================

Renames all images in the product_2_Tagine folder to follow the image_XX.jpg pattern
starting from image_1.jpg. Also creates the corresponding labels folder structure.
"""

import os
import shutil
from pathlib import Path
import re
from PIL import Image

class TagineImageRenamer:
    def __init__(self, images_folder):
        self.images_folder = Path(images_folder)
        self.labels_folder = Path(str(images_folder).replace('product_2_Tagine', 'labels_product_2_Tagine'))
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        
    def get_all_images(self):
        """Get all image files in the folder"""
        images = []
        for file in self.images_folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.image_extensions:
                images.append(file)
        return sorted(images, key=lambda x: x.name.lower())  # Sort alphabetically
    
    def parse_existing_numbers(self, images):
        """Find existing image_XX files and their numbers"""
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
    
    def create_labels_folder(self):
        """Create the labels folder if it doesn't exist"""
        self.labels_folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 Labels folder ready: {self.labels_folder}")
    
    def convert_and_rename_images(self, start_number=1, dry_run=True):
        """Rename and convert images to JPG format"""
        
        print(f"🏺 Processing Tagine Images")
        print(f"📁 Images folder: {self.images_folder}")
        print(f"🏷️ Labels folder: {self.labels_folder}")
        print(f"🔢 Starting from: image_{start_number}.jpg")
        print(f"{'🧪 DRY RUN MODE' if dry_run else '✅ ACTUAL RENAME'}")
        print("-" * 70)
        
        # Check if folder exists
        if not self.images_folder.exists():
            print(f"❌ Images folder not found: {self.images_folder}")
            return 0
        
        # Create labels folder
        if not dry_run:
            self.create_labels_folder()
        
        # Get all images
        all_images = self.get_all_images()
        print(f"📸 Found {len(all_images)} total images")
        
        if not all_images:
            print("❌ No images found!")
            return 0
        
        # Parse existing numbered images
        existing_numbers = self.parse_existing_numbers(all_images)
        print(f"🔢 Found {len(existing_numbers)} images already following pattern")
        
        if existing_numbers:
            sorted_numbers = sorted(existing_numbers)
            print(f"   Existing numbers: {sorted_numbers}")
        
        # Find files that need renaming
        files_to_rename = self.find_files_to_rename(all_images)
        print(f"🔄 Found {len(files_to_rename)} images to rename")
        
        if not files_to_rename:
            print("✅ All images already follow the correct pattern!")
            return 0
        
        print(f"\nFirst 10 files to rename:")
        for i, file in enumerate(files_to_rename[:10], 1):
            print(f"  {i:2d}. {file.name}")
        if len(files_to_rename) > 10:
            print(f"  ... and {len(files_to_rename) - 10} more files")
        
        # Perform renaming
        print(f"\n{'Simulating' if dry_run else 'Performing'} renaming:")
        renamed_count = 0
        current_number = start_number
        
        # Skip existing numbers
        while current_number in existing_numbers:
            current_number += 1
        
        for i, file in enumerate(files_to_rename):
            # Find next available number
            while current_number in existing_numbers:
                current_number += 1
            
            # Determine new name (always save as .jpg)
            new_name = f"image_{current_number}.jpg"
            new_path = self.images_folder / new_name
            
            if i < 5 or not dry_run:  # Show first 5 in dry run, all in actual run
                print(f"  {file.name} → {new_name}")
            elif i == 5 and dry_run:
                print(f"  ... (showing first 5, {len(files_to_rename) - 5} more to process)")
            
            if not dry_run:
                try:
                    # Convert and save as JPG
                    if file.suffix.lower() != '.jpg':
                        img = Image.open(file)
                        if img.mode in ('RGBA', 'P', 'LA'):
                            img = img.convert('RGB')
                        img.save(new_path, 'JPEG', quality=90)
                        file.unlink()  # Remove original
                    else:
                        # Just rename if already JPG
                        file.rename(new_path)
                    
                    renamed_count += 1
                    existing_numbers.add(current_number)
                    
                except Exception as e:
                    print(f"    ❌ Error processing {file.name}: {e}")
            
            current_number += 1
        
        print("-" * 70)
        if dry_run:
            print(f"🧪 DRY RUN COMPLETE")
            print(f"📊 Would rename {len(files_to_rename)} files")
            print(f"🔢 Would use numbers {start_number} to {current_number - 1}")
            print(f"📁 Would create labels folder: {self.labels_folder}")
        else:
            print(f"✅ RENAMING COMPLETE")
            print(f"📊 Successfully renamed {renamed_count} files")
            print(f"🔢 Used numbers {start_number} to {current_number - 1}")
            print(f"📁 Labels folder created: {self.labels_folder}")
        
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
            if len(sorted_numbers) > 1:
                expected_range = set(range(min(sorted_numbers), max(sorted_numbers) + 1))
                gaps = expected_range - existing_numbers
                if gaps:
                    print(f"⚠️ Missing numbers: {sorted(gaps)}")
                else:
                    print(f"✅ No gaps in numbering")
        
        # Check labels folder
        if self.labels_folder.exists():
            label_files = list(self.labels_folder.glob('*.txt'))
            print(f"🏷️ Labels folder exists with {len(label_files)} label files")
        else:
            print(f"📁 Labels folder not created yet")

def main():
    # Configuration
    IMAGES_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_2_Tagine"
    START_NUMBER = 1
    
    print("🏺 Tagine Image Renamer")
    print("=" * 70)
    
    # Initialize renamer
    renamer = TagineImageRenamer(IMAGES_FOLDER)
    
    # Show current status
    print("📋 CURRENT STATUS:")
    all_images = renamer.get_all_images()
    existing_numbers = renamer.parse_existing_numbers(all_images)
    files_to_rename = renamer.find_files_to_rename(all_images)
    
    print(f"📸 Total images: {len(all_images)}")
    print(f"🔢 Already properly named: {len(existing_numbers)}")
    print(f"🔄 Need renaming: {len(files_to_rename)}")
    
    if existing_numbers:
        sorted_numbers = sorted(existing_numbers)
        print(f"🔢 Existing numbers: {sorted_numbers}")
    
    if not files_to_rename:
        print("\n✅ All images already follow the correct pattern!")
        renamer.show_final_status()
        return
    
    # Show some example files
    print(f"\nExample files that need renaming:")
    for i, file in enumerate(files_to_rename[:5], 1):
        print(f"  {i}. {file.name}")
    if len(files_to_rename) > 5:
        print(f"  ... and {len(files_to_rename) - 5} more")
    
    # Perform dry run first
    print(f"\n" + "="*70)
    print("🧪 PERFORMING DRY RUN...")
    renamer.convert_and_rename_images(start_number=START_NUMBER, dry_run=True)
    
    # Ask for confirmation
    print(f"\n" + "="*70)
    response = input("❓ Proceed with actual renaming? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n✅ PERFORMING ACTUAL RENAMING...")
        renamed_count = renamer.convert_and_rename_images(start_number=START_NUMBER, dry_run=False)
        
        # Show final status
        renamer.show_final_status()
        
        print(f"\n🎉 Renaming completed!")
        print(f"📁 Images folder: {IMAGES_FOLDER}")
        print(f"📊 Renamed: {renamed_count} files")
        print(f"🏷️ Labels folder created and ready for label files")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"1. Create label files (.txt) for each image in the labels folder")
        print(f"2. Each label file should contain bounding box coordinates")
        print(f"3. Use the same naming: image_1.txt, image_2.txt, etc.")
        
    else:
        print("\n⏹️ Renaming cancelled by user")

if __name__ == "__main__":
    main()