import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

def fine_tune_model(model_path, data_dir, epochs=10, unfreeze_layers=50):
    # Load trained model
    model = tf.keras.models.load_model(model_path)
    
    # Unfreeze base model layers
    base_model = model.layers[0]
    base_model.trainable = True
    
    # Freeze only first layers
    for layer in base_model.layers[:-unfreeze_layers]:
        layer.trainable = False
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Prepare data
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )
    
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='training'
    )
    
    val_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        subset='validation'
    )
    
    # Fine-tune
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=2)
    ]
    
    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Save fine-tuned model
    model.save("marrakech_efficientnet_finetuned.h5")
    print("Fine-tuned model saved!")
    
    return history

if __name__ == "__main__":
    model_path = "marrakech_efficientnet.h5"
    data_dir = "../data/marrakech"
    
    if os.path.exists(model_path) and os.path.exists(data_dir):
        fine_tune_model(model_path, data_dir, epochs=15)
    else:
        print("Model or data directory not found.")