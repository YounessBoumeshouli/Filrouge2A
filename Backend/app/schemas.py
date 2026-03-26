from pydantic import BaseModel
from typing import  Optional

class LocationResponse(BaseModel):
    name: str
    city: str
    description: str
    history: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PriceResponse(BaseModel):
    product_name: str
    estimated_price_min: float
    estimated_price_max: float
    currency: str = "MAD"
    confidence_score: float

class AnalysisRequest(BaseModel):
    # If we were sending JSON, but we are likely using multipart form data for images
    pass
