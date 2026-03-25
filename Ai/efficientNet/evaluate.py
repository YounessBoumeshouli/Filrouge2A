import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def evaluate_model(model_path, test_data_dir, img_size=224):
    # Load model
    model = tf.keras.models.load_model(model_path)
    
    # Prepare test data
    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        test_data_dir,
        target_size=(img_size, img_size),
        batch_size=32,
        class_mode='categorical',
        shuffle=False
    )
    
    # Get predictions
    predictions = model.predict(test_generator)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_generator.classes
    
    # Classification report
    class_names = list(test_generator.class_indices.keys())
    report = classification_report(y_true, y_pred, target_names=class_names)
    print("Classification Report:")
    print(report)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.show()
    
    # Calculate accuracy
    accuracy = np.sum(y_pred == y_true) / len(y_true)
    print(f"\nTest Accuracy: {accuracy:.4f}")
    
    return accuracy, report, cm

if __name__ == "__main__":
    model_path = "marrakech_efficientnet.h5"
    test_data_dir = "../data/test"  # Adjust path as needed
    
    try:
        accuracy, report, cm = evaluate_model(model_path, test_data_dir)
    except Exception as e:
        print(f"Error during evaluation: {e}")
        print("Make sure the model exists and test data is properly organized.")