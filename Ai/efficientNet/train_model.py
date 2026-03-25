import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os

class MarrakechClassifier:
    def __init__(self, num_classes, img_size=224):
        self.num_classes = num_classes
        self.img_size = img_size
        self.model = None
        
    def build_model(self):
        # Load pretrained EfficientNet
        base_model = EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_shape=(self.img_size, self.img_size, 3)
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom classification head
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.2)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return self.model
    
    def prepare_data(self, data_dir, batch_size=32):
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(
            rescale=1./255,
            validation_split=0.2
        )
        
        train_generator = train_datagen.flow_from_directory(
            data_dir,
            target_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            class_mode='categorical',
            subset='training'
        )
        
        val_generator = val_datagen.flow_from_directory(
            data_dir,
            target_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation'
        )
        
        return train_generator, val_generator
    
    def train(self, train_gen, val_gen, epochs=10):
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=2)
        ]
        
        # Train model
        history = self.model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=epochs,
            callbacks=callbacks
        )
        
        return history
    
    def predict(self, image_path):
        # Load and preprocess image
        img = tf.keras.preprocessing.image.load_img(
            image_path, target_size=(self.img_size, self.img_size)
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        # Make prediction
        predictions = self.model.predict(img_array)
        confidence = np.max(predictions)
        class_idx = np.argmax(predictions)
        
        return class_idx, confidence
    
    def save_model(self, path):
        self.model.save(path)
    
    def load_model(self, path):
        self.model = tf.keras.models.load_model(path)

if __name__ == "__main__":
    # Initialize classifier
    classifier = MarrakechClassifier(num_classes=10)  # Adjust based on your dataset
    
    # Build model
    model = classifier.build_model()
    print("Model built successfully!")
    
    # Prepare data (assuming marrakech dataset is in data/marrakech/)
    data_dir = "../data/marrakech"
    if os.path.exists(data_dir):
        train_gen, val_gen = classifier.prepare_data(data_dir)
        
        # Train model
        history = classifier.train(train_gen, val_gen, epochs=20)
        
        # Save model
        classifier.save_model("marrakech_efficientnet.h5")
        print("Model saved!")
    else:
        print(f"Data directory {data_dir} not found. Please organize your dataset.")