#!/usr/bin/env python3
"""
Quick model retraining script for better accuracy
"""

import os
import sys

def retrain_model():
    """Retrain the model with improved settings"""
    print("🚀 Starting Model Retraining Process")
    print("=" * 50)
    
    # Step 1: Improve data quality
    print("\n1️⃣ Checking and improving data quality...")
    os.system("python improve_data.py")
    
    # Step 2: Train improved model
    print("\n2️⃣ Training improved model...")
    os.system("python train_improved.py")
    
    # Step 3: Test the new model
    print("\n3️⃣ Testing new model...")
    
    # Update the classifier to use the new model
    update_classifier_code = '''
# Update improved_classifier.py to use new model
import os
import shutil

# Backup old model
if os.path.exists("../models/price_efficientnet_finetuned.h5"):
    shutil.copy("../models/price_efficientnet_finetuned.h5", "../models/price_efficientnet_finetuned_backup.h5")

# Use new improved model
if os.path.exists("../models/price_efficientnet_finetuned_improved.h5"):
    shutil.copy("../models/price_efficientnet_finetuned_improved.h5", "../models/price_efficientnet_finetuned.h5")
    print("✅ Updated to use improved model")
else:
    print("❌ Improved model not found")
'''
    
    exec(update_classifier_code)
    
    print("\n✅ Retraining complete!")
    print("\nNext steps:")
    print("1. Test the API: python test_model_direct.py")
    print("2. Start the server: uvicorn main:app --reload")

if __name__ == "__main__":
    retrain_model()