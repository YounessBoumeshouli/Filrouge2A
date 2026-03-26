from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from ..database import get_db
from ..services.ai_service import AIService
from ..schemas import LocationResponse
from ..models import ScanHistory

router = APIRouter(prefix="/api/location", tags=["location"])


@router.post("/analyze", response_model=LocationResponse)
async def analyze_location(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        result = AIService.analyze_location(contents)

        # Save to history
        history_entry = ScanHistory(
            scan_type="location",
            query_text="Image Scan",
            result_data=json.dumps(result),
            # In a real app, we might also store the image path if saved
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
