"""
Test YOLO-Nano model
"""

import torch
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.models import YOLONano, create_yolo_nano
from utils.loss import YOLOLoss
from utils.metrics import compute_iou, compute_ap
import numpy as np

def test_model_creation():
    """Test model creation"""
    print("Testing model creation...")
    model = create_yolo_nano(num_classes=17, img_size=416)
    
    info = model.get_model_info()
    print(f"✓ Model created successfully")
    print(f"  Total parameters: {info['total_params']:,}")
    print(f"  Model size: {info['model_size_mb']:.2f} MB")
    print(f"  Number of classes: {info['num_classes']}")
    print(f"  Input size: {info['input_size']}")

def test_forward_pass():
    """Test forward pass"""
    print("\nTesting forward pass...")
    model = create_yolo_nano(num_classes=17, img_size=416)
    model.eval()
    
    # Test training mode
    model.train()
    x = torch.randn(2, 3, 416, 416)
    with torch.no_grad():
        outputs = model(x)
    
    print(f"✓ Training mode forward pass successful")
    print(f"  Number of output scales: {len(outputs)}")
    for i, out in enumerate(outputs):
        print(f"  Scale {i}: {out.shape}")
    
    # Test inference mode
    model.eval()
    with torch.no_grad():
        outputs = model(x)
    
    print(f"✓ Inference mode forward pass successful")
    print(f"  Output shape: {outputs.shape}")

def test_loss_function():
    """Test loss function"""
    print("\nTesting loss function...")
    criterion = YOLOLoss(num_classes=17)
    
    # Create dummy predictions and targets
    # Output channels = 3 anchors * (5 + 17 classes) = 3 * 22 = 66
    predictions = [
        torch.randn(2, 66, 52, 52),  # 3 anchors * (5 + 17 classes)
        torch.randn(2, 66, 26, 26),
        torch.randn(2, 66, 13, 13)
    ]
    
    targets = torch.zeros(4, 6)  # 4 objects, 6 values per object
    targets[0] = torch.tensor([0, 5, 0.5, 0.5, 0.3, 0.4])  # batch 0, class 5
    targets[1] = torch.tensor([0, 10, 0.3, 0.7, 0.2, 0.2])
    targets[2] = torch.tensor([1, 2, 0.8, 0.2, 0.4, 0.5])  # batch 1, class 2
    targets[3] = torch.tensor([1, 15, 0.1, 0.9, 0.1, 0.1])
    
    loss = criterion(predictions, targets)
    print(f"✓ Loss function works")
    print(f"  Loss value: {loss.item():.4f}")

def test_metrics():
    """Test metrics"""
    print("\nTesting metrics...")
    
    # Test IoU
    box1 = [0, 0, 10, 10]
    box2 = [5, 5, 15, 15]
    iou = compute_iou(box1, box2)
    print(f"✓ IoU computation works")
    print(f"  IoU between boxes: {iou:.4f}")
    
    # Test AP
    recall = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    precision = np.array([1.0, 0.9, 0.8, 0.7, 0.6, 0.5])
    ap = compute_ap(recall, precision)
    print(f"✓ AP computation works")
    print(f"  Average Precision: {ap:.4f}")

def test_device_compatibility():
    """Test device compatibility"""
    print("\nTesting device compatibility...")
    
    model = create_yolo_nano(num_classes=17)
    
    # CPU
    model = model.cpu()
    x = torch.randn(1, 3, 416, 416)
    model.eval()
    with torch.no_grad():
        _ = model(x)
    print(f"✓ CPU inference works")
    
    # GPU (if available)
    if torch.cuda.is_available():
        model = model.cuda()
        x = x.cuda()
        with torch.no_grad():
            _ = model(x)
        print(f"✓ GPU inference works")
    else:
        print(f"⚠ GPU not available (CUDA not installed)")

def main():
    print("=" * 60)
    print("YOLO-Nano Model Test Suite")
    print("=" * 60)
    
    try:
        test_model_creation()
        test_forward_pass()
        test_loss_function()
        test_metrics()
        test_device_compatibility()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
