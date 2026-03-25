"""
YOLO Dataset loader with augmentation
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path
import albumentations as A
from albumentations.pytorch import ToTensorV2

class YOLODataset(Dataset):
    """YOLO dataset loader"""
    
    def __init__(self, data_dir, img_size=416, augment=True):
        self.img_size = img_size
        self.augment = augment
        self.data_dir = Path(data_dir)
        
        # Get image and label files
        self.img_files = sorted(self.data_dir.glob('images/*.jpg')) + \
                        sorted(self.data_dir.glob('images/*.png'))
        self.label_files = [str(f).replace('images', 'labels').replace('.jpg', '.txt').replace('.png', '.txt') 
                           for f in self.img_files]
        
        # Setup augmentation
        if self.augment:
            self.transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.2),
                A.Rotate(limit=10, p=0.5),
                A.GaussNoise(p=0.1),
                A.Resize(img_size, img_size),
                A.Normalize(),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='pascal_voc', label_fields=['labels']))
        else:
            self.transform = A.Compose([
                A.Resize(img_size, img_size),
                A.Normalize(),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='pascal_voc', label_fields=['labels']))
    
    def __len__(self):
        return len(self.img_files)
    
    def __getitem__(self, idx):
        img_path = str(self.img_files[idx])
        label_path = self.label_files[idx]
        
        # Load image
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        
        # Load labels
        bboxes = []
        labels = []
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    line = line.strip()  # Remove whitespace and newlines
                    if not line:  # Skip empty lines
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            # YOLO format: x_center, y_center, width, height (normalized)
                            x_center = float(parts[1]) * w
                            y_center = float(parts[2]) * h
                            box_w = float(parts[3]) * w
                            box_h = float(parts[4]) * h
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Error parsing label line '{line}' in {label_path}: {e}")
                            continue
                        
                        # Convert to pascal_voc format (x1, y1, x2, y2)
                        x1 = x_center - box_w / 2
                        y1 = y_center - box_h / 2
                        x2 = x_center + box_w / 2
                        y2 = y_center + box_h / 2
                        
                        bboxes.append([x1, y1, x2, y2])
                        labels.append(class_id)
        
        # Apply augmentation
        if self.augment and len(bboxes) > 0:
            transformed = self.transform(image=image, bboxes=bboxes, labels=labels)
            image = transformed['image']
            bboxes = transformed['bboxes']
            labels = transformed['labels']
        else:
            transformed = self.transform(image=image, bboxes=[], labels=[])
            image = transformed['image']
        
        # Convert to tensor format for YOLO
        targets = torch.zeros((len(labels), 6))
        for i, (bbox, label) in enumerate(zip(bboxes, labels)):
            x1, y1, x2, y2 = bbox
            # Normalize coordinates
            x1 = max(0, min(x1 / self.img_size, 1))
            y1 = max(0, min(y1 / self.img_size, 1))
            x2 = max(0, min(x2 / self.img_size, 1))
            y2 = max(0, min(y2 / self.img_size, 1))
            
            # Convert to YOLO format
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = x2 - x1
            height = y2 - y1
            
            targets[i] = torch.tensor([0, label, x_center, y_center, width, height])
        
        return image, targets