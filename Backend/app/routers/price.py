from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import base64
import io
from PIL import Image
import sys
import os
from ..database import get_db
from ..schemas import PriceResponse
from ..models import ScanHistory

# Try to load classifiers, but make them optional
model_api = None
classifier_status = "No classifier loaded"

# Add the AI model path to Python path
ai_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Ai', 'efficientNet')
if os.path.exists(ai_path):
    sys.path.append(ai_path)
    
    try:
        from rule_based_classifier import RuleBasedClassifier
        model_api = RuleBasedClassifier()
        classifier_status = "✅ Rule-based classifier loaded successfully"
    except ImportError:
        try:
            from improved_classifier import ImprovedPriceClassifier
            model_api = ImprovedPriceClassifier()
            classifier_status = "✅ Improved price classifier loaded successfully"
        except ImportError:
            classifier_status = "⚠️ No AI classifiers available - using mock data"
    except Exception as e:
        classifier_status = f"⚠️ Classifier loading error: {e}"
else:
    classifier_status = "⚠️ AI model directory not found - using mock data"

print(classifier_status)
router = APIRouter(prefix="/api/price", tags=["price"])

@router.post("/analyze")
async def analyze_price(file: UploadFile = File(None), image: str = None, db: Session = Depends(get_db)):
    try:
        # Handle both file upload and base64 image
        if file:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="File must be an image")
            contents = await file.read()
            image_base64 = base64.b64encode(contents).decode('utf-8')
        elif image:
            image_base64 = image
        else:
            raise HTTPException(status_code=400, detail="Either file or image data required")
        
        # Use trained model if available
        if model_api:
            result = model_api.predict_from_base64(image_base64)
        else:
            # Fallback mock response with uncertainty handling
            result = {
                "success": True,
                "product_type": "uncertain",
                "confidence": 0.15,
                "message": "Model prediction has low confidence. This could be leather, textiles, or crafts.",
                "top_suggestions": [
                    {"category": "leather", "confidence": 0.15},
                    {"category": "textiles", "confidence": 0.14},
                    {"category": "crafts", "confidence": 0.13}
                ],
                "all_predictions": {
                    "leather": 0.15,
                    "textiles": 0.14,
                    "crafts": 0.13,
                    "spices": 0.12,
                    "jewelry": 0.12,
                    "lanterns": 0.11,
                    "argan": 0.11,
                    "price_tags": 0.12
                }
            }
        
        # Save to history if successful
        if result.get("success"):
            history_entry = ScanHistory(
                scan_type="price",
                query_text="Image Scan",
                result_data=json.dumps(result),
                confidence_score=result.get("confidence", 0)
            )
            db.add(history_entry)
            db.commit()
            db.refresh(history_entry)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Price analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
