import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os

class MarrakechPredictor:
    def __init__(self, model_path, class_names=None):
        self.model = tf.keras.models.load_model(model_path)
        self.img_size = 224
        self.class_names = class_names or self.load_class_names()
    
    def load_class_names(self):
        # Default Marrakech monument classes
        return [
            "Jemaa_el_Fnaa",
            "Koutoubia_Mosque", 
            "Bahia_Palace",
            "Saadian_Tombs",
            "Ben_Youssef_Madrasa",
            "Majorelle_Garden",
            "Menara_Gardens",
            "El_Badi_Palace",
            "Agdal_Gardens",
            "Marrakech_Medina"
        ]
    
    def preprocess_image(self, image_path):
        # Load and preprocess image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((self.img_size, self.img_size))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict(self, image_path):
        # Preprocess image
        img_array = self.preprocess_image(image_path)
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)
        confidence = float(np.max(predictions))
        class_idx = int(np.argmax(predictions))
        class_name = self.class_names[class_idx]
        
        return {
            "class_name": class_name,
            "class_index": class_idx,
            "confidence": confidence,
            "all_predictions": {
                self.class_names[i]: float(predictions[0][i]) 
                for i in range(len(self.class_names))
            }
        }
    
    def predict_batch(self, image_paths):
        results = []
        for img_path in image_paths:
            try:
                result = self.predict(img_path)
                result["image_path"] = img_path
                results.append(result)
            except Exception as e:
                results.append({
                    "image_path": img_path,
                    "error": str(e)
                })
        return results

def main():
    model_path = "marrakech_efficientnet.h5"
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Please train the model first.")
        return
    
    # Initialize predictor
    predictor = MarrakechPredictor(model_path)
    
    # Example usage
    test_image = "../data/test_image.jpg"
    if os.path.exists(test_image):
        result = predictor.predict(test_image)
        print(f"Prediction: {result['class_name']}")
        print(f"Confidence: {result['confidence']:.3f}")
    else:
        print("No test image found. Place an image at ../data/test_image.jpg")

if __name__ == "__main__":
    main()