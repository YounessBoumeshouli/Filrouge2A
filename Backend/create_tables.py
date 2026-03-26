#!/usr/bin/env python3
"""
Create Database Tables
This script creates all the required tables for the Tourist Helper application
"""

import sys
sys.path.append('/app')

from app.database import engine, Base

def create_tables():
    """Create all database tables"""
    try:
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_tables()