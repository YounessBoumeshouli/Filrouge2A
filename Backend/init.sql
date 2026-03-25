-- Initialize the database with tracking tables
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User profiles table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_hash VARCHAR(64),
    user_agent_hash VARCHAR(64),
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    total_sessions INTEGER DEFAULT 1,
    total_location_scans INTEGER DEFAULT 0,
    total_price_scans INTEGER DEFAULT 0
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    pages_visited INTEGER DEFAULT 0,
    features_used TEXT[] DEFAULT '{}',
    session_duration INTEGER DEFAULT 0
);

-- Location scan history
CREATE TABLE location_scan_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_type VARCHAR(50),
    location_data JSONB,
    scan_method VARCHAR(50),
    accuracy_level VARCHAR(20)
);

-- Price scan purchases
CREATE TABLE price_scan_purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    item_category VARCHAR(100),
    detected_price DECIMAL(10,2),
    owner_price DECIMAL(10,2),
    fair_price_min DECIMAL(10,2),
    fair_price_max DECIMAL(10,2),
    price_difference DECIMAL(10,2),
    recommendation VARCHAR(20),
    purchase_decision VARCHAR(20)
);

-- Hotel stays
CREATE TABLE hotel_stays (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    check_in_date DATE,
    check_out_date DATE,
    hotel_name VARCHAR(255),
    location VARCHAR(255),
    room_type VARCHAR(100),
    price_per_night DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    booking_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User journey map
CREATE TABLE user_journey_map (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_profile_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    journey_date DATE DEFAULT CURRENT_DATE,
    locations_visited JSONB DEFAULT '[]',
    activities JSONB DEFAULT '[]',
    expenses JSONB DEFAULT '[]',
    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_user_profiles_session_id ON user_profiles(session_id);
CREATE INDEX idx_user_sessions_profile_id ON user_sessions(user_profile_id);
CREATE INDEX idx_location_scan_profile_id ON location_scan_history(user_profile_id);
CREATE INDEX idx_price_scan_profile_id ON price_scan_purchases(user_profile_id);
CREATE INDEX idx_hotel_stays_profile_id ON hotel_stays(user_profile_id);
CREATE INDEX idx_journey_map_profile_id ON user_journey_map(user_profile_id);

-- Insert some sample data
INSERT INTO user_profiles (session_id, ip_hash, user_agent_hash, consent_given, preferences) VALUES
('demo-session-1', 'hash1', 'agent1', true, '{"language": "en", "currency": "USD"}'),
('demo-session-2', 'hash2', 'agent2', true, '{"language": "fr", "currency": "EUR"}');