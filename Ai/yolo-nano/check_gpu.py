#!/usr/bin/env python3
"""
GPU Setup Check for YOLO-Nano Training
======================================

Check CUDA availability and provide optimized training settings.
"""

import torch
import sys
from pathlib import Path

def check_gpu_setup():
    print("🔍 Checking GPU Setup...")
    print("=" * 50)
    
    # Check CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        # Get GPU info
        gpu_count = torch.cuda.device_count()
        print(f"Number of GPUs: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
        
        # Test GPU tensor operations
        try:
            device = torch.device('cuda:0')
            test_tensor = torch.randn(1000, 1000).to(device)
            result = torch.mm(test_tensor, test_tensor)
            print("✅ GPU tensor operations working!")
            
            # Memory info
            allocated = torch.cuda.memory_allocated(0) / 1024**3
            cached = torch.cuda.memory_reserved(0) / 1024**3
            print(f"GPU Memory - Allocated: {allocated:.2f} GB, Cached: {cached:.2f} GB")
            
        except Exception as e:
            print(f"❌ GPU test failed: {e}")
            return False
            
    else:
        print("❌ CUDA not available. Reasons could be:")
        print("   - No NVIDIA GPU")
        print("   - CUDA not installed")
        print("   - PyTorch CPU-only version")
        print("   - Driver issues")
        
        # Check PyTorch version
        print(f"\nPyTorch version: {torch.__version__}")
        print("To install CUDA-enabled PyTorch:")
        print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        
        return False
    
    print("\n🚀 Recommended Training Settings:")
    print("=" * 50)
    
    # Get GPU memory
    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    if gpu_memory_gb >= 8:
        batch_size = 32
        workers = 4
    elif gpu_memory_gb >= 6:
        batch_size = 24
        workers = 2
    elif gpu_memory_gb >= 4:
        batch_size = 16
        workers = 2
    else:
        batch_size = 8
        workers = 1
    
    print(f"Recommended batch size: {batch_size}")
    print(f"Recommended workers: {workers}")
    print(f"GPU Memory: {gpu_memory_gb:.1f} GB")
    
    print(f"\n📝 Optimized Training Command:")
    print("=" * 50)
    print(f"python train_improved.py \\")
    print(f"    --epochs 100 \\")
    print(f"    --batch-size {batch_size} \\")
    print(f"    --workers {workers} \\")
    print(f"    --device cuda \\")
    print(f"    --data data/yolo_dataset/dataset.yaml")
    
    print(f"\n⚡ Expected Performance:")
    print("=" * 50)
    print("CPU Training: ~3+ seconds per batch (days to complete)")
    print("GPU Training: ~0.1-0.3 seconds per batch (hours to complete)")
    print(f"Speed improvement: ~10-30x faster")
    
    return True

if __name__ == '__main__':
    success = check_gpu_setup()
    
    if not success:
        print("\n⚠️  GPU not available - training will be very slow on CPU!")
        print("Consider using Google Colab, Kaggle, or cloud GPU for faster training.")
    else:
        print("\n✅ GPU setup looks good! Ready for fast training.")