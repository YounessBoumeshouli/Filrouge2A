from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from .database import Base
import uuid

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    scan_type = Column(String, index=True) # 'location' or 'price'
    query_text = Column(String, nullable=True) # Name of monument or product
    result_data = Column(Text, nullable=True) # JSON string representation of result
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    city = Column(String, index=True)
    description = Column(Text)
    image_url = Column(String, nullable=True)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now())
    ip_hash = Column(String(64))
    user_agent_hash = Column(String(64))
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    preferences = Column(JSON, default={})
    total_sessions = Column(Integer, default=1)
    total_location_scans = Column(Integer, default=0)
    total_price_scans = Column(Integer, default=0)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))
    session_start = Column(DateTime, default=func.now())
    session_end = Column(DateTime)
    pages_visited = Column(Integer, default=0)
    features_used = Column(JSON)
    session_duration = Column(Integer, default=0)

class LocationScanHistory(Base):
    __tablename__ = "location_scan_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))
    scan_timestamp = Column(DateTime, default=func.now())
    location_type = Column(String(50))
    location_data = Column(JSON)
    scan_method = Column(String(50))
    accuracy_level = Column(String(20))

class PriceScanPurchase(Base):
    __tablename__ = "price_scan_purchases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))
    scan_timestamp = Column(DateTime, default=func.now())
    item_category = Column(String(100))
    detected_price = Column(Float)
    owner_price = Column(Float)
    fair_price_min = Column(Float)
    fair_price_max = Column(Float)
    price_difference = Column(Float)
    recommendation = Column(String(20))
    purchase_decision = Column(String(20))

class HotelStay(Base):
    __tablename__ = "hotel_stays"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    hotel_name = Column(String(255))
    location = Column(String(255))
    room_type = Column(String(100))
    price_per_night = Column(Float)
    total_cost = Column(Float)
    booking_timestamp = Column(DateTime, default=func.now())

class UserJourneyMap(Base):
    __tablename__ = "user_journey_map"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"))
    journey_date = Column(DateTime, default=func.current_date())
    locations_visited = Column(JSON, default=[])
    activities = Column(JSON, default=[])
    expenses = Column(JSON, default=[])
    satisfaction_score = Column(Integer)
    notes = Column(Text)