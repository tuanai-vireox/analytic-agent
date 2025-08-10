#!/usr/bin/env python3
"""
Database initialization script.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import init_db, engine
from app.models import analysis_task, user
from app.services.user_service import UserService
from app.schemas.user import UserCreate


async def create_superuser():
    """Create a superuser account."""
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        user_service = UserService()
        
        # Check if superuser already exists
        existing_user = await user_service.get_user_by_email(db, "admin@analytic-agent.com")
        if existing_user:
            print("Superuser already exists")
            return
        
        # Create superuser
        superuser_data = UserCreate(
            email="admin@analytic-agent.com",
            username="admin",
            full_name="System Administrator",
            password="admin123"  # Change this in production
        )
        
        user = await user_service.create_user(db, superuser_data)
        
        # Make user a superuser
        user.is_superuser = True
        db.commit()
        
        print("Superuser created successfully")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
    finally:
        db.close()


def main():
    """Main function."""
    print("Initializing database...")
    
    try:
        # Initialize database tables
        init_db()
        print("Database tables created successfully")
        
        # Create superuser
        asyncio.run(create_superuser())
        
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 