# YOLO-Nano Training on Google Colab
# ===================================
# 
# This notebook sets up YOLO-Nano training with GPU acceleration on Google Colab
# 
# Instructions:
# 1. Go to https://colab.research.google.com/
# 2. Create a new notebook
# 3. Go to Runtime > Change runtime type > Select GPU
# 4. Copy and paste the cells below

# Cell 1: Setup and Install Dependencies
"""
!pip install albumentations opencv-python-headless
!pip install wandb  # Optional for logging

import torch
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
"""

# Cell 2: Upload Your Dataset
"""
# Option 1: Upload from local computer
from google.colab import files
import zipfile
import os

# Upload your dataset zip file
uploaded = files.upload()

# Extract the dataset
for filename in uploaded.keys():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('/content/')
    print(f"Extracted {filename}")

# Option 2: Download from Google Drive (if you have it there)
# from google.colab import drive
# drive.mount('/content/drive')
# !cp -r "/content/drive/MyDrive/yolo-nano" "/content/"
"""

# Cell 3: Setup Training Code
"""
# Create the training structure
!mkdir -p /content/yolo-nano/utils
!mkdir -p /content/yolo-nano/configs

# You'll need to upload your training files:
# - train_improved.py
# - utils/datasets.py
# - utils/models.py
# - utils/loss.py
# - utils/metrics.py
# - utils/general.py
# - configs/yolo_nano.yaml
"""

# Cell 4: Start Training with GPU
"""
import os
os.chdir('/content/yolo-nano')

# GPU-optimized training command
!python train_improved.py \
    --epochs 100 \
    --batch-size 32 \
    --workers 2 \
    --device cuda \
    --data data/yolo_dataset/dataset.yaml \
    --wandb
"""

# Cell 5: Monitor Training Progress
"""
# View training logs
!tail -f runs/train/exp/train.log

# Download trained model
from google.colab import files
files.download('runs/train/exp/best.pt')
"""

print("Google Colab Setup Instructions:")
print("1. Go to https://colab.research.google.com/")
print("2. Create new notebook")
print("3. Runtime > Change runtime type > GPU")
print("4. Copy the cells above")
print("5. Upload your dataset and code files")
print("6. Run training with GPU acceleration!")