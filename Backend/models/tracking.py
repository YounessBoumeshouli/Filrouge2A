from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    preferred_currency = Column(String, default="MAD")
    traveler_type = Column(String)  # solo, couple, family, business
    consent_tracking = Column(Boolean, default=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    location_scans = relationship("LocationScanHistory", back_populates="user")
    price_scans = relationship("PriceScanPurchase", back_populates="user")
    hotel_stays = relationship("HotelStay", back_populates="user")
    journeys = relationship("UserJourneyMap", back_populates="user")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"))
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    device_type = Column(String)
    ip_hash = Column(String)
    location_region = Column(String)
    
    # Relationships
    user = relationship("UserProfile", back_populates="sessions")
    location_scans = relationship("LocationScanHistory", back_populates="session")
    price_scans = relationship("PriceScanPurchase", back_populates="session")

class LocationScanHistory(Base):
    __tablename__ = "location_scan_history"
    
    scan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.session_id"))
    monument_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    scan_timestamp = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Integer)
    was_guided = Column(Boolean, default=False)
    rating = Column(Integer)  # 1-5 stars
    
    # Relationships
    user = relationship("UserProfile", back_populates="location_scans")
    session = relationship("UserSession", back_populates="location_scans")

class PriceScanPurchase(Base):
    __tablename__ = "price_scan_purchase"
    
    scan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.session_id"))
    product_name = Column(String)
    product_category = Column(String)  # artisanat, alimentation, souvenir
    detected_price = Column(Float)
    actual_price_paid = Column(Float)
    owner_asking_price = Column(Float)  # Added for owner price input
    price_fairness_rating = Column(Integer)  # 1-5 stars
    scan_timestamp = Column(DateTime, default=datetime.utcnow)
    purchase_made = Column(Boolean, default=False)
    location = Column(String)
    
    # Relationships
    user = relationship("UserProfile", back_populates="price_scans")
    session = relationship("UserSession", back_populates="price_scans")

class HotelStay(Base):
    __tablename__ = "hotel_stays"
    
    stay_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"))
    hotel_name = Column(String)
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    night_count = Column(Integer)
    rating = Column(Integer)  # 1-5 stars
    review_text = Column(Text)
    price_per_night = Column(Float)
    location = Column(String)
    
    # Relationships
    user = relationship("UserProfile", back_populates="hotel_stays")

class UserJourneyMap(Base):
    __tablename__ = "user_journey_maps"
    
    journey_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"))
    city_sequence = Column(ARRAY(String))
    country_sequence = Column(ARRAY(String))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_scans = Column(Integer, default=0)
    most_searched_product_category = Column(String)
    most_visited_monument_type = Column(String)
    
    # Relationships
    user = relationship("UserProfile", back_populates="journeys")