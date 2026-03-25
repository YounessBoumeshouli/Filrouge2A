#!/usr/bin/env python3
"""
Improved training script for accurate price classification
"""

import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import json

def create_improved_model(num_classes=8):
    """Create improved EfficientNet model with better architecture"""
    base = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.2)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=outputs)
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def create_data_generators(data_dir, batch_size=32):
    """Create improved data generators with better augmentation"""
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.2,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        channel_shift_range=0.2,
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )
    
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'val'),
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_gen, val_gen

def train_improved_model():
    """Train the improved model with better parameters"""
    data_dir = "../data/price"
    models_dir = "../models"
    
    if not os.path.exists(data_dir):
        print("❌ Data directory not found. Run data preparation first.")
        return
    
    # Create generators with smaller batch size for better learning
    train_gen, val_gen = create_data_generators(data_dir, batch_size=8)
    
    # Create model
    model = create_improved_model(len(train_gen.class_indices))
    
    # Callbacks with more patience
    callbacks = [
        EarlyStopping(patience=15, restore_best_weights=True, monitor='val_accuracy'),
        ReduceLROnPlateau(factor=0.3, patience=7, min_lr=1e-8, monitor='val_loss'),
        ModelCheckpoint(
            os.path.join(models_dir, 'price_efficientnet_improved.h5'),
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    # Phase 1: Train head longer
    print("🚀 Phase 1: Training classification head...")
    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=100,  # More epochs
        callbacks=callbacks,
        verbose=1
    )
    
    # Phase 2: Fine-tune with more layers
    print("🚀 Phase 2: Fine-tuning...")
    model.layers[0].trainable = True
    for layer in model.layers[0].layers[:-50]:  # Unfreeze more layers
        layer.trainable = False
    
    model.compile(
        optimizer=Adam(learning_rate=5e-6),  # Lower learning rate
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks[2] = ModelCheckpoint(
        os.path.join(models_dir, 'price_efficientnet_finetuned_improved.h5'),
        save_best_only=True,
        monitor='val_accuracy'
    )
    
    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=50,  # More fine-tuning epochs
        callbacks=callbacks,
        verbose=1
    )
    
    # Save class indices
    with open(os.path.join(models_dir, 'price_class_indices.json'), 'w') as f:
        idx_to_class = {v: k for k, v in train_gen.class_indices.items()}
        json.dump(idx_to_class, f, indent=2)
    
    print("✅ Training complete!")
    return model

if __name__ == "__main__":
    train_improved_model()