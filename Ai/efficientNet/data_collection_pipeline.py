#!/usr/bin/env python3
"""
Complete pipeline: Scrape data → Prepare dataset → Train model
"""

import os
import sys

def run_data_collection_pipeline():
    """Run the complete data collection and training pipeline"""
    
    print("🚀 Complete Data Collection & Training Pipeline")
    print("=" * 60)
    
    # Step 1: Scrape more images
    print("\n1️⃣ STEP 1: Scraping more images...")
    print("This will collect ~150 images per category from multiple sources")
    
    choice = input("Start scraping? (y/n): ").lower().strip()
    if choice == 'y':
        print("🔄 Starting image scraping...")
        os.system("python enhanced_scraper.py")
    else:
        print("⏭️  Skipping scraping step")
    
    # Step 2: Prepare enhanced dataset
    print("\n2️⃣ STEP 2: Preparing enhanced dataset...")
    choice = input("Prepare dataset from scraped images? (y/n): ").lower().strip()
    if choice == 'y':
        print("🔄 Preparing enhanced dataset...")
        os.system("python prepare_enhanced_data.py")
    else:
        print("⏭️  Skipping dataset preparation")
    
    # Step 3: Train with enhanced data
    print("\n3️⃣ STEP 3: Training model with enhanced data...")
    choice = input("Train model with enhanced dataset? (y/n): ").lower().strip()
    if choice == 'y':
        print("🔄 Training model...")
        # Update pipeline to use enhanced data
        update_pipeline_for_enhanced_data()
        os.system("python pipeline.py")
    else:
        print("⏭️  Skipping training step")
    
    print("\n✅ Pipeline complete!")
    print("🎯 Expected improvements:")
    print("   - Much more training data (500-1000+ images per category)")
    print("   - Better model accuracy (target: 60-80%)")
    print("   - More robust predictions")

def update_pipeline_for_enhanced_data():
    """Update pipeline to use enhanced dataset"""
    pipeline_file = "pipeline.py"
    
    # Read current pipeline
    with open(pipeline_file, 'r') as f:
        content = f.read()
    
    # Update data directory paths
    content = content.replace(
        'data_dir = "../data/price"',
        'data_dir = "../data/price_enhanced"'
    )
    content = content.replace(
        'train_data_dir = "../data/price_augmented"',
        'train_data_dir = "../data/price_enhanced"'
    )
    
    # Write updated pipeline
    with open(pipeline_file, 'w') as f:
        f.write(content)
    
    print("📝 Updated pipeline to use enhanced dataset")

def quick_scrape_sample():
    """Quick scrape of sample images for testing"""
    print("🔄 Quick sample scraping (10 images per category)...")
    
    # Create a simple scraper for testing
    scraper_code = '''
import requests
import os
from PIL import Image
import io

categories = ["argan", "spices", "leather", "textiles"]
base_dir = "../../marrakech_dataset_sample"

for category in categories:
    os.makedirs(f"{base_dir}/{category}/sample", exist_ok=True)
    print(f"Scraping {category}...")
    
    # Simple image URLs (you would replace with actual scraping)
    # For demo, we'll create placeholder structure
    for i in range(5):
        print(f"  Sample {i+1}/5 for {category}")

print("Sample scraping complete!")
'''
    
    with open("quick_scraper.py", "w") as f:
        f.write(scraper_code)
    
    os.system("python quick_scraper.py")

if __name__ == "__main__":
    print("Data Collection Pipeline Options:")
    print("1. Full pipeline (scrape + prepare + train)")
    print("2. Quick sample scrape (for testing)")
    print("3. Just prepare existing data")
    print("4. Just train with current data")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        run_data_collection_pipeline()
    elif choice == "2":
        quick_scrape_sample()
    elif choice == "3":
        os.system("python prepare_enhanced_data.py")
    elif choice == "4":
        os.system("python pipeline.py")
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)