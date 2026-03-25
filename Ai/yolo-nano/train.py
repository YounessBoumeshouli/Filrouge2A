#!/usr/bin/env python3
"""
YOLO-Nano Training Script for Marrakech Object Detection
========================================================

Train YOLO-Nano model for detecting monuments and products in Marrakech scenes.
Supports both single-class and multi-class detection scenarios.

Usage:
    python train.py --config configs/yolo_nano.yaml --data data/dataset.yaml
    python train.py --epochs 100 --batch-size 16 --img-size 416
"""

import argparse
import os
import sys
import yaml
from pathlib import Path

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
                self.best_weights = model.state_dict().copy()
        else:
            self.counter += 1
            
        if self.counter >= self.patience:
            if self.restore_best_weights and self.best_weights is not None:
                model.load_state_dict(self.best_weights)
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
    parser = argparse.ArgumentParser(description='YOLO-Nano Training')
    parser.add_argument('--config', type=str, default='configs/yolo_nano.yaml',
                       help='Path to config file')
    parser.add_argument('--data', type=str, default='data/dataset.yaml',
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
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    
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
            print(f'Epoch {epoch}, Batch {batch_idx}/{len(dataloader)}, '
                  f'Loss: {loss.item():.4f}, LR: {current_lr:.6f}')
    
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
    
    # Initialize Weights & Biases
    if args.wandb and WANDB_AVAILABLE:
        wandb.init(project='yolo-nano-marrakech', config=config)
    elif args.wandb:
        print('Warning: wandb not available, skipping logging')
    
    # Model with dropout
    model = YOLONano(
        num_classes=config['data']['nc'],
        img_size=args.img_size,
        dropout_rate=args.dropout
    ).to(device)
    
    # Loss function
    criterion = YOLOLoss(num_classes=config['data']['nc'])
    
    # Optimizer with increased weight decay
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config['train']['learning_rate'],
        momentum=config['train']['momentum'],
        weight_decay=config['train'].get('weight_decay', 0.001)  # Increased from 0.0005
    )
    
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
    
    # Early stopping
    early_stopping = None
    if args.early_stopping:
        early_stopping = EarlyStopping(patience=args.patience, min_delta=0.001)
    
    # Construct full paths for datasets
    data_root = Path(config['data']['path']) if 'path' in config['data'] else Path('data')
    train_path = data_root / config['data']['train']
    val_path = data_root / config['data']['val']
    
    print(f'Train path: {train_path}')
    print(f'Val path: {val_path}')
    
    # Datasets
    train_dataset = YOLODataset(
        str(train_path.parent),  # Pass the directory containing images
        img_size=args.img_size,
        augment=True
    )
    val_dataset = YOLODataset(
        str(val_path.parent),  # Pass the directory containing images
        img_size=args.img_size,
        augment=False
    )
    
    # Data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=False,  # Disable for CPU
        collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=False,  # Disable for CPU
        collate_fn=collate_fn
    )
    
    print(f'Training on {len(train_dataset)} images, '
          f'validating on {len(val_dataset)} images')
    
    # Training loop with early stopping
    best_loss = float('inf')
    
    for epoch in range(args.epochs):
        print(f'\nEpoch {epoch+1}/{args.epochs}')
        print('-' * 50)
        
        # Train
        train_loss = train_one_epoch(
            model, train_loader, optimizer, criterion, device, epoch, scheduler
        )
        
        # Validate
        val_loss = validate(model, val_loader, criterion, device)
        
        print(f'Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')
        print(f'Learning Rate: {optimizer.param_groups[0]["lr"]:.6f}')
        
        # Log to wandb
        if args.wandb and WANDB_AVAILABLE:
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'lr': optimizer.param_groups[0]['lr']
            })
        
        # Save best model
        if val_loss < best_loss:
            best_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
                'loss': val_loss,
                'config': config
            }, save_dir / 'best.pt')
            print(f'New best model saved with val_loss: {val_loss:.4f}')
        
        # Early stopping check
        if early_stopping is not None:
            if early_stopping(val_loss, model):
                print(f'Early stopping triggered after {epoch + 1} epochs')
                print(f'Best validation loss: {early_stopping.best_loss:.4f}')
                break
        
        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict() if scheduler else None,
                'loss': val_loss,
                'config': config
            }, save_dir / f'epoch_{epoch+1}.pt')
    
    print(f'\nTraining completed! Best model saved to {save_dir / "best.pt"}')

if __name__ == '__main__':
    main()