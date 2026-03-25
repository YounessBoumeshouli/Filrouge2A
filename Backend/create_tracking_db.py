"""
Database migration script for user tracking system
Run this to create all tracking tables in PostgreSQL
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tourist_helper")

def create_tracking_tables():
    """Create all tracking tables"""
    
    engine = create_engine(DATABASE_URL)
    
    # SQL statements to create tracking tables
    tracking_tables_sql = """
    -- User Profiles Table
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        preferred_currency VARCHAR DEFAULT 'MAD',
        traveler_type VARCHAR CHECK (traveler_type IN ('solo', 'couple', 'family', 'business')),
        consent_tracking BOOLEAN DEFAULT FALSE
    );

    -- User Sessions Table
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
        session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_end TIMESTAMP,
        device_type VARCHAR,
        ip_hash VARCHAR,
        location_region VARCHAR
    );

    -- Location Scan History Table
    CREATE TABLE IF NOT EXISTS location_scan_history (
        scan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
        session_id UUID REFERENCES user_sessions(session_id) ON DELETE CASCADE,
        monument_name VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        time_spent_seconds INTEGER,
        was_guided BOOLEAN DEFAULT FALSE,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5)
    );

    -- Price Scan & Purchase Table
    CREATE TABLE IF NOT EXISTS price_scan_purchase (
        scan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
        session_id UUID REFERENCES user_sessions(session_id) ON DELETE CASCADE,
        product_name VARCHAR,
        product_category VARCHAR,
        detected_price FLOAT,
        actual_price_paid FLOAT,
        owner_asking_price FLOAT,
        price_fairness_rating INTEGER CHECK (price_fairness_rating >= 1 AND price_fairness_rating <= 5),
        scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        purchase_made BOOLEAN DEFAULT FALSE,
        location VARCHAR
    );

    -- Hotel Stays Table
    CREATE TABLE IF NOT EXISTS hotel_stays (
        stay_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
        hotel_name VARCHAR,
        check_in_date DATE,
        check_out_date DATE,
        night_count INTEGER,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        review_text TEXT,
        price_per_night FLOAT,
        location VARCHAR
    );

    -- User Journey Maps Table
    CREATE TABLE IF NOT EXISTS user_journey_maps (
        journey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES user_profiles(user_id) ON DELETE CASCADE,
        city_sequence TEXT[], -- Array of cities
        country_sequence TEXT[], -- Array of countries
        start_date DATE,
        end_date DATE,
        total_scans INTEGER DEFAULT 0,
        most_searched_product_category VARCHAR,
        most_visited_monument_type VARCHAR
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_sessions_start ON user_sessions(session_start);
    CREATE INDEX IF NOT EXISTS idx_location_scans_user_id ON location_scan_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_location_scans_timestamp ON location_scan_history(scan_timestamp);
    CREATE INDEX IF NOT EXISTS idx_price_scans_user_id ON price_scan_purchase(user_id);
    CREATE INDEX IF NOT EXISTS idx_price_scans_timestamp ON price_scan_purchase(scan_timestamp);
    CREATE INDEX IF NOT EXISTS idx_hotel_stays_user_id ON hotel_stays(user_id);
    CREATE INDEX IF NOT EXISTS idx_journey_maps_user_id ON user_journey_maps(user_id);

    -- Create a function to automatically update last_active
    CREATE OR REPLACE FUNCTION update_last_active()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE user_profiles 
        SET last_active = CURRENT_TIMESTAMP 
        WHERE user_id = NEW.user_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Create triggers to update last_active on any tracking activity
    DROP TRIGGER IF EXISTS trigger_update_last_active_location ON location_scan_history;
    CREATE TRIGGER trigger_update_last_active_location
        AFTER INSERT ON location_scan_history
        FOR EACH ROW EXECUTE FUNCTION update_last_active();

    DROP TRIGGER IF EXISTS trigger_update_last_active_price ON price_scan_purchase;
    CREATE TRIGGER trigger_update_last_active_price
        AFTER INSERT ON price_scan_purchase
        FOR EACH ROW EXECUTE FUNCTION update_last_active();

    -- Create a view for user analytics
    CREATE OR REPLACE VIEW user_analytics AS
    SELECT 
        up.user_id,
        up.email,
        up.traveler_type,
        up.created_at,
        up.last_active,
        COUNT(DISTINCT us.session_id) as total_sessions,
        COUNT(DISTINCT lsh.scan_id) as location_scans,
        COUNT(DISTINCT psp.scan_id) as price_scans,
        COUNT(DISTINCT hs.stay_id) as hotel_stays,
        AVG(lsh.rating) as avg_location_rating,
        AVG(psp.price_fairness_rating) as avg_price_rating,
        AVG(hs.rating) as avg_hotel_rating
    FROM user_profiles up
    LEFT JOIN user_sessions us ON up.user_id = us.user_id
    LEFT JOIN location_scan_history lsh ON up.user_id = lsh.user_id
    LEFT JOIN price_scan_purchase psp ON up.user_id = psp.user_id
    LEFT JOIN hotel_stays hs ON up.user_id = hs.user_id
    GROUP BY up.user_id, up.email, up.traveler_type, up.created_at, up.last_active;
    """
    
    try:
        with engine.connect() as connection:
            # Execute the SQL statements
            for statement in tracking_tables_sql.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
            connection.commit()
            
        print("✅ Successfully created all tracking tables and indexes")
        print("✅ Created triggers for automatic last_active updates")
        print("✅ Created user_analytics view")
        
    except Exception as e:
        print(f"❌ Error creating tracking tables: {e}")
        raise

def create_sample_data():
    """Create sample tracking data for testing"""
    
    engine = create_engine(DATABASE_URL)
    
    sample_data_sql = """
    -- Insert sample user
    INSERT INTO user_profiles (email, traveler_type, consent_tracking) 
    VALUES ('test@example.com', 'solo', TRUE)
    ON CONFLICT (email) DO NOTHING;
    
    -- Get the user ID
    WITH sample_user AS (
        SELECT user_id FROM user_profiles WHERE email = 'test@example.com'
    )
    -- Insert sample session
    INSERT INTO user_sessions (user_id, device_type, location_region)
    SELECT user_id, 'desktop', 'Morocco' FROM sample_user;
    
    -- Insert sample location scans
    WITH sample_user AS (
        SELECT user_id FROM user_profiles WHERE email = 'test@example.com'
    ),
    sample_session AS (
        SELECT session_id FROM user_sessions 
        WHERE user_id = (SELECT user_id FROM sample_user)
        ORDER BY session_start DESC LIMIT 1
    )
    INSERT INTO location_scan_history (user_id, session_id, monument_name, latitude, longitude, rating)
    SELECT 
        su.user_id, 
        ss.session_id,
        monument_name,
        latitude,
        longitude,
        rating
    FROM sample_user su, sample_session ss,
    (VALUES 
        ('Jemaa el-Fna', 31.6260, -7.9890, 5),
        ('Koutoubia Mosque', 31.6248, -7.9928, 4),
        ('Bahia Palace', 31.6214, -7.9844, 5)
    ) AS monuments(monument_name, latitude, longitude, rating);
    
    -- Insert sample price scans
    WITH sample_user AS (
        SELECT user_id FROM user_profiles WHERE email = 'test@example.com'
    ),
    sample_session AS (
        SELECT session_id FROM user_sessions 
        WHERE user_id = (SELECT user_id FROM sample_user)
        ORDER BY session_start DESC LIMIT 1
    )
    INSERT INTO price_scan_purchase (user_id, session_id, product_name, product_category, detected_price, owner_asking_price, location)
    SELECT 
        su.user_id, 
        ss.session_id,
        product_name,
        product_category,
        detected_price,
        owner_asking_price,
        location
    FROM sample_user su, sample_session ss,
    (VALUES 
        ('Moroccan Leather Babouches', 'Leather', 120.0, 150.0, 'Souk Smata'),
        ('Argan Oil 250ml', 'Argan', 200.0, 250.0, 'Souk El Attarine'),
        ('Hand-painted Tagine', 'Ceramics', 35.0, 45.0, 'Souk Semmarine')
    ) AS products(product_name, product_category, detected_price, owner_asking_price, location);
    """
    
    try:
        with engine.connect() as connection:
            for statement in sample_data_sql.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
            connection.commit()
            
        print("✅ Successfully created sample tracking data")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Creating tracking database tables...")
    create_tracking_tables()
    
    print("\n📊 Creating sample data...")
    create_sample_data()
    
    print("\n✅ Database setup complete!")
    print("You can now use the tracking system with real database persistence.")