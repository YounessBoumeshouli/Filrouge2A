#!/usr/bin/env python3
"""
start_test_server.py
Quick test server to verify the integration
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import base64
import sys
import os

# Add the AI model path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Ai', 'efficientNet'))

try:
    from test_api_integration import PriceClassifierAPI
    # Use absolute path to the model
    model_path = os.path.join(os.path.dirname(__file__), '..', 'Ai', 'models', 'price_efficientnet_finetuned.h5')
    if not os.path.exists(model_path):
        model_path = os.path.join(os.path.dirname(__file__), '..', 'Ai', 'models', 'price_efficientnet.h5')
    
    classes_path = os.path.join(os.path.dirname(__file__), '..', 'Ai', 'models', 'price_class_indices.json')
    
    if os.path.exists(model_path) and os.path.exists(classes_path):
        model_api = PriceClassifierAPI(model_path, classes_path)
        print(f"✅ Model loaded from: {model_path}")
    else:
        model_api = None
        print(f"❌ Model files not found. Checked: {model_path}")
except ImportError as e:
    model_api = None
    print(f"❌ Could not load model: {e}")

app = FastAPI(title="Price Classifier Test API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/price/analyze")
async def analyze_price(file: UploadFile = File(None), image: str = None):
    try:
        # Handle both file upload and base64 image
        if file:
            contents = await file.read()
            image_base64 = base64.b64encode(contents).decode('utf-8')
        elif image:
            image_base64 = image
        else:
            return {"success": False, "error": "No image provided"}
        
        # Use trained model if available
        if model_api:
            result = model_api.predict_from_base64(image_base64)
            print(f"Model prediction: {result}")
        else:
            # Fallback mock response
            result = {
                "success": True,
                "product_type": "leather",
                "confidence": 0.75,
                "all_predictions": {
                    "leather": 0.75,
                    "textiles": 0.15,
                    "crafts": 0.10,
                    "spices": 0.05,
                    "jewelry": 0.03,
                    "lanterns": 0.02,
                    "argan": 0.01,
                    "price_tags": 0.01
                }
            }
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Price Classifier Test API", 
        "model_loaded": model_api is not None,
        "endpoints": ["/api/price/analyze"]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Price Classifier Test Server...")
    print("API will be available at: http://localhost:8000")
    print("Docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)