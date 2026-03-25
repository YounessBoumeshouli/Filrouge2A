from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import uuid

# Import from the correct path structure
from app.database import get_db

router = APIRouter(prefix="/track", tags=["tracking"])

# Pydantic models for request/response
class LocationScanRequest(BaseModel):
    monument_name: str
    latitude: float
    longitude: float
    was_guided: bool = False
    rating: Optional[int] = None

class PriceScanRequest(BaseModel):
    product_name: str
    product_category: str
    detected_price: float
    owner_asking_price: Optional[float] = None
    location: str

class PriceRatingRequest(BaseModel):
    scan_id: str
    actual_price_paid: Optional[float] = None
    price_fairness_rating: int
    purchase_made: bool = False

class HotelStayRequest(BaseModel):
    hotel_name: str
    check_in_date: datetime
    check_out_date: datetime
    rating: int
    review_text: Optional[str] = None
    price_per_night: Optional[float] = None
    location: str

class SessionEndRequest(BaseModel):
    session_id: str

# Helper functions
def get_or_create_user(user_id: str, db: Session):
    """Get or create user profile"""
    # Check if user exists
    result = db.execute(text(
        "SELECT user_id FROM user_profiles WHERE user_id = :user_id"
    ), {"user_id": user_id})
    
    if result.fetchone():
        return user_id
    
    # Create new user with default email
    db.execute(text(
        "INSERT INTO user_profiles (user_id, email, consent_tracking) VALUES (:user_id, :email, :consent)"
    ), {
        "user_id": user_id,
        "email": f"{user_id}@temp.local",
        "consent": True
    })
    db.commit()
    return user_id

def get_or_create_session(user_id: str, device_type: str, ip_address: str, db: Session):
    """Get active session or create new one"""
    # Hash IP for privacy
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
    
    # Check for active session (within last 30 minutes)
    cutoff_time = datetime.utcnow() - timedelta(minutes=30)
    result = db.execute(text(
        "SELECT session_id FROM user_sessions WHERE user_id = :user_id AND session_start > :cutoff AND session_end IS NULL ORDER BY session_start DESC LIMIT 1"
    ), {"user_id": user_id, "cutoff": cutoff_time})
    
    existing_session = result.fetchone()
    if existing_session:
        return existing_session[0]
    
    # Create new session
    session_id = str(uuid.uuid4())
    db.execute(text(
        "INSERT INTO user_sessions (session_id, user_id, device_type, ip_hash, location_region) VALUES (:session_id, :user_id, :device_type, :ip_hash, :location_region)"
    ), {
        "session_id": session_id,
        "user_id": user_id,
        "device_type": device_type,
        "ip_hash": ip_hash,
        "location_region": "Morocco"
    })
    db.commit()
    return session_id

def update_user_activity(user_id: str, db: Session):
    """Update user's last_active timestamp"""
    db.execute(text(
        "UPDATE user_profiles SET last_active = CURRENT_TIMESTAMP WHERE user_id = :user_id"
    ), {"user_id": user_id})
    db.commit()

def calculate_time_spent(user_id: str, location: str, db: Session):
    """Calculate time spent at a location based on scan history"""
    # Get previous scan at same location without time_spent_seconds
    result = db.execute(text(
        "SELECT scan_id, scan_timestamp FROM location_scan_history WHERE user_id = :user_id AND monument_name = :location AND time_spent_seconds IS NULL ORDER BY scan_timestamp DESC LIMIT 1"
    ), {"user_id": user_id, "location": location})
    
    previous_scan = result.fetchone()
    if previous_scan:
        scan_id, scan_timestamp = previous_scan
        time_diff = datetime.utcnow() - scan_timestamp
        time_spent = int(time_diff.total_seconds())
        
        # Update the previous scan with calculated time
        db.execute(text(
            "UPDATE location_scan_history SET time_spent_seconds = :time_spent WHERE scan_id = :scan_id"
        ), {"time_spent": time_spent, "scan_id": scan_id})
        db.commit()

# API Endpoints
@router.post("/location-scan")
async def track_location_scan(
    request: LocationScanRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user",
    device_type: str = "web",
    ip_address: str = "127.0.0.1",
    db: Session = Depends(get_db)
):
    """Store location recognition event"""
    try:
        # Ensure user exists
        get_or_create_user(user_id, db)
        
        # Get or create session
        session_id = get_or_create_session(user_id, device_type, ip_address, db)
        
        # Calculate time spent at previous location
        background_tasks.add_task(calculate_time_spent, user_id, request.monument_name, db)
        
        # Create location scan record
        scan_id = str(uuid.uuid4())
        db.execute(text(
            "INSERT INTO location_scan_history (scan_id, user_id, session_id, monument_name, latitude, longitude, was_guided, rating) VALUES (:scan_id, :user_id, :session_id, :monument_name, :latitude, :longitude, :was_guided, :rating)"
        ), {
            "scan_id": scan_id,
            "user_id": user_id,
            "session_id": session_id,
            "monument_name": request.monument_name,
            "latitude": request.latitude,
            "longitude": request.longitude,
            "was_guided": request.was_guided,
            "rating": request.rating
        })
        db.commit()
        
        print(f"📍 Location Scan Stored: {request.monument_name} by {user_id}")
        
        return {"status": "success", "scan_id": scan_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/price-scan")
async def track_price_scan(
    request: PriceScanRequest,
    user_id: str = "default_user",
    device_type: str = "web",
    ip_address: str = "127.0.0.1",
    db: Session = Depends(get_db)
):
    """Store product price scan"""
    try:
        # Ensure user exists
        get_or_create_user(user_id, db)
        
        # Get or create session
        session_id = get_or_create_session(user_id, device_type, ip_address, db)
        
        # Create price scan record
        scan_id = str(uuid.uuid4())
        db.execute(text(
            "INSERT INTO price_scan_purchase (scan_id, user_id, session_id, product_name, product_category, detected_price, owner_asking_price, location) VALUES (:scan_id, :user_id, :session_id, :product_name, :product_category, :detected_price, :owner_asking_price, :location)"
        ), {
            "scan_id": scan_id,
            "user_id": user_id,
            "session_id": session_id,
            "product_name": request.product_name,
            "product_category": request.product_category,
            "detected_price": request.detected_price,
            "owner_asking_price": request.owner_asking_price,
            "location": request.location
        })
        db.commit()
        
        print(f"💰 Price Scan Stored: {request.product_name} - {request.detected_price} MAD by {user_id}")
        
        return {"status": "success", "scan_id": scan_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/price-rating")
async def track_price_rating(
    request: PriceRatingRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Submit rating for a product scan"""
    try:
        # Update the price scan with rating and purchase info
        result = db.execute(text(
            "UPDATE price_scan_purchase SET actual_price_paid = :actual_price, price_fairness_rating = :rating, purchase_made = :purchase WHERE scan_id = :scan_id AND user_id = :user_id"
        ), {
            "actual_price": request.actual_price_paid,
            "rating": request.price_fairness_rating,
            "purchase": request.purchase_made,
            "scan_id": request.scan_id,
            "user_id": user_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Price scan not found")
        
        db.commit()
        
        print(f"⭐ Price Rating Stored: {request.price_fairness_rating} stars for scan {request.scan_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hotel-stay")
async def track_hotel_stay(
    request: HotelStayRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Store hotel stay and rating"""
    try:
        # Calculate night count
        night_count = (request.check_out_date - request.check_in_date).days
        
        tracking_data = {
            "type": "hotel_stay",
            "user_id": user_id,
            "hotel_name": request.hotel_name,
            "check_in_date": request.check_in_date.isoformat(),
            "check_out_date": request.check_out_date.isoformat(),
            "night_count": night_count,
            "rating": request.rating,
            "review_text": request.review_text,
            "price_per_night": request.price_per_night,
            "location": request.location,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"🏨 Hotel Stay Tracked: {tracking_data}")
        
        return {"status": "success", "stay_id": str(uuid.uuid4())}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/end")
async def end_session(
    request: SessionEndRequest,
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """End current session manually"""
    try:
        tracking_data = {
            "type": "session_end",
            "user_id": user_id,
            "session_id": request.session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"🔚 Session End Tracked: {tracking_data}")
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/journey/{user_id}")
async def get_user_journey(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve aggregated journey summary"""
    try:
        # Get user analytics from the view
        result = db.execute(text(
            "SELECT * FROM user_analytics WHERE user_id = :user_id"
        ), {"user_id": user_id})
        
        user_data = result.fetchone()
        
        if not user_data:
            # Return empty journey data
            return {
                "user_id": user_id,
                "total_scans": 0,
                "most_searched_product_category": None,
                "most_visited_monument_type": None,
                "location_scans_count": 0,
                "price_scans_count": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        # Convert to dict
        columns = result.keys()
        user_dict = dict(zip(columns, user_data))
        
        # Get most searched product category
        category_result = db.execute(text(
            "SELECT product_category, COUNT(*) as count FROM price_scan_purchase WHERE user_id = :user_id AND product_category IS NOT NULL GROUP BY product_category ORDER BY count DESC LIMIT 1"
        ), {"user_id": user_id})
        
        most_searched_category = category_result.fetchone()
        
        # Get most visited monument type
        monument_result = db.execute(text(
            "SELECT monument_name, COUNT(*) as count FROM location_scan_history WHERE user_id = :user_id AND monument_name IS NOT NULL GROUP BY monument_name ORDER BY count DESC LIMIT 1"
        ), {"user_id": user_id})
        
        most_visited_monument = monument_result.fetchone()
        
        journey_data = {
            "user_id": str(user_dict["user_id"]),
            "email": user_dict["email"],
            "traveler_type": user_dict["traveler_type"],
            "created_at": user_dict["created_at"].isoformat() if user_dict["created_at"] else None,
            "last_active": user_dict["last_active"].isoformat() if user_dict["last_active"] else None,
            "total_sessions": user_dict["total_sessions"] or 0,
            "location_scans_count": user_dict["location_scans"] or 0,
            "price_scans_count": user_dict["price_scans"] or 0,
            "hotel_stays_count": user_dict["hotel_stays"] or 0,
            "avg_location_rating": float(user_dict["avg_location_rating"]) if user_dict["avg_location_rating"] else None,
            "avg_price_rating": float(user_dict["avg_price_rating"]) if user_dict["avg_price_rating"] else None,
            "avg_hotel_rating": float(user_dict["avg_hotel_rating"]) if user_dict["avg_hotel_rating"] else None,
            "most_searched_product_category": most_searched_category[0] if most_searched_category else None,
            "most_visited_monument_type": most_visited_monument[0] if most_visited_monument else None,
            "total_scans": (user_dict["location_scans"] or 0) + (user_dict["price_scans"] or 0)
        }
        
        print(f"📊 Journey Data Retrieved for {user_id}: {journey_data['total_scans']} total scans")
        
        return journey_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))