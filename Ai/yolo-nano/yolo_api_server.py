#!/usr/bin/env python3
"""
YOLO-Nano API Server for Frontend Integration
=============================================

FastAPI server that loads the trained YOLO-Nano model and provides
detection endpoints compatible with your React frontend.

Usage:
    python yolo_api_server.py

Then your frontend can call:
    POST http://localhost:8000/api/yolo/detect
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
from pathlib import Path
import sys
import uvicorn
from typing import List, Dict, Any

# Add utils to path
sys.path.append(str(Path(__file__).parent / 'utils'))

from utils.models import YOLONano
from utils.general import non_max_suppression, scale_coords

app = FastAPI(title="YOLO-Nano Detection API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
device = None
class_names = []

class DetectionRequest(BaseModel):
    image: str  # Base64 encoded image
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class DetectionResponse(BaseModel):
    success: bool
    detections: List[Detection]
    message: str = ""

def load_model(model_path: str = "runs/train/exp/best.pt"):
    """Load the trained YOLO-Nano model"""
    global model, device, class_names
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading model on device: {device}")
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=device)
        config = checkpoint.get('config', {})
        
        # Get model parameters
        num_classes = config.get('data', {}).get('nc', 6)
        class_names = config.get('data', {}).get('names', [
            'JEWELERY', 'crafts', 'lantern', 'material_fabric', 'spices', 'textile'
        ])
        
        print(f"Model classes ({num_classes}): {class_names}")
        
        # Create model
        model = YOLONano(
            num_classes=num_classes,
            img_size=416,
            dropout_rate=0.0  # No dropout for inference
        ).to(device)
        
        # Load weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        print(f"✅ Model loaded successfully from {model_path}")
        print(f"   - Classes: {num_classes}")
        print(f"   - Device: {device}")
        print(f"   - Epoch: {checkpoint.get('epoch', 'unknown')}")
        print(f"   - Val Loss: {checkpoint.get('loss', 'unknown'):.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False

def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 image to numpy array"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array
        image = np.array(pil_image)
        
        return image
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

def preprocess_image(image: np.ndarray, img_size: int = 416) -> torch.Tensor:
    """Preprocess image for YOLO inference"""
    # Resize image
    h, w = image.shape[:2]
    image_resized = cv2.resize(image, (img_size, img_size))
    
    # Normalize to [0, 1]
    image_normalized = image_resized.astype(np.float32) / 255.0
    
    # Convert to tensor and add batch dimension
    image_tensor = torch.from_numpy(image_normalized).permute(2, 0, 1).unsqueeze(0)
    
    return image_tensor, (h, w)

def postprocess_detections(predictions: torch.Tensor, 
                         original_shape: tuple,
                         img_size: int = 416,
                         conf_threshold: float = 0.25,
                         iou_threshold: float = 0.45) -> List[Detection]:
    """Post-process YOLO predictions"""
    
    # Apply NMS
    detections = non_max_suppression(
        predictions, 
        conf_thres=conf_threshold,
        iou_thres=iou_threshold
    )
    
    results = []
    
    if detections[0] is not None and len(detections[0]) > 0:
        # Scale coordinates back to original image size
        det = detections[0]
        det[:, :4] = scale_coords((img_size, img_size), det[:, :4], original_shape).round()
        
        for *bbox, conf, cls in det:
            x1, y1, x2, y2 = bbox
            class_id = int(cls)
            confidence = float(conf)
            
            # Get class name
            class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
            
            detection = Detection(
                class_name=class_name,
                confidence=confidence,
                bbox=[float(x1), float(y1), float(x2), float(y2)]
            )
            results.append(detection)
    
    return results

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    model_path = "runs/train/exp/best.pt"
    
    # Check if model exists
    if not Path(model_path).exists():
        print(f"⚠️  Model not found at {model_path}")
        print("   Make sure training has completed and model is saved.")
        return
    
    success = load_model(model_path)
    if not success:
        print("❌ Failed to load model on startup")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YOLO-Nano Detection API",
        "model_loaded": model is not None,
        "device": str(device) if device else "unknown",
        "classes": class_names
    }

@app.post("/api/yolo/detect", response_model=DetectionResponse)
async def detect_objects(request: DetectionRequest):
    """
    Detect objects in image using trained YOLO-Nano model
    
    Compatible with your React frontend API calls.
    """
    
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # Decode image
        image = decode_base64_image(request.image)
        
        # Preprocess
        image_tensor, original_shape = preprocess_image(image)
        image_tensor = image_tensor.to(device)
        
        # Inference
        with torch.no_grad():
            predictions = model(image_tensor)
        
        # Post-process
        detections = postprocess_detections(
            predictions,
            original_shape,
            conf_threshold=request.conf_threshold,
            iou_threshold=request.iou_threshold
        )
        
        return DetectionResponse(
            success=True,
            detections=detections,
            message=f"Found {len(detections)} objects"
        )
        
    except Exception as e:
        print(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/yolo/classes")
async def get_classes():
    """Get available object classes"""
    return {
        "classes": class_names,
        "num_classes": len(class_names)
    }

@app.get("/api/yolo/model-info")
async def get_model_info():
    """Get model information"""
    if model is None:
        return {"error": "Model not loaded"}
    
    # Try to get model info
    try:
        info = model.get_model_info()
        return {
            "model_loaded": True,
            "device": str(device),
            "classes": class_names,
            "num_classes": len(class_names),
            **info
        }
    except:
        return {
            "model_loaded": True,
            "device": str(device),
            "classes": class_names,
            "num_classes": len(class_names)
        }

if __name__ == "__main__":
    print("🚀 Starting YOLO-Nano Detection API Server...")
    print("   Frontend URL: http://localhost:3000")
    print("   API URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=False
    )