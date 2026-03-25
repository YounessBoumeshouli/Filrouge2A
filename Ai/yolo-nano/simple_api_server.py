#!/usr/bin/env python3
"""
Simplified YOLO-Nano API Server
===============================

Simplified FastAPI server that loads the trained YOLO-Nano model
without complex utility imports.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torch.nn as nn
import torch.nn.functional as F
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
from pathlib import Path
import uvicorn
from typing import List, Dict, Any
import torchvision

app = FastAPI(title="YOLO-Nano Detection API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],  # React frontend + API docs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None
device = None
class_names = ['JEWELERY', 'crafts', 'lantern', 'material_fabric', 'spices', 'textile']

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

class PriceAnalysisRequest(BaseModel):
    image: str  # Base64 encoded image

class PriceAnalysisResponse(BaseModel):
    success: bool
    product_type: str = ""
    confidence: float = 0.0
    all_predictions: List[Dict] = []
    message: str = ""

# Simplified YOLO model classes (minimal implementation)
class ConvBNReLU(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1, padding=0, groups=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU6(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))

class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size, stride, padding, groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU6(inplace=True)
    
    def forward(self, x):
        x = self.relu(self.bn1(self.depthwise(x)))
        x = self.relu(self.bn2(self.pointwise(x)))
        return x

class ShuffleBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, groups=2):
        super().__init__()
        self.stride = stride
        self.groups = groups
        
        mid_channels = out_channels // 4
        
        self.conv1 = ConvBNReLU(in_channels, mid_channels, 1, groups=groups)
        self.conv2 = DepthwiseSeparableConv(mid_channels, mid_channels, 3, stride)
        self.conv3 = ConvBNReLU(mid_channels, out_channels, 1, groups=groups)
        
        if stride == 2:
            self.shortcut = nn.Sequential(
                DepthwiseSeparableConv(in_channels, in_channels, 3, stride),
                ConvBNReLU(in_channels, out_channels, 1, groups=groups)
            )
        elif in_channels != out_channels:
            self.shortcut = ConvBNReLU(in_channels, out_channels, 1)
        else:
            self.shortcut = nn.Identity()
    
    def forward(self, x):
        residual = self.shortcut(x)
        
        x = self.conv1(x)
        x = self.channel_shuffle(x)
        x = self.conv2(x)
        x = self.conv3(x)
        
        return F.relu(x + residual)
    
    def channel_shuffle(self, x):
        batch_size, channels, height, width = x.size()
        channels_per_group = channels // self.groups
        
        x = x.view(batch_size, self.groups, channels_per_group, height, width)
        x = x.transpose(1, 2).contiguous()
        x = x.view(batch_size, channels, height, width)
        
        return x

class YOLONanoBackbone(nn.Module):
    def __init__(self, width_mult=0.25):
        super().__init__()
        
        def _make_divisible(v, divisor=8):
            return max(divisor, int(v + divisor / 2) // divisor * divisor)
        
        channels = [32, 64, 128, 256, 512]
        channels = [_make_divisible(ch * width_mult) for ch in channels]
        
        self.stem = ConvBNReLU(3, channels[0], 3, 2, 1)
        
        self.stage1 = nn.Sequential(
            DepthwiseSeparableConv(channels[0], channels[1], 3, 2),
            ShuffleBlock(channels[1], channels[1])
        )
        
        self.stage2 = nn.Sequential(
            ShuffleBlock(channels[1], channels[2], 2),
            ShuffleBlock(channels[2], channels[2]),
            ShuffleBlock(channels[2], channels[2])
        )
        
        self.stage3 = nn.Sequential(
            ShuffleBlock(channels[2], channels[3], 2),
            ShuffleBlock(channels[3], channels[3]),
            ShuffleBlock(channels[3], channels[3]),
            ShuffleBlock(channels[3], channels[3])
        )
        
        self.stage4 = nn.Sequential(
            ShuffleBlock(channels[3], channels[4], 2),
            ShuffleBlock(channels[4], channels[4])
        )
        
        self.out_channels = channels
    
    def forward(self, x):
        x = self.stem(x)
        c1 = self.stage1(x)
        c2 = self.stage2(c1)
        c3 = self.stage3(c2)
        c4 = self.stage4(c3)
        return c2, c3, c4

class YOLONanoHead(nn.Module):
    def __init__(self, num_classes, c2_channels, c3_channels, c4_channels, anchors_per_scale=3, dropout_rate=0.0):
        super().__init__()
        self.num_classes = num_classes
        self.anchors_per_scale = anchors_per_scale
        self.num_outputs = anchors_per_scale * (5 + num_classes)
        
        self.dropout = nn.Dropout2d(p=dropout_rate)
        
        self.head_large_conv = nn.Sequential(
            ConvBNReLU(c2_channels, c2_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c2_channels // 2, self.num_outputs, 1)
        )
        
        self.head_medium_conv = nn.Sequential(
            ConvBNReLU(c3_channels, c3_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c3_channels // 2, self.num_outputs, 1)
        )
        
        self.head_small_conv = nn.Sequential(
            ConvBNReLU(c4_channels, c4_channels // 2, 3, 1, 1),
            nn.Dropout2d(p=dropout_rate),
            nn.Conv2d(c4_channels // 2, self.num_outputs, 1)
        )
        
        self.upsample = nn.Upsample(scale_factor=2, mode='nearest')
        
        self.fusion1 = nn.Sequential(
            ConvBNReLU(c3_channels + c2_channels, c3_channels, 1),
            nn.Dropout2d(p=dropout_rate)
        )
        self.fusion2 = nn.Sequential(
            ConvBNReLU(c4_channels + c3_channels, c4_channels, 1),
            nn.Dropout2d(p=dropout_rate)
        )
    
    def forward(self, features):
        c2, c3, c4 = features
        
        out_large = self.head_large_conv(c2)
        
        p3 = F.max_pool2d(c2, kernel_size=2, stride=2)
        p3 = torch.cat([p3, c3], dim=1)
        p3 = self.fusion1(p3)
        out_medium = self.head_medium_conv(p3)
        
        p4 = F.max_pool2d(p3, kernel_size=2, stride=2)
        p4 = torch.cat([p4, c4], dim=1)
        p4 = self.fusion2(p4)
        out_small = self.head_small_conv(p4)
        
        return [out_large, out_medium, out_small]

class YOLONano(nn.Module):
    def __init__(self, num_classes=6, img_size=416, width_mult=0.25, dropout_rate=0.0):
        super().__init__()
        self.num_classes = num_classes
        self.img_size = img_size
        
        self.backbone = YOLONanoBackbone(width_mult)
        
        backbone_channels = self.backbone.out_channels
        c2_ch = backbone_channels[2]
        c3_ch = backbone_channels[3]
        c4_ch = backbone_channels[4]
        
        self.head = YOLONanoHead(num_classes, c2_ch, c3_ch, c4_ch, dropout_rate=dropout_rate)
        
        self._initialize_weights()
    
    def forward(self, x):
        features = self.backbone(x)
        outputs = self.head(features)
        
        if self.training:
            return outputs
        else:
            inference_outputs = []
            for i, out in enumerate(outputs):
                batch_size, _, height, width = out.shape
                
                out = out.view(batch_size, 3, 5 + self.num_classes, height, width)
                out = out.permute(0, 1, 3, 4, 2).contiguous()
                
                out[..., 4:] = torch.sigmoid(out[..., 4:])
                
                out = out.view(batch_size, -1, 5 + self.num_classes)
                inference_outputs.append(out)
            
            return torch.cat(inference_outputs, dim=1)
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

def load_model(model_path: str = "runs/train/exp/best.pt"):
    """Load the trained YOLO-Nano model"""
    global model, device
    
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading model on device: {device}")
        
        checkpoint = torch.load(model_path, map_location=device)
        config = checkpoint.get('config', {})
        
        num_classes = config.get('data', {}).get('nc', 6)
        
        print(f"Model classes ({num_classes}): {class_names}")
        
        model = YOLONano(
            num_classes=num_classes,
            img_size=416,
            dropout_rate=0.0
        ).to(device)
        
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
        import traceback
        traceback.print_exc()
        return False

def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 image to numpy array"""
    try:
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        pil_image = Image.open(io.BytesIO(image_data))
        
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        image = np.array(pil_image)
        return image
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

def preprocess_image(image: np.ndarray, img_size: int = 416) -> torch.Tensor:
    """Preprocess image for YOLO inference"""
    h, w = image.shape[:2]
    image_resized = cv2.resize(image, (img_size, img_size))
    
    image_normalized = image_resized.astype(np.float32) / 255.0
    image_tensor = torch.from_numpy(image_normalized).permute(2, 0, 1).unsqueeze(0)
    
    return image_tensor, (h, w)

def simple_nms(predictions: torch.Tensor, conf_threshold: float = 0.25, iou_threshold: float = 0.45) -> List[Detection]:
    """Simplified NMS for YOLO predictions with debugging"""
    results = []
    
    print(f"🔍 NMS Debug - Input shape: {predictions.shape}")
    
    if predictions.shape[0] == 0:
        print("❌ No predictions to process")
        return results
    
    # Get predictions for first image
    pred = predictions[0]  # [num_predictions, 5+num_classes]
    print(f"📊 Processing {pred.shape[0]} predictions")
    
    # Filter by confidence
    obj_conf = pred[:, 4]  # objectness confidence
    class_conf, class_pred = pred[:, 5:].max(1)  # class confidence and prediction
    
    total_conf = obj_conf * class_conf
    print(f"📈 Confidence stats - Max: {total_conf.max():.3f}, Min: {total_conf.min():.3f}, Mean: {total_conf.mean():.3f}")
    
    mask = total_conf > conf_threshold
    valid_count = mask.sum().item()
    print(f"✅ {valid_count} predictions above confidence threshold {conf_threshold}")
    
    if not mask.any():
        print(f"❌ No predictions above confidence threshold {conf_threshold}")
        return results
    
    # Get valid predictions
    valid_pred = pred[mask]
    valid_conf = total_conf[mask]
    valid_class = class_pred[mask]
    
    # Show top predictions before NMS
    top_indices = valid_conf.argsort(descending=True)[:5]
    print("🏆 Top 5 predictions before NMS:")
    for i, idx in enumerate(top_indices):
        class_id = valid_class[idx].item()
        conf = valid_conf[idx].item()
        class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
        print(f"   {i+1}. {class_name}: {conf:.3f}")
    
    # Convert center format to corner format
    boxes = valid_pred[:, :4].clone()
    boxes[:, 0] = valid_pred[:, 0] - valid_pred[:, 2] / 2  # x1
    boxes[:, 1] = valid_pred[:, 1] - valid_pred[:, 3] / 2  # y1
    boxes[:, 2] = valid_pred[:, 0] + valid_pred[:, 2] / 2  # x2
    boxes[:, 3] = valid_pred[:, 1] + valid_pred[:, 3] / 2  # y2
    
    # Apply NMS using torchvision
    keep = torchvision.ops.nms(boxes, valid_conf, iou_threshold)
    print(f"🎯 NMS kept {len(keep)} detections out of {len(valid_conf)}")
    
    # Create detection results
    for i in keep:
        x1, y1, x2, y2 = boxes[i].tolist()
        confidence = valid_conf[i].item()
        class_id = valid_class[i].item()
        
        class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
        
        detection = Detection(
            class_name=class_name,
            confidence=confidence,
            bbox=[x1, y1, x2, y2]
        )
        results.append(detection)
        print(f"✨ Final detection: {class_name} ({confidence:.3f})")
    
    return results

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    model_path = "runs/train/exp/best.pt"
    
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
    """Detect objects in image using trained YOLO-Nano model"""
    
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
        
        # Post-process with simplified NMS
        detections = simple_nms(
            predictions,
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/yolo/classes")
async def get_classes():
    """Get available object classes"""
    return {
        "classes": class_names,
        "num_classes": len(class_names)
    }

@app.get("/api/debug/model-status")
async def debug_model_status():
    """Debug endpoint to check model status"""
    return {
        "model_loaded": model is not None,
        "device": str(device) if device else "unknown",
        "classes": class_names,
        "num_classes": len(class_names),
        "model_training": model.training if model else None
    }

@app.post("/api/price/analyze", response_model=PriceAnalysisResponse)
async def analyze_price(request: PriceAnalysisRequest):
    """
    Analyze price from image - uses YOLO detection results
    to determine product type for price analysis
    """
    
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # Use YOLO detection to identify product type
        image = decode_base64_image(request.image)
        image_tensor, original_shape = preprocess_image(image)
        image_tensor = image_tensor.to(device)
        
        # Inference
        with torch.no_grad():
            predictions = model(image_tensor)
        
        # Get detections
        detections = simple_nms(predictions, conf_threshold=0.25, iou_threshold=0.45)
        
        if detections:
            # Use the highest confidence detection as the product type
            best_detection = max(detections, key=lambda x: x.confidence)
            product_type = best_detection.class_name
            confidence = best_detection.confidence
            
            # Create mock predictions for compatibility
            all_predictions = [
                {
                    "class": product_type,
                    "confidence": confidence,
                    "bbox": best_detection.bbox
                }
            ]
            
            return PriceAnalysisResponse(
                success=True,
                product_type=product_type,
                confidence=confidence,
                all_predictions=all_predictions,
                message=f"Detected {product_type} with {confidence:.2f} confidence"
            )
        else:
            return PriceAnalysisResponse(
                success=False,
                message="No products detected in image"
            )
            
    except Exception as e:
        print(f"Price analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting YOLO-Nano Detection API Server...")
    print("   Frontend URL: http://localhost:3000")
    print("   API URL: http://localhost:8001")  # Changed port
    print("   Docs: http://localhost:8001/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,  # Changed port
        reload=False
    )