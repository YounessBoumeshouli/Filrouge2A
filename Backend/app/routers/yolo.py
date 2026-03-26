"""
YOLO-Nano Detection Router
FastAPI endpoints for object detection using YOLO-Nano
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
from PIL import Image

from ..services.yolo_service import get_yolo_service

router = APIRouter(prefix="/api/yolo", tags=["YOLO Detection"])


class DetectionRequest(BaseModel):
    image: str  # base64 encoded image
    conf_threshold: Optional[float] = 0.25
    iou_threshold: Optional[float] = 0.45


class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str
    category: str  # 'monument' or 'product'


class DetectionResponse(BaseModel):
    success: bool
    detections: List[Detection]
    image_size: Optional[List[int]] = None
    visualized_image: Optional[str] = None
    model_info: Optional[dict] = None
    error: Optional[str] = None


@router.get("/status")
async def get_model_status():
    """Get YOLO-Nano model status"""
    service = get_yolo_service()

    return {
        "model_loaded": service.model is not None,
        "device": str(service.device),
        "classes": len(service.class_names),
        "class_names": service.class_names,
        "image_size": service.img_size,
        "conf_threshold": service.conf_thres,
        "iou_threshold": service.iou_thres,
    }


@router.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: DetectionRequest):
    """Detect objects in uploaded image using YOLO-Nano"""
    try:
        service = get_yolo_service()

        if service.model is None:
            raise HTTPException(
                status_code=503,
                detail="YOLO-Nano model not loaded. Please train the model first.",
            )

        # Process the image
        result = service.process_image_base64(
            request.image, request.conf_threshold, request.iou_threshold
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return DetectionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/detect-file")
async def detect_objects_file(
    file: UploadFile = File(...),
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
):
    """Detect objects in uploaded file using YOLO-Nano"""
    try:
        service = get_yolo_service()

        if service.model is None:
            raise HTTPException(
                status_code=503,
                detail="YOLO-Nano model not loaded. Please train the model first.",
            )

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Detect objects
        result = service.detect_objects(image, conf_threshold, iou_threshold)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Add visualization
        if result["detections"]:
            img_with_boxes = service.visualize_detections(image, result["detections"])

            # Convert to base64
            img_pil = Image.fromarray(img_with_boxes)
            buffer = io.BytesIO()
            img_pil.save(buffer, format="JPEG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            result["visualized_image"] = f"data:image/jpeg;base64,{img_base64}"

        return DetectionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.get("/classes")
async def get_classes():
    """Get list of supported classes"""
    service = get_yolo_service()

    monuments = []
    products = []

    for i, class_name in enumerate(service.class_names):
        if i <= 9:  # Monuments (0-9)
            monuments.append({"id": i, "name": class_name, "category": "monument"})
        else:  # Products (10-16)
            products.append({"id": i, "name": class_name, "category": "product"})

    return {
        "total_classes": len(service.class_names),
        "monuments": monuments,
        "products": products,
    }


@router.post("/analyze")
async def analyze_image(request: DetectionRequest):
    """Analyze image and provide detailed information about detected objects"""
    try:
        service = get_yolo_service()

        if service.model is None:
            raise HTTPException(
                status_code=503,
                detail="YOLO-Nano model not loaded. Please train the model first.",
            )

        # Process the image
        result = service.process_image_base64(
            request.image, request.conf_threshold, request.iou_threshold
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Analyze detections
        analysis = {
            "total_objects": len(result["detections"]),
            "monuments_found": [],
            "products_found": [],
            "confidence_stats": {"average": 0, "highest": 0, "lowest": 1},
        }

        if result["detections"]:
            confidences = [det["confidence"] for det in result["detections"]]
            analysis["confidence_stats"] = {
                "average": round(sum(confidences) / len(confidences), 3),
                "highest": round(max(confidences), 3),
                "lowest": round(min(confidences), 3),
            }

            for det in result["detections"]:
                if det["category"] == "monument":
                    analysis["monuments_found"].append(
                        {"name": det["class_name"], "confidence": det["confidence"]}
                    )
                else:
                    analysis["products_found"].append(
                        {"name": det["class_name"], "confidence": det["confidence"]}
                    )

        return {**result, "analysis": analysis}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
