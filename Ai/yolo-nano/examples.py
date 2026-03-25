"""
Example usage of YOLO-Nano components
"""

import torch
import yaml
from pathlib import Path

# Import YOLO components
from utils import (
    YOLONano,
    YOLODataset,
    YOLOLoss,
    compute_metrics,
    MetricsTracker
)

def example_1_create_model():
    """Example 1: Create and inspect model"""
    print("=" * 60)
    print("Example 1: Create and Inspect Model")
    print("=" * 60)
    
    # Create model
    model = YOLONano(num_classes=17, img_size=416, width_mult=0.25)
    
    # Get model info
    info = model.get_model_info()
    print(f"Model Information:")
    print(f"  Total Parameters: {info['total_params']:,}")
    print(f"  Trainable Parameters: {info['trainable_params']:,}")
    print(f"  Model Size: {info['model_size_mb']:.2f} MB")
    print(f"  Number of Classes: {info['num_classes']}")
    print(f"  Input Size: {info['input_size']}")
    
    # Test forward pass
    x = torch.randn(2, 3, 416, 416)
    model.eval()
    with torch.no_grad():
        output = model(x)
    print(f"\nForward Pass:")
    print(f"  Input shape: {x.shape}")
    print(f"  Output shape: {output.shape}")

def example_2_load_config():
    """Example 2: Load configuration"""
    print("\n" + "=" * 60)
    print("Example 2: Load Configuration")
    print("=" * 60)
    
    config_path = 'configs/yolo_nano.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"Configuration loaded from {config_path}")
    print(f"\nModel Config:")
    print(f"  Architecture: {config['model']['architecture']}")
    print(f"  Input Size: {config['model']['input_size']}")
    print(f"  Number of Classes: {config['data']['nc']}")
    
    print(f"\nTraining Config:")
    print(f"  Epochs: {config['train']['epochs']}")
    print(f"  Batch Size: {config['train']['batch_size']}")
    print(f"  Learning Rate: {config['train']['learning_rate']}")
    
    print(f"\nClasses ({len(config['data']['names'])} total):")
    for i, name in enumerate(config['data']['names']):
        print(f"  {i}: {name}")

def example_3_loss_function():
    """Example 3: Use loss function"""
    print("\n" + "=" * 60)
    print("Example 3: Loss Function")
    print("=" * 60)
    
    # Create loss function
    criterion = YOLOLoss(num_classes=17)
    
    # Create dummy predictions (3 scales)
    predictions = [
        torch.randn(2, 66, 52, 52),  # Scale 1: 8x downsampling (3 * 22 = 66)
        torch.randn(2, 66, 26, 26),  # Scale 2: 16x downsampling
        torch.randn(2, 66, 13, 13)   # Scale 3: 32x downsampling
    ]
    
    # Create dummy targets
    targets = torch.zeros(4, 6)
    targets[0] = torch.tensor([0, 5, 0.5, 0.5, 0.3, 0.4])   # Batch 0, class 5
    targets[1] = torch.tensor([0, 10, 0.3, 0.7, 0.2, 0.2])  # Batch 0, class 10
    targets[2] = torch.tensor([1, 2, 0.8, 0.2, 0.4, 0.5])   # Batch 1, class 2
    targets[3] = torch.tensor([1, 14, 0.1, 0.9, 0.1, 0.1])  # Batch 1, class 14
    
    # Compute loss
    loss = criterion(predictions, targets)
    
    print(f"Loss Computation:")
    print(f"  Number of predictions: {len(predictions)}")
    print(f"  Number of targets: {len(targets)}")
    print(f"  Total Loss: {loss.item():.4f}")

def example_4_metrics_tracking():
    """Example 4: Track metrics during training"""
    print("\n" + "=" * 60)
    print("Example 4: Metrics Tracking")
    print("=" * 60)
    
    # Create metrics tracker
    tracker = MetricsTracker()
    
    # Simulate training loop
    print("Simulating training loop...")
    for epoch in range(5):
        # Simulate losses
        loss = 2.0 * (0.9 ** epoch)  # Decreasing loss
        accuracy = 0.5 + 0.1 * epoch  # Increasing accuracy
        
        tracker.update(loss, accuracy)
        print(f"  Epoch {epoch+1}: Loss={loss:.4f}, Accuracy={accuracy:.4f}")
    
    print(f"\nMetrics Summary:")
    print(f"  Average Loss: {tracker.get_average_loss():.4f}")
    print(f"  Average Accuracy: {tracker.get_average_accuracy():.4f}")

def example_5_dataset_loading():
    """Example 5: Load dataset"""
    print("\n" + "=" * 60)
    print("Example 5: Dataset Loading")
    print("=" * 60)
    
    data_dir = 'data/train'
    
    if Path(data_dir).exists():
        # Create dataset
        dataset = YOLODataset(data_dir, img_size=416, augment=True)
        
        print(f"Dataset Information:")
        print(f"  Directory: {data_dir}")
        print(f"  Number of images: {len(dataset)}")
        print(f"  Image size: 416x416")
        print(f"  Augmentation: Enabled")
        
        if len(dataset) > 0:
            # Load a sample
            image, targets = dataset[0]
            print(f"\nSample Information:")
            print(f"  Image shape: {image.shape}")
            print(f"  Number of objects: {len(targets)}")
            if len(targets) > 0:
                print(f"  First object: {targets[0]}")
    else:
        print(f"Dataset directory not found: {data_dir}")
        print("Run 'python prepare_dataset.py' first to prepare the dataset")

def example_6_training_setup():
    """Example 6: Setup training components"""
    print("\n" + "=" * 60)
    print("Example 6: Training Setup")
    print("=" * 60)
    
    # Load config
    with open('configs/yolo_nano.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create model
    model = YOLONano(
        num_classes=config['data']['nc'],
        img_size=config['model']['input_size'][0]
    )
    
    # Create loss function
    criterion = YOLOLoss(num_classes=config['data']['nc'])
    
    # Create optimizer
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config['train']['learning_rate'],
        momentum=config['train']['momentum'],
        weight_decay=config['train']['weight_decay']
    )
    
    # Create scheduler
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config['train']['epochs']
    )
    
    print(f"Training Setup Complete:")
    print(f"  Model: YOLONano")
    print(f"  Loss Function: YOLOLoss")
    print(f"  Optimizer: SGD")
    print(f"  Scheduler: CosineAnnealingLR")
    print(f"  Learning Rate: {config['train']['learning_rate']}")
    print(f"  Momentum: {config['train']['momentum']}")
    print(f"  Weight Decay: {config['train']['weight_decay']}")

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  YOLO-Nano Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_1_create_model()
        example_2_load_config()
        example_3_loss_function()
        example_4_metrics_tracking()
        example_5_dataset_loading()
        example_6_training_setup()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Run: python prepare_dataset.py")
        print("  2. Run: python test_model.py")
        print("  3. Run: python train.py --epochs 100")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
