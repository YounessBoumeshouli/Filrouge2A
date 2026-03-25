"""
Background task service for processing tracking data
Handles time calculations, journey aggregation, and analytics
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import logging
from typing import List, Dict, Any
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackingProcessor:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def process_session_timeouts(self):
        """End sessions that have been inactive for more than 30 minutes"""
        try:
            with self.SessionLocal() as db:
                cutoff_time = datetime.utcnow() - timedelta(minutes=30)
                
                # Find sessions to timeout
                result = db.execute(text("""
                    SELECT session_id, user_id, session_start 
                    FROM user_sessions 
                    WHERE session_end IS NULL 
                    AND session_start < :cutoff_time
                """), {"cutoff_time": cutoff_time})
                
                sessions_to_end = result.fetchall()
                
                if sessions_to_end:
                    # End the sessions
                    session_ids = [str(session[0]) for session in sessions_to_end]
                    db.execute(text("""
                        UPDATE user_sessions 
                        SET session_end = CURRENT_TIMESTAMP 
                        WHERE session_id = ANY(:session_ids)
                    """), {"session_ids": session_ids})
                    
                    db.commit()
                    logger.info(f"Ended {len(sessions_to_end)} inactive sessions")
                
        except Exception as e:
            logger.error(f"Error processing session timeouts: {e}")
    
    def calculate_location_dwell_times(self):
        """Calculate time spent at locations for scans without time_spent_seconds"""
        try:
            with self.SessionLocal() as db:
                # Find location scans without calculated time
                result = db.execute(text("""
                    SELECT scan_id, user_id, monument_name, scan_timestamp
                    FROM location_scan_history 
                    WHERE time_spent_seconds IS NULL
                    ORDER BY user_id, scan_timestamp
                """))
                
                scans_to_update = result.fetchall()
                
                for scan in scans_to_update:
                    scan_id, user_id, monument_name, scan_timestamp = scan
                    
                    # Find the next scan by the same user
                    next_scan = db.execute(text("""
                        SELECT scan_timestamp 
                        FROM location_scan_history 
                        WHERE user_id = :user_id 
                        AND scan_timestamp > :current_timestamp
                        ORDER BY scan_timestamp ASC 
                        LIMIT 1
                    """), {
                        "user_id": user_id,
                        "current_timestamp": scan_timestamp
                    }).fetchone()
                    
                    if next_scan:
                        # Calculate time difference
                        time_diff = next_scan[0] - scan_timestamp
                        time_spent = int(time_diff.total_seconds())
                        
                        # Cap at 2 hours (7200 seconds) to avoid unrealistic values
                        time_spent = min(time_spent, 7200)
                        
                        # Update the scan
                        db.execute(text("""
                            UPDATE location_scan_history 
                            SET time_spent_seconds = :time_spent 
                            WHERE scan_id = :scan_id
                        """), {
                            "time_spent": time_spent,
                            "scan_id": scan_id
                        })
                
                db.commit()
                logger.info(f"Updated dwell times for {len(scans_to_update)} location scans")
                
        except Exception as e:
            logger.error(f"Error calculating dwell times: {e}")
    
    def generate_user_journey_maps(self):
        """Generate or update user journey maps with aggregated data"""
        try:
            with self.SessionLocal() as db:
                # Get users who need journey map updates
                result = db.execute(text("""
                    SELECT DISTINCT up.user_id, up.created_at
                    FROM user_profiles up
                    LEFT JOIN user_journey_maps ujm ON up.user_id = ujm.user_id
                    WHERE ujm.journey_id IS NULL 
                    OR ujm.end_date < CURRENT_DATE - INTERVAL '1 day'
                """))
                
                users_to_update = result.fetchall()
                
                for user_id, created_at in users_to_update:
                    # Calculate journey statistics
                    stats = self._calculate_user_stats(db, user_id)
                    
                    # Delete existing journey map
                    db.execute(text("""
                        DELETE FROM user_journey_maps WHERE user_id = :user_id
                    """), {"user_id": user_id})
                    
                    # Insert new journey map
                    db.execute(text("""
                        INSERT INTO user_journey_maps (
                            user_id, start_date, end_date, total_scans,
                            most_searched_product_category, most_visited_monument_type
                        ) VALUES (
                            :user_id, :start_date, :end_date, :total_scans,
                            :most_searched_category, :most_visited_monument
                        )
                    """), {
                        "user_id": user_id,
                        "start_date": created_at.date() if created_at else datetime.utcnow().date(),
                        "end_date": datetime.utcnow().date(),
                        "total_scans": stats["total_scans"],
                        "most_searched_category": stats["most_searched_category"],
                        "most_visited_monument": stats["most_visited_monument"]
                    })
                
                db.commit()
                logger.info(f"Updated journey maps for {len(users_to_update)} users")
                
        except Exception as e:
            logger.error(f"Error generating journey maps: {e}")
    
    def _calculate_user_stats(self, db, user_id: str) -> Dict[str, Any]:
        """Calculate statistics for a user"""
        stats = {
            "total_scans": 0,
            "most_searched_category": None,
            "most_visited_monument": None
        }
        
        # Total scans
        location_count = db.execute(text("""
            SELECT COUNT(*) FROM location_scan_history WHERE user_id = :user_id
        """), {"user_id": user_id}).scalar()
        
        price_count = db.execute(text("""
            SELECT COUNT(*) FROM price_scan_purchase WHERE user_id = :user_id
        """), {"user_id": user_id}).scalar()
        
        stats["total_scans"] = (location_count or 0) + (price_count or 0)
        
        # Most searched product category
        category_result = db.execute(text("""
            SELECT product_category, COUNT(*) as count 
            FROM price_scan_purchase 
            WHERE user_id = :user_id AND product_category IS NOT NULL
            GROUP BY product_category 
            ORDER BY count DESC 
            LIMIT 1
        """), {"user_id": user_id}).fetchone()
        
        if category_result:
            stats["most_searched_category"] = category_result[0]
        
        # Most visited monument
        monument_result = db.execute(text("""
            SELECT monument_name, COUNT(*) as count 
            FROM location_scan_history 
            WHERE user_id = :user_id AND monument_name IS NOT NULL
            GROUP BY monument_name 
            ORDER BY count DESC 
            LIMIT 1
        """), {"user_id": user_id}).fetchone()
        
        if monument_result:
            stats["most_visited_monument"] = monument_result[0]
        
        return stats
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate overall analytics report"""
        try:
            with self.SessionLocal() as db:
                report = {}
                
                # Total users
                total_users = db.execute(text("""
                    SELECT COUNT(*) FROM user_profiles
                """)).scalar()
                report["total_users"] = total_users
                
                # Active users (last 7 days)
                active_users = db.execute(text("""
                    SELECT COUNT(*) FROM user_profiles 
                    WHERE last_active > CURRENT_TIMESTAMP - INTERVAL '7 days'
                """)).scalar()
                report["active_users_7d"] = active_users
                
                # Total scans
                total_location_scans = db.execute(text("""
                    SELECT COUNT(*) FROM location_scan_history
                """)).scalar()
                
                total_price_scans = db.execute(text("""
                    SELECT COUNT(*) FROM price_scan_purchase
                """)).scalar()
                
                report["total_location_scans"] = total_location_scans
                report["total_price_scans"] = total_price_scans
                report["total_scans"] = total_location_scans + total_price_scans
                
                # Most popular monuments
                popular_monuments = db.execute(text("""
                    SELECT monument_name, COUNT(*) as visits
                    FROM location_scan_history 
                    WHERE monument_name IS NOT NULL
                    GROUP BY monument_name 
                    ORDER BY visits DESC 
                    LIMIT 10
                """)).fetchall()
                
                report["popular_monuments"] = [
                    {"name": monument[0], "visits": monument[1]} 
                    for monument in popular_monuments
                ]
                
                # Most searched product categories
                popular_categories = db.execute(text("""
                    SELECT product_category, COUNT(*) as searches
                    FROM price_scan_purchase 
                    WHERE product_category IS NOT NULL
                    GROUP BY product_category 
                    ORDER BY searches DESC 
                    LIMIT 10
                """)).fetchall()
                
                report["popular_categories"] = [
                    {"category": category[0], "searches": category[1]} 
                    for category in popular_categories
                ]
                
                # Average ratings
                avg_location_rating = db.execute(text("""
                    SELECT AVG(rating) FROM location_scan_history WHERE rating IS NOT NULL
                """)).scalar()
                
                avg_price_rating = db.execute(text("""
                    SELECT AVG(price_fairness_rating) FROM price_scan_purchase WHERE price_fairness_rating IS NOT NULL
                """)).scalar()
                
                report["avg_location_rating"] = float(avg_location_rating) if avg_location_rating else None
                report["avg_price_rating"] = float(avg_price_rating) if avg_price_rating else None
                
                # Traveler type distribution
                traveler_types = db.execute(text("""
                    SELECT traveler_type, COUNT(*) as count
                    FROM user_profiles 
                    WHERE traveler_type IS NOT NULL
                    GROUP BY traveler_type
                """)).fetchall()
                
                report["traveler_types"] = [
                    {"type": ttype[0], "count": ttype[1]} 
                    for ttype in traveler_types
                ]
                
                report["generated_at"] = datetime.utcnow().isoformat()
                
                logger.info("Generated analytics report")
                return report
                
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old tracking data (GDPR compliance)"""
        try:
            with self.SessionLocal() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Delete old sessions
                deleted_sessions = db.execute(text("""
                    DELETE FROM user_sessions 
                    WHERE session_start < :cutoff_date
                """), {"cutoff_date": cutoff_date}).rowcount
                
                # Delete old location scans
                deleted_location_scans = db.execute(text("""
                    DELETE FROM location_scan_history 
                    WHERE scan_timestamp < :cutoff_date
                """), {"cutoff_date": cutoff_date}).rowcount
                
                # Delete old price scans
                deleted_price_scans = db.execute(text("""
                    DELETE FROM price_scan_purchase 
                    WHERE scan_timestamp < :cutoff_date
                """), {"cutoff_date": cutoff_date}).rowcount
                
                db.commit()
                
                logger.info(f"Cleaned up old data: {deleted_sessions} sessions, {deleted_location_scans} location scans, {deleted_price_scans} price scans")
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def run_all_tasks(self):
        """Run all background processing tasks"""
        logger.info("Starting background processing tasks...")
        
        self.process_session_timeouts()
        self.calculate_location_dwell_times()
        self.generate_user_journey_maps()
        
        logger.info("Background processing tasks completed")

def main():
    """Main function to run background tasks"""
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tourist_helper")
    
    processor = TrackingProcessor(database_url)
    
    # Run all tasks
    processor.run_all_tasks()
    
    # Generate and save analytics report
    report = processor.generate_analytics_report()
    
    # Save report to file
    with open("analytics_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    logger.info("Analytics report saved to analytics_report.json")

if __name__ == "__main__":
    main()