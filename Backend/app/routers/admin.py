from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics overview"""
    try:
        overview = {}

        # Total users
        total_users = db.execute(text("SELECT COUNT(*) FROM user_profiles")).scalar()
        overview["total_users"] = total_users or 0

        # Active users (last 7 days)
        active_users = db.execute(text("""
            SELECT COUNT(*) FROM user_profiles 
            WHERE last_active > CURRENT_TIMESTAMP - INTERVAL '7 days'
        """)).scalar()
        overview["active_users_7d"] = active_users or 0

        # Total scans
        location_scans = db.execute(
            text("SELECT COUNT(*) FROM location_scan_history")
        ).scalar()
        price_scans = db.execute(
            text("SELECT COUNT(*) FROM price_scan_purchase")
        ).scalar()

        overview["location_scans"] = location_scans or 0
        overview["price_scans"] = price_scans or 0
        overview["total_scans"] = (location_scans or 0) + (price_scans or 0)

        # Sessions
        total_sessions = db.execute(text("SELECT COUNT(*) FROM user_sessions")).scalar()
        active_sessions = db.execute(text("""
            SELECT COUNT(*) FROM user_sessions 
            WHERE session_end IS NULL 
            AND session_start > CURRENT_TIMESTAMP - INTERVAL '30 minutes'
        """)).scalar()

        overview["total_sessions"] = total_sessions or 0
        overview["active_sessions"] = active_sessions or 0

        # Average ratings
        avg_location_rating = db.execute(text("""
            SELECT AVG(rating) FROM location_scan_history WHERE rating IS NOT NULL
        """)).scalar()

        avg_price_rating = db.execute(text("""
            SELECT AVG(price_fairness_rating) FROM price_scan_purchase WHERE price_fairness_rating IS NOT NULL
        """)).scalar()

        overview["avg_location_rating"] = (
            float(avg_location_rating) if avg_location_rating else None
        )
        overview["avg_price_rating"] = (
            float(avg_price_rating) if avg_price_rating else None
        )

        return overview

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/popular-places")
async def get_popular_places(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)
):
    """Get most popular monuments/places"""
    try:
        result = db.execute(
            text("""
            SELECT 
                monument_name, 
                COUNT(*) as visits,
                AVG(rating) as avg_rating,
                AVG(time_spent_seconds) as avg_time_spent
            FROM location_scan_history 
            WHERE monument_name IS NOT NULL
            GROUP BY monument_name 
            ORDER BY visits DESC 
            LIMIT :limit
        """),
            {"limit": limit},
        )

        places = []
        for row in result:
            places.append(
                {
                    "name": row[0],
                    "visits": row[1],
                    "avg_rating": float(row[2]) if row[2] else None,
                    "avg_time_spent_minutes": float(row[3] / 60) if row[3] else None,
                }
            )

        return {"popular_places": places}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/popular-products")
async def get_popular_products(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)
):
    """Get most searched product categories"""
    try:
        result = db.execute(
            text("""
            SELECT 
                product_category, 
                COUNT(*) as searches,
                AVG(detected_price) as avg_detected_price,
                AVG(owner_asking_price) as avg_owner_price,
                AVG(price_fairness_rating) as avg_rating,
                COUNT(CASE WHEN purchase_made = true THEN 1 END) as purchases
            FROM price_scan_purchase 
            WHERE product_category IS NOT NULL
            GROUP BY product_category 
            ORDER BY searches DESC 
            LIMIT :limit
        """),
            {"limit": limit},
        )

        products = []
        for row in result:
            products.append(
                {
                    "category": row[0],
                    "searches": row[1],
                    "avg_detected_price": float(row[2]) if row[2] else None,
                    "avg_owner_price": float(row[3]) if row[3] else None,
                    "avg_rating": float(row[4]) if row[4] else None,
                    "purchases": row[5],
                    "conversion_rate": float(row[5] / row[1]) if row[1] > 0 else 0,
                }
            )

        return {"popular_products": products}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/user-activity")
async def get_user_activity(
    days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)
):
    """Get user activity over time"""
    try:
        # Daily activity for the last N days
        result = db.execute(
            text("""
            SELECT 
                DATE(scan_timestamp) as date,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_scans
            FROM (
                SELECT user_id, scan_timestamp FROM location_scan_history
                UNION ALL
                SELECT user_id, scan_timestamp FROM price_scan_purchase
            ) combined_scans
            WHERE scan_timestamp > CURRENT_DATE - INTERVAL ':days days'
            GROUP BY DATE(scan_timestamp)
            ORDER BY date DESC
        """),
            {"days": days},
        )

        activity = []
        for row in result:
            activity.append(
                {
                    "date": row[0].isoformat(),
                    "active_users": row[1],
                    "total_scans": row[2],
                }
            )

        return {"daily_activity": activity}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/traveler-types")
async def get_traveler_types(db: Session = Depends(get_db)):
    """Get distribution of traveler types"""
    try:
        result = db.execute(text("""
            SELECT 
                COALESCE(traveler_type, 'Unknown') as traveler_type,
                COUNT(*) as count,
                AVG(
                    (SELECT COUNT(*) FROM location_scan_history lsh WHERE lsh.user_id = up.user_id) +
                    (SELECT COUNT(*) FROM price_scan_purchase psp WHERE psp.user_id = up.user_id)
                ) as avg_scans_per_user
            FROM user_profiles up
            GROUP BY traveler_type
            ORDER BY count DESC
        """))

        traveler_types = []
        for row in result:
            traveler_types.append(
                {
                    "type": row[0],
                    "count": row[1],
                    "avg_scans_per_user": float(row[2]) if row[2] else 0,
                }
            )

        return {"traveler_types": traveler_types}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of users with their activity summary"""
    try:
        result = db.execute(
            text("""
            SELECT * FROM user_analytics
            ORDER BY last_active DESC
            LIMIT :limit OFFSET :offset
        """),
            {"limit": limit, "offset": offset},
        )

        users = []
        columns = result.keys()
        for row in result:
            user_dict = dict(zip(columns, row))
            # Convert datetime objects to ISO strings
            for key, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
                elif isinstance(value, float) and value is not None:
                    user_dict[key] = round(value, 2)

            users.append(user_dict)

        # Get total count
        total_count = db.execute(text("SELECT COUNT(*) FROM user_profiles")).scalar()

        return {
            "users": users,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/details")
async def get_user_details(user_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific user"""
    try:
        # User profile
        user_result = db.execute(
            text("""
            SELECT * FROM user_analytics WHERE user_id = :user_id
        """),
            {"user_id": user_id},
        )

        user_data = user_result.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        columns = user_result.keys()
        user_dict = dict(zip(columns, user_data))

        # Convert datetime objects
        for key, value in user_dict.items():
            if isinstance(value, datetime):
                user_dict[key] = value.isoformat()
            elif isinstance(value, float) and value is not None:
                user_dict[key] = round(value, 2)

        # Recent location scans
        location_scans = db.execute(
            text("""
            SELECT monument_name, scan_timestamp, rating, time_spent_seconds, was_guided
            FROM location_scan_history 
            WHERE user_id = :user_id
            ORDER BY scan_timestamp DESC
            LIMIT 10
        """),
            {"user_id": user_id},
        ).fetchall()

        # Recent price scans
        price_scans = db.execute(
            text("""
            SELECT product_name, product_category, detected_price, owner_asking_price, 
                   price_fairness_rating, purchase_made, scan_timestamp, location
            FROM price_scan_purchase 
            WHERE user_id = :user_id
            ORDER BY scan_timestamp DESC
            LIMIT 10
        """),
            {"user_id": user_id},
        ).fetchall()

        # Sessions
        sessions = db.execute(
            text("""
            SELECT session_id, session_start, session_end, device_type, location_region
            FROM user_sessions 
            WHERE user_id = :user_id
            ORDER BY session_start DESC
            LIMIT 5
        """),
            {"user_id": user_id},
        ).fetchall()

        return {
            "user": user_dict,
            "recent_location_scans": [
                {
                    "monument_name": scan[0],
                    "scan_timestamp": scan[1].isoformat() if scan[1] else None,
                    "rating": scan[2],
                    "time_spent_minutes": round(scan[3] / 60, 1) if scan[3] else None,
                    "was_guided": scan[4],
                }
                for scan in location_scans
            ],
            "recent_price_scans": [
                {
                    "product_name": scan[0],
                    "product_category": scan[1],
                    "detected_price": scan[2],
                    "owner_asking_price": scan[3],
                    "price_fairness_rating": scan[4],
                    "purchase_made": scan[5],
                    "scan_timestamp": scan[6].isoformat() if scan[6] else None,
                    "location": scan[7],
                }
                for scan in price_scans
            ],
            "recent_sessions": [
                {
                    "session_id": str(session[0]),
                    "session_start": session[1].isoformat() if session[1] else None,
                    "session_end": session[2].isoformat() if session[2] else None,
                    "device_type": session[3],
                    "location_region": session[4],
                }
                for session in sessions
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user_data(user_id: str, db: Session = Depends(get_db)):
    """Delete all data for a specific user (GDPR compliance)"""
    try:
        # Delete in correct order due to foreign key constraints
        tables = [
            "location_scan_history",
            "price_scan_purchase",
            "hotel_stays",
            "user_journey_maps",
            "user_sessions",
            "user_profiles",
        ]

        total_deleted = 0
        for table in tables:
            result = db.execute(
                text(f"""
                DELETE FROM {table} WHERE user_id = :user_id
            """),
                {"user_id": user_id},
            )
            total_deleted += result.rowcount

        db.commit()

        return {
            "message": f"Successfully deleted all data for user {user_id}",
            "records_deleted": total_deleted,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/old-data")
async def cleanup_old_data(
    days_to_keep: int = Query(365, ge=30, le=1095), db: Session = Depends(get_db)
):
    """Clean up old tracking data"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old data
        deleted_sessions = db.execute(
            text("""
            DELETE FROM user_sessions 
            WHERE session_start < :cutoff_date
        """),
            {"cutoff_date": cutoff_date},
        ).rowcount

        deleted_location_scans = db.execute(
            text("""
            DELETE FROM location_scan_history 
            WHERE scan_timestamp < :cutoff_date
        """),
            {"cutoff_date": cutoff_date},
        ).rowcount

        deleted_price_scans = db.execute(
            text("""
            DELETE FROM price_scan_purchase 
            WHERE scan_timestamp < :cutoff_date
        """),
            {"cutoff_date": cutoff_date},
        ).rowcount

        db.commit()

        return {
            "message": f"Successfully cleaned up data older than {days_to_keep} days",
            "deleted_sessions": deleted_sessions,
            "deleted_location_scans": deleted_location_scans,
            "deleted_price_scans": deleted_price_scans,
            "total_deleted": deleted_sessions
            + deleted_location_scans
            + deleted_price_scans,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
