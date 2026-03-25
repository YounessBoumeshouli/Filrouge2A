#!/usr/bin/env python3
"""
Data augmentation script to increase dataset size and variety
"""

import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random
from pathlib import Path

class DataAugmenter:
    def __init__(self):
        self.augmentations = [
            self.rotate,
            self.zoom,
            self.brightness,
            self.contrast,
            self.blur,
            self.noise,
            self.flip,
            self.crop_and_resize
        ]
    
    def rotate(self, img):
        """Random rotation"""
        angle = random.uniform(-45, 45)
        return img.rotate(angle, fillcolor=(255, 255, 255))
    
    def zoom(self, img):
        """Random zoom in/out"""
        zoom_factor = random.uniform(0.8, 1.3)
        w, h = img.size
        new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
        
        if zoom_factor > 1:  # Zoom in
            img = img.resize((new_w, new_h))
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            return img.crop((left, top, left + w, top + h))
        else:  # Zoom out
            img = img.resize((new_w, new_h))
            new_img = Image.new('RGB', (w, h), (255, 255, 255))
            paste_x = (w - new_w) // 2
            paste_y = (h - new_h) // 2
            new_img.paste(img, (paste_x, paste_y))
            return new_img
    
    def brightness(self, img):
        """Random brightness adjustment"""
        factor = random.uniform(0.7, 1.4)
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(factor)
    
    def contrast(self, img):
        """Random contrast adjustment"""
        factor = random.uniform(0.8, 1.3)
        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(factor)
    
    def blur(self, img):
        """Random blur"""
        if random.random() < 0.3:
            return img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
        return img
    
    def noise(self, img):
        """Add random noise"""
        if random.random() < 0.2:
            img_array = np.array(img)
            noise = np.random.normal(0, 10, img_array.shape)
            noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            return Image.fromarray(noisy)
        return img
    
    def flip(self, img):
        """Random horizontal flip"""
        if random.random() < 0.5:
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        return img
    
    def crop_and_resize(self, img):
        """Random crop and resize"""
        w, h = img.size
        crop_size = random.uniform(0.8, 1.0)
        new_w, new_h = int(w * crop_size), int(h * crop_size)
        
        left = random.randint(0, w - new_w)
        top = random.randint(0, h - new_h)
        
        cropped = img.crop((left, top, left + new_w, top + new_h))
        return cropped.resize((w, h))
    
    def augment_image(self, img, num_augmentations=3):
        """Apply random augmentations to image"""
        augmented = img.copy()
        selected_augs = random.sample(self.augmentations, num_augmentations)
        
        for aug_func in selected_augs:
            augmented = aug_func(augmented)
        
        return augmented

def augment_dataset(source_dir="../data/price", target_dir="../data/price_augmented", multiplier=5):
    """Augment entire dataset"""
    augmenter = DataAugmenter()
    
    print(f"🔄 Augmenting dataset from {source_dir} to {target_dir}")
    print(f"📈 Multiplier: {multiplier}x")
    
    for split in ['train', 'val']:  # Don't augment test set
        source_split = os.path.join(source_dir, split)
        target_split = os.path.join(target_dir, split)
        
        if not os.path.exists(source_split):
            continue
            
        os.makedirs(target_split, exist_ok=True)
        
        for class_name in os.listdir(source_split):
            source_class = os.path.join(source_split, class_name)
            target_class = os.path.join(target_split, class_name)
            
            if not os.path.isdir(source_class):
                continue
                
            os.makedirs(target_class, exist_ok=True)
            
            images = [f for f in os.listdir(source_class) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            print(f"📂 {split}/{class_name}: {len(images)} → {len(images) * multiplier}")
            
            # Copy original images
            for img_file in images:
                source_path = os.path.join(source_class, img_file)
                target_path = os.path.join(target_class, img_file)
                
                img = Image.open(source_path).convert('RGB')
                img.save(target_path)
                
                # Generate augmented versions
                for i in range(multiplier - 1):
                    augmented = augmenter.augment_image(img)
                    name, ext = os.path.splitext(img_file)
                    aug_name = f"{name}_aug_{i+1}{ext}"
                    aug_path = os.path.join(target_class, aug_name)
                    augmented.save(aug_path)
    
    # Copy test set without augmentation
    test_source = os.path.join(source_dir, 'test')
    test_target = os.path.join(target_dir, 'test')
    
    if os.path.exists(test_source):
        import shutil
        if os.path.exists(test_target):
            shutil.rmtree(test_target)
        shutil.copytree(test_source, test_target)
        print("📋 Test set copied without augmentation")
    
    print("✅ Dataset augmentation complete!")

if __name__ == "__main__":
    augment_dataset(multiplier=4)  # 4x more data