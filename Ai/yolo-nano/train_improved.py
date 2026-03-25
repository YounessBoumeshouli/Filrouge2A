#!/usr/bin/env python3
"""
Improved YOLO-Nano Training Script with Enhanced Regularization
==============================================================

Features:
- Enhanced data augmentation (flip, rotate, color jitter, noise, blur)
- Dropout regularization in detection heads
- OneCycleLR learning rate scheduler
- Early stopping with patience=10
- Increased weight decay
- Gradient clipping
- Comprehensive logging

Usage:
    python train_improved.py --epochs 100 --batch-size 16 --dropout 0.2
    python train_improved.py --config configs/yolo_nano.yaml --early-stopping --patience 15
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

# Add utils to path
sys.path.append(str(Path(__file__).parent / 'utils'))

from utils.datasets import YOLODataset
from utils.models import YOLONano
from utils.loss import YOLOLoss
from utils.metrics import compute_ap
from utils.general import check_img_size, colorstr

class EarlyStopping:
    """Early stopping to stop training when validation loss doesn't improve"""
    def __init__(self, patience=10, min_delta=0.001, restore_best_weights=True):
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        self.best_loss = float('inf')
        self.counter = 0
        self.best_weights = None
        
    def __call__(self, val_loss, model):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            if self.restore_best_weights:
                self.best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            self.counter += 1
            
        if self.counter >= self.patience:
            if self.restore_best_weights and self.best_weights is not None:
                model.load_state_dict({k: v.to(next(model.parameters()).device) for k, v in self.best_weights.items()})
            return True
        return False

def collate_fn(batch):
    """Custom collate function for YOLO dataset"""
    images, targets = zip(*batch)
    
    # Stack images
    images = torch.stack(images, 0)
    
    # Concatenate targets and add batch index
    batch_targets = []
    for i, target in enumerate(targets):
        if len(target) > 0:
            # Add batch index as first column
            batch_idx = torch.full((len(target), 1), i, dtype=target.dtype)
            target_with_batch = torch.cat([batch_idx, target[:, 1:]], dim=1)
            batch_targets.append(target_with_batch)
    
    if batch_targets:
        targets = torch.cat(batch_targets, 0)
    else:
        targets = torch.zeros((0, 6))
    
    return images, targets

def parse_args():
    parser = argparse.ArgumentParser(description='Improved YOLO-Nano Training')
    parser.add_argument('--config', type=str, default='configs/yolo_nano.yaml',
                       help='Path to config file')
    parser.add_argument('--data', type=str, default='data/yolo_dataset/dataset.yaml',
                       help='Path to dataset config')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size')
    parser.add_argument('--img-size', type=int, default=416,
                       help='Input image size')
    parser.add_argument('--device', type=str, default='',
                       help='Device to use (cuda/cpu)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of data loading workers')
    parser.add_argument('--project', type=str, default='runs/train',
                       help='Save results to project/name')
    parser.add_argument('--name', type=str, default='exp',
                       help='Experiment name')
    parser.add_argument('--resume', type=str, default='',
                       help='Resume training from checkpoint')
    parser.add_argument('--dropout', type=float, default=0.2,
                       help='Dropout rate for regularization')
    parser.add_argument('--early-stopping', action='store_true', default=True,
                       help='Enable early stopping')
    parser.add_argument('--patience', type=int, default=10,
                       help='Early stopping patience')
    parser.add_argument('--wandb', action='store_true',
                       help='Use Weights & Biases logging')
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def train_one_epoch(model, dataloader, optimizer, criterion, device, epoch, scheduler=None):
    """Train for one epoch with improved logging"""
    model.train()
    running_loss = 0.0
    start_time = time.time()
    
    for batch_idx, (images, targets) in enumerate(dataloader):
        images = images.to(device)
        targets = targets.to(device)
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, targets)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        
        optimizer.step()
        
        # Update learning rate if using OneCycleLR
        if scheduler is not None:
            scheduler.step()
        
        running_loss += loss.item()
        
        if batch_idx % 50 == 0:
            current_lr = optimizer.param_groups[0]['lr']
            elapsed = time.time() - start_time
            print(f'Epoch {epoch}, Batch {batch_idx}/{len(dataloader)}, '
                  f'Loss: {loss.item():.4f}, LR: {current_lr:.6f}, '
                  f'Time: {elapsed:.1f}s')
    
    return running_loss / len(dataloader)

def validate(model, dataloader, criterion, device):
    """Validate model performance"""
    model.eval()
    val_loss = 0.0
    
    with torch.no_grad():
        for images, targets in dataloader:
            images = images.to(device)
            targets = targets.to(device)
            
            # Set model to training mode for loss computation
            model.train()
            outputs = model(images)
            model.eval()
            
            loss = criterion(outputs, targets)
            val_loss += loss.item()
    
    return val_loss / len(dataloader)

def main():
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Load dataset configuration
    if os.path.exists(args.data):
        with open(args.data, 'r') as f:
            data_config = yaml.safe_load(f)
        # Update config with dataset info
        config['data'].update(data_config)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() and args.device != 'cpu' else 'cpu')
    print(f'Using device: {device}')
    
    # Create save directory
    save_dir = Path(args.project) / args.name
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Save training configuration
    with open(save_dir / 'config.yaml', 'w') as f:
        yaml.dump(config, f)
    
    # Initialize Weights & Biases
    if args.wandb and WANDB_AVAILABLE:
        wandb.init(
            project='yolo-nano-marrakech-improved',
            config={**config, **vars(args)},
            name=f"{args.name}_dropout{args.dropout}_wd{config['train'].get('weight_decay', 0.001)}"
        )
    elif args.wandb:
        print('Warning: wandb not available, skipping logging')
    
    # Model with dropout
    model = YOLONano(
        num_classes=config['data']['nc'],
        img_size=args.img_size,
        dropout_rate=args.dropout
    ).to(device)
    
    # Print model info
    info = model.get_model_info()
    print("\\nYOLO-Nano Model Information:")
    print(f"Total parameters: {info['total_params']:,}")
    print(f"Trainable parameters: {info['trainable_params']:,}")
    print(f"Model size: {info['model_size_mb']:.2f} MB")
    print(f"Dropout rate: {args.dropout}")
    
    # Loss function
    criterion = YOLOLoss(num_classes=config['data']['nc'])
    
    # Optimizer with increased weight decay
    weight_decay = config['train'].get('weight_decay', 0.001)
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config['train']['learning_rate'],
        momentum=config['train']['momentum'],
        weight_decay=weight_decay
    )
    
    print(f"\\nTraining Configuration:")
    print(f"Learning rate: {config['train']['learning_rate']}")
    print(f"Weight decay: {weight_decay}")
    print(f"Momentum: {config['train']['momentum']}")
    print(f"Batch size: {args.batch_size}")
    print(f"Epochs: {args.epochs}")
    
    # Construct full paths for datasets
    data_root = Path(config['data']['path']) if 'path' in config['data'] else Path('data')
    train_path = data_root / config['data']['train']
    val_path = data_root / config['data']['val']
    
    print(f'\\nDataset paths:')
    print(f'Train path: {train_path}')
    print(f'Val path: {val_path}')
    
    # Datasets with enhanced augmentation
    train_dataset = YOLODataset(
        str(train_path.parent),
        img_size=args.img_size,
        augment=True  # Enhanced augmentation enabled
    )
    val_dataset = YOLODataset(
        str(val_path.parent),
        img_size=args.img_size,
        augment=False
    )
    
    # Data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=False,
        collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=False,
        collate_fn=collate_fn
    )
    
    print(f'\\nDataset sizes:')
    print(f'Training on {len(train_dataset)} images')
    print(f'Validating on {len(val_dataset)} images')
    
    # Learning rate scheduler - OneCycleLR for better convergence
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=config['train']['learning_rate'],
        epochs=args.epochs,
        steps_per_epoch=len(train_loader),
        pct_start=0.1,  # 10% of training for warmup
        anneal_strategy='cos',
        div_factor=25.0,  # initial_lr = max_lr / div_factor
        final_div_factor=1e4  # min_lr = initial_lr / final_div_factor
    )
    
    print(f"\\nUsing OneCycleLR scheduler:")
    print(f"Max LR: {config['train']['learning_rate']}")
    print(f"Steps per epoch: {len(train_loader)}")
    print(f"Warmup: {int(0.1 * args.epochs)} epochs")
    
    # Early stopping
    early_stopping = None
    if args.early_stopping:
        early_stopping = EarlyStopping(patience=args.patience, min_delta=0.001)
        print(f"\\nEarly stopping enabled with patience: {args.patience}")
    
    # Training loop with early stopping
    best_loss = float('inf')
    start_time = time.time()
    
    print(f"\\n{'='*60}")
    print(f"Starting training with enhanced regularization...")
    print(f"{'='*60}")
    
    for epoch in range(args.epochs):
        epoch_start = time.time()
        print(f'\\nEpoch {epoch+1}/{args.epochs}')
        print('-' * 50)
        
        # Train
        train_loss = train_one_epoch(
            model, train_loader, optimizer, criterion, device, epoch, scheduler
        )
        
        # Validate
        val_loss = validate(model, val_loader, criterion, device)
        
        epoch_time = time.time() - epoch_start
        total_time = time.time() - start_time
        
        print(f'\\nEpoch {epoch+1} Summary:')
        print(f'Train Loss: {train_loss:.4f}')
        print(f'Val Loss: {val_loss:.4f}')
        print(f'Learning Rate: {optimizer.param_groups[0]["lr"]:.6f}')
        print(f'Epoch Time: {epoch_time:.1f}s')
        print(f'Total Time: {total_time/60:.1f}m')
        
        # Log to wandb
        if args.wandb and WANDB_AVAILABLE:
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'lr': optimizer.param_groups[0]['lr'],
                'epoch_time': epoch_time
            })
        
        # Save best model
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': val_loss,
                'config': config,
                'args': vars(args)
            }, save_dir / 'best.pt')
            print(f'✓ New best model saved with val_loss: {val_loss:.4f}')
        
        # Early stopping check
        if early_stopping is not None:
            if early_stopping(val_loss, model):
                print(f'\\n🛑 Early stopping triggered after {epoch + 1} epochs')
                print(f'Best validation loss: {early_stopping.best_loss:.4f}')
                break
        
        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': val_loss,
                'config': config,
                'args': vars(args)
            }, save_dir / f'epoch_{epoch+1}.pt')
            print(f'📁 Checkpoint saved: epoch_{epoch+1}.pt')
    
    total_training_time = time.time() - start_time
    print(f'\\n{"="*60}')
    print(f'🎉 Training completed!')
    print(f'Total training time: {total_training_time/3600:.2f} hours')
    print(f'Best validation loss: {best_loss:.4f}')
    print(f'Best model saved to: {save_dir / "best.pt"}')
    print(f'{"="*60}')
    
    if args.wandb and WANDB_AVAILABLE:
        wandb.finish()

if __name__ == '__main__':
    main()