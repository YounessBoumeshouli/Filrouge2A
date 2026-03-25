#!/usr/bin/env python3
"""
Quick accuracy improvement - focused training
"""

import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import json

# Key improvements for accuracy
def quick_retrain():
    """Quick retraining with key accuracy improvements"""
    
    data_dir = "../data/price"
    models_dir = "../models"
    
    # Better data augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=45,
        width_shift_range=0.3,
        height_shift_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )
    
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Smaller batch size for better learning
    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(224, 224),
        batch_size=8,
        class_mode='categorical',
        shuffle=True
    )
    
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, 'val'),
        target_size=(224, 224),
        batch_size=8,
        class_mode='categorical',
        shuffle=False
    )
    
    # Improved model architecture
    base = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base.trainable = False
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    outputs = Dense(len(train_gen.class_indices), activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=outputs)
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train with more epochs and patience
    callbacks = [
        EarlyStopping(patience=20, restore_best_weights=True, monitor='val_accuracy'),
        ReduceLROnPlateau(factor=0.3, patience=8, min_lr=1e-8),
        ModelCheckpoint(
            os.path.join(models_dir, 'price_efficientnet_quick.h5'),
            save_best_only=True,
            monitor='val_accuracy'
        )
    ]
    
    print("🚀 Quick retraining started...")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=80,
        callbacks=callbacks,
        verbose=1
    )
    
    # Fine-tune
    base.trainable = True
    for layer in base.layers[:-40]:
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
    
    print("🔧 Fine-tuning...")
    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=40,
        callbacks=callbacks,
        verbose=1
    )
    
    # Update class indices
    with open(os.path.join(models_dir, 'price_class_indices.json'), 'w') as f:
        idx_to_class = {v: k for k, v in train_gen.class_indices.items()}
        json.dump(idx_to_class, f, indent=2)
    
    print("✅ Quick retraining complete!")

if __name__ == "__main__":
    quick_retrain()