import tensorflow as tf
import numpy as np
from PIL import Image
import io
import base64
import json

class MarrakechAPI:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
        self.img_size = 224
        self.class_names = [
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
    
    def predict_from_base64(self, image_base64):
        """Predict from base64 encoded image"""
        try:
            # Decode base64
            image_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            
            # Preprocess
            img = img.resize((self.img_size, self.img_size))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = self.model.predict(img_array, verbose=0)
            confidence = float(np.max(predictions))
            class_idx = int(np.argmax(predictions))
            
            return {
                "success": True,
                "class_name": self.class_names[class_idx],
                "confidence": round(confidence, 3),
                "predictions": {
                    self.class_names[i]: round(float(predictions[0][i]), 3)
                    for i in range(len(self.class_names))
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict_from_file(self, file_path):
        """Predict from file path"""
        try:
            img = Image.open(file_path).convert('RGB')
            img = img.resize((self.img_size, self.img_size))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            predictions = self.model.predict(img_array, verbose=0)
            confidence = float(np.max(predictions))
            class_idx = int(np.argmax(predictions))
            
            return {
                "success": True,
                "class_name": self.class_names[class_idx],
                "confidence": round(confidence, 3),
                "predictions": {
                    self.class_names[i]: round(float(predictions[0][i]), 3)
                    for i in range(len(self.class_names))
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# FastAPI integration example
def create_fastapi_routes(app, model_path):
    from fastapi import File, UploadFile
    
    api = MarrakechAPI(model_path)
    
    @app.post("/api/location/analyze")
    async def analyze_location(file: UploadFile = File(...)):
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = api.model.predict(img_array, verbose=0)
        confidence = float(np.max(predictions))
        class_idx = int(np.argmax(predictions))
        
        return {
            "name": api.class_names[class_idx],
            "city": "Marrakech",
            "history": f"Identified as {api.class_names[class_idx]}",
            "latitude": 31.6295,
            "longitude": -7.9811,
            "confidence": round(confidence, 3)
        }
    
    return app

if __name__ == "__main__":
    api = MarrakechAPI("marrakech_efficientnet.h5")
    print("API initialized successfully!")