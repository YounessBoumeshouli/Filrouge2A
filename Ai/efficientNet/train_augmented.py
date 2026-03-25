#!/usr/bin/env python3
"""
Train model with augmented data for better accuracy
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

def train_with_augmented_data():
    """Train model using augmented dataset"""
    
    # First, create augmented data
    print("🔄 Creating augmented dataset...")
    os.system("python augment_data.py")
    
    data_dir = "../data/price_augmented"
    models_dir = "../models"
    
    if not os.path.exists(data_dir):
        print("❌ Augmented data not found")
        return
    
    # Simple data generators (no additional augmentation since data is pre-augmented)
    train_datagen = ImageDataGenerator(rescale=1./255)
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        shuffle=True
    )
    
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'val'),
        target_size=(224, 224),
        batch_size=16,
        class_mode='categorical',
        shuffle=False
    )
    
    print(f"📊 Training samples: {train_gen.samples}")
    print(f"📊 Validation samples: {val_gen.samples}")
    
    # Build model
    base = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    outputs = Dense(len(train_gen.class_indices), activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=outputs)
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        EarlyStopping(patience=15, restore_best_weights=True, monitor='val_accuracy'),
        ReduceLROnPlateau(factor=0.5, patience=7, min_lr=1e-7),
        ModelCheckpoint(
            os.path.join(models_dir, 'price_efficientnet_augmented.h5'),
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    # Phase 1: Train head
    print("🚀 Phase 1: Training with augmented data...")
    history1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=50,
        callbacks=callbacks,
        verbose=1
    )
    
    # Phase 2: Fine-tune
    print("🔧 Phase 2: Fine-tuning...")
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    
    model.compile(
        optimizer=Adam(learning_rate=1e-5),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    callbacks[2] = ModelCheckpoint(
        os.path.join(models_dir, 'price_efficientnet_finetuned.h5'),
        save_best_only=True,
        monitor='val_accuracy'
    )
    
    history2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=30,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save class indices
    with open(os.path.join(models_dir, 'price_class_indices.json'), 'w') as f:
        idx_to_class = {v: k for k, v in train_gen.class_indices.items()}
        json.dump(idx_to_class, f, indent=2)
    
    print("✅ Training with augmented data complete!")

if __name__ == "__main__":
    train_with_augmented_data()