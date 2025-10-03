#!/usr/bin/env python3
"""
Script to create an admin user
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.lms.models.user import LMSUser
from app.core.security import get_password_hash
from app.core.config import settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(LMSUser).filter(LMSUser.email == "admin@example.com").first()

        if not admin:
            # Create new admin
            admin = LMSUser(
                email="admin@example.com",
                name="Admin User",
                hashed_password=get_password_hash("admin123"),
                role="ADMIN",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print("✅ Created admin user:")
            print("   Email: admin@example.com")
            print("   Password: admin123")
        else:
            # Update existing user to admin
            admin.role = "ADMIN"
            db.commit()
            print(f"✅ Updated user {admin.email} to ADMIN role")

        # Show all users
        print("\n📋 All users in system:")
        users = db.query(LMSUser).all()
        for user in users:
            print(f"   {user.email}: {user.role}")

    finally:
        db.close()

if __name__ == "__main__":
    create_admin()