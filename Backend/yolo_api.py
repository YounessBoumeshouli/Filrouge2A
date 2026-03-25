#!/usr/bin/env python3
"""
YOLO Model API Server
====================

FastAPI server to serve the trained YOLO model for frontend integration.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ceramic Products YOLO API",
    description="API for ceramic product detection using trained YOLO model",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
# Class names based on training dataset structure
# Class ID 0 = product_1, Class ID 1 = product_2, etc.
class_names = [
    "Ceramic Vase",                                           # Class 0 - product_1
    "Tagine",                                                  # Class 1 - product_2  
    "Ceramic Cups",                                           # Class 2 - product_3
    "Handcrafted Tamegroute Ceramic Cake Stand",             # Class 3 - product_51
    "White Ceramic Divided Plate with Silver Accents",       # Class 4 - product_66
    "Tamegroute Ceramic Pitcher Handmade Moroccan Water"      # Class 5 - product_68
]

def load_model():
    """Load the trained YOLO model"""
    global model
    
    model_path = Path("models/ceramic_yolo_trained.pt")
    
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        return False
    
    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        logger.info(f"✅ Model loaded successfully from {model_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    if not load_model():
        logger.warning("⚠️ Model not loaded - some endpoints will not work")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Ceramic Products YOLO API",
        "status": "running",
        "model_loaded": model is not None,
        "classes": class_names
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "total_classes": len(class_names),
        "classes": class_names
    }

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    """
    Detect ceramic products in uploaded image
    
    Returns:
    - detections: List of detected objects with bounding boxes
    - annotated_image: Base64 encoded image with bounding boxes
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Run inference
        results = model(image)
        
        # Process results
        detections = []
        annotated_image = None
        
        for result in results:
            # Get annotated image
            annotated_img = result.plot()
            
            # Convert to base64 for frontend
            _, buffer = cv2.imencode('.jpg', annotated_img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            annotated_image = f"data:image/jpeg;base64,{img_base64}"
            
            # Extract detection data
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                classes = result.boxes.cls.cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    x1, y1, x2, y2 = box.astype(int)
                    
                    detection = {
                        "class_id": int(cls),
                        "class_name": class_names[int(cls)],
                        "confidence": float(conf),
                        "bbox": {
                            "x1": int(x1),
                            "y1": int(y1), 
                            "x2": int(x2),
                            "y2": int(y2),
                            "width": int(x2 - x1),
                            "height": int(y2 - y1)
                        }
                    }
                    detections.append(detection)
        
        return {
            "success": True,
            "detections": detections,
            "total_detections": len(detections),
            "annotated_image": annotated_image,
            "image_size": {
                "width": image.width,
                "height": image.height
            }
        }
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/detect-batch")
async def detect_batch(files: list[UploadFile] = File(...)):
    """
    Detect objects in multiple images
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
    
    results = []
    
    for i, file in enumerate(files):
        if not file.content_type.startswith('image/'):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Not an image file"
            })
            continue
        
        try:
            # Read and process image
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Run inference
            model_results = model(image)
            
            detections = []
            for result in model_results:
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy()
                    
                    for box, conf, cls in zip(boxes, confidences, classes):
                        x1, y1, x2, y2 = box.astype(int)
                        
                        detection = {
                            "class_id": int(cls),
                            "class_name": class_names[int(cls)],
                            "confidence": float(conf),
                            "bbox": {
                                "x1": int(x1), "y1": int(y1),
                                "x2": int(x2), "y2": int(y2),
                                "width": int(x2 - x1),
                                "height": int(y2 - y1)
                            }
                        }
                        detections.append(detection)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "detections": detections,
                "total_detections": len(detections)
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "success": True,
        "results": results,
        "total_processed": len(files)
    }

@app.get("/classes")
async def get_classes():
    """Get available object classes"""
    return {
        "classes": class_names,
        "total_classes": len(class_names)
    }

@app.get("/model-info")
async def get_model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_loaded": True,
        "model_type": "YOLOv8",
        "classes": class_names,
        "total_classes": len(class_names),
        "input_size": 640,
        "framework": "Ultralytics"
    }

if __name__ == "__main__":
    uvicorn.run(
        "yolo_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )