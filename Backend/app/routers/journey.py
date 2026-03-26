from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

# import uuid

from ..database import get_db
from ..models import UserProfile, LocationScanHistory, UserJourneyMap
from pydantic import BaseModel

router = APIRouter(prefix="/api/journey", tags=["journey"])


# Pydantic models for request/response
class JourneyStartRequest(BaseModel):
    user_id: str
    start_location: Optional[dict] = None


class LocationVisitRequest(BaseModel):
    user_id: str
    journey_id: str
    location_name: str
    latitude: float
    longitude: float
    distance_km: float
    visit_timestamp: datetime


class JourneyEndRequest(BaseModel):
    user_id: str
    journey_id: str
    end_location: Optional[dict] = None
    total_duration_seconds: int
    locations_visited: int


class JourneyResponse(BaseModel):
    journey_id: str
    status: str
    message: str


class LocationVisitResponse(BaseModel):
    visit_id: str
    status: str
    message: str


@router.post("/start", response_model=JourneyResponse)
async def start_journey(request: JourneyStartRequest, db: Session = Depends(get_db)):
    """Start a new journey tracking session"""
    try:
        # Get or create user profile
        user_profile = (
            db.query(UserProfile)
            .filter(UserProfile.session_id == request.user_id)
            .first()
        )

        if not user_profile:
            user_profile = UserProfile(
                session_id=request.user_id,
                consent_given=True,
                preferences={"journey_tracking": True},
            )
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)

        journey = UserJourneyMap(
            user_profile_id=user_profile.id,
            journey_date=datetime.now(),
            locations_visited=[],
            activities=["journey_started"],
            expenses=[],
            notes=f"Journey started at {datetime.now().isoformat()}",
        )

        db.add(journey)
        db.commit()
        db.refresh(journey)

        return JourneyResponse(
            journey_id=str(journey.id),
            status="started",
            message="Journey tracking started successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start journey: {str(e)}"
        )


@router.post("/visit", response_model=LocationVisitResponse)
async def log_location_visit(
    request: LocationVisitRequest, db: Session = Depends(get_db)
):
    """Log a visit to a tourist location"""
    try:
        # Get user profile
        user_profile = (
            db.query(UserProfile)
            .filter(UserProfile.session_id == request.user_id)
            .first()
        )

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Create location scan entry
        location_scan = LocationScanHistory(
            user_profile_id=user_profile.id,
            scan_timestamp=request.visit_timestamp,
            location_type="tourist_attraction",
            location_data={
                "name": request.location_name,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "distance_km": request.distance_km,
                "visit_type": "journey_tracking",
            },
            scan_method="gps_proximity",
            accuracy_level="high",
        )

        db.add(location_scan)

        # Update journey map
        journey = (
            db.query(UserJourneyMap)
            .filter(
                UserJourneyMap.id == request.journey_id,
                UserJourneyMap.user_profile_id == user_profile.id,
            )
            .first()
        )

        if journey:
            # Update locations visited
            current_locations = journey.locations_visited or []
            current_locations.append(
                {
                    "name": request.location_name,
                    "latitude": request.latitude,
                    "longitude": request.longitude,
                    "visit_time": request.visit_timestamp.isoformat(),
                    "distance_km": request.distance_km,
                }
            )
            journey.locations_visited = current_locations

            # Update activities
            current_activities = journey.activities or []
            current_activities.append(f"visited_{request.location_name}")
            journey.activities = current_activities

        # Update user profile stats
        user_profile.total_location_scans = (user_profile.total_location_scans or 0) + 1
        user_profile.last_active = datetime.now()

        db.commit()
        db.refresh(location_scan)

        return LocationVisitResponse(
            visit_id=str(location_scan.id),
            status="logged",
            message=f"Visit to {request.location_name} logged successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to log location visit: {str(e)}"
        )


@router.post("/end", response_model=JourneyResponse)
async def end_journey(request: JourneyEndRequest, db: Session = Depends(get_db)):
    """End a journey tracking session"""
    try:
        # Get user profile
        user_profile = (
            db.query(UserProfile)
            .filter(UserProfile.session_id == request.user_id)
            .first()
        )

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Update journey
        journey = (
            db.query(UserJourneyMap)
            .filter(
                UserJourneyMap.id == request.journey_id,
                UserJourneyMap.user_profile_id == user_profile.id,
            )
            .first()
        )

        if journey:
            # Update activities
            current_activities = journey.activities or []
            current_activities.append("journey_ended")
            journey.activities = current_activities

            # Update notes
            journey.notes = (
                (journey.notes or "")
                + f" | Journey ended after {request.total_duration_seconds}s with {request.locations_visited} locations visited"
            )

            # Set satisfaction score based on locations visited
            if request.locations_visited >= 3:
                journey.satisfaction_score = 5
            elif request.locations_visited >= 2:
                journey.satisfaction_score = 4
            elif request.locations_visited >= 1:
                journey.satisfaction_score = 3
            else:
                journey.satisfaction_score = 2

        db.commit()

        return JourneyResponse(
            journey_id=request.journey_id,
            status="ended",
            message=f"Journey ended successfully. Visited {request.locations_visited} locations in {request.total_duration_seconds} seconds",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end journey: {str(e)}")


@router.get("/history/{user_id}")
async def get_journey_history(user_id: str, db: Session = Depends(get_db)):
    """Get journey history for a user"""
    try:
        # Get user profile
        user_profile = (
            db.query(UserProfile).filter(UserProfile.session_id == user_id).first()
        )

        if not user_profile:
            return {"journeys": [], "total": 0}

        # Get all journeys
        journeys = (
            db.query(UserJourneyMap)
            .filter(UserJourneyMap.user_profile_id == user_profile.id)
            .order_by(UserJourneyMap.journey_date.desc())
            .all()
        )

        journey_data = []
        for journey in journeys:
            journey_data.append(
                {
                    "journey_id": str(journey.id),
                    "date": (
                        journey.journey_date.isoformat()
                        if journey.journey_date
                        else None
                    ),
                    "locations_visited": journey.locations_visited or [],
                    "activities": journey.activities or [],
                    "satisfaction_score": journey.satisfaction_score,
                    "notes": journey.notes,
                }
            )

        return {
            "journeys": journey_data,
            "total": len(journey_data),
            "user_stats": {
                "total_location_scans": user_profile.total_location_scans or 0,
                "member_since": (
                    user_profile.created_at.isoformat()
                    if user_profile.created_at
                    else None
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get journey history: {str(e)}"
        )


@router.get("/locations/nearby")
async def get_nearby_locations(lat: float, lon: float, radius_km: float = 1.0):
    """Get nearby tourist locations (mock data for demo)"""

    # Mock tourist locations in Morocco
    locations = [
        {
            "id": 1,
            "name": "Hassan II Mosque",
            "latitude": 33.6084,
            "longitude": -7.6324,
            "city": "Casablanca",
            "type": "mosque",
            "description": "One of the largest mosques in the world",
        },
        {
            "id": 2,
            "name": "Jemaa el-Fnaa",
            "latitude": 31.6260,
            "longitude": -7.9890,
            "city": "Marrakech",
            "type": "square",
            "description": "Famous market square and UNESCO World Heritage site",
        },
        {
            "id": 3,
            "name": "Koutoubia Mosque",
            "latitude": 31.6236,
            "longitude": -7.9993,
            "city": "Marrakech",
            "type": "mosque",
            "description": "Iconic minaret and mosque in Marrakech",
        },
        {
            "id": 4,
            "name": "Majorelle Garden",
            "latitude": 31.6417,
            "longitude": -7.9930,
            "city": "Marrakech",
            "type": "garden",
            "description": "Beautiful botanical garden designed by Jacques Majorelle",
        },
        {
            "id": 5,
            "name": "Chefchaouen Blue City",
            "latitude": 35.1689,
            "longitude": -5.2636,
            "city": "Chefchaouen",
            "type": "city",
            "description": "Famous blue-painted city in the mountains",
        },
    ]

    # Calculate distances and filter by radius
    import math

    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth's radius in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(
            math.radians(lat1)
        ) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    nearby = []
    for location in locations:
        distance = calculate_distance(
            lat, lon, location["latitude"], location["longitude"]
        )
        if distance <= radius_km:
            location["distance_km"] = round(distance, 2)
            nearby.append(location)

    return {
        "locations": nearby,
        "search_center": {"latitude": lat, "longitude": lon},
        "radius_km": radius_km,
        "total_found": len(nearby),
    }
