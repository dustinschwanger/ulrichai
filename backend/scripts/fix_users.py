#!/usr/bin/env python3
"""
Script to fix/create users for authentication
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import sys

# Add the app module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.lms.models.user import LMSUser
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

# Create database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ulrichai_user:ulrichai_pass@localhost/ulrichai_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_users():
    db = SessionLocal()
    try:
        # Check existing users
        print("\n📋 Current users in database:")
        users = db.query(LMSUser).all()
        for user in users:
            print(f"   {user.email}: role={user.role}, name={user.first_name} {user.last_name}")
        
        # Create or update instructor user
        instructor = db.query(LMSUser).filter(LMSUser.email == "instructor@example.com").first()
        
        if not instructor:
            print("\n✨ Creating instructor user...")
            instructor = LMSUser(
                email="instructor@example.com",
                first_name="John",
                last_name="Instructor",
                password_hash=pwd_context.hash("password123"),
                role="INSTRUCTOR",
                is_active=True,
                email_verified=True,
                organization_id="default-org"
            )
            db.add(instructor)
            db.commit()
            print("✅ Created instructor user")
        else:
            print(f"\n🔄 Updating existing instructor user (current role: {instructor.role})")
            instructor.password_hash = pwd_context.hash("password123")
            instructor.role = "INSTRUCTOR"
            instructor.is_active = True
            instructor.email_verified = True
            if not instructor.first_name:
                instructor.first_name = "John"
            if not instructor.last_name:
                instructor.last_name = "Instructor"
            if not instructor.organization_id:
                instructor.organization_id = "default-org"
            db.commit()
            print("✅ Updated instructor user")
        
        # Create or update admin user
        admin = db.query(LMSUser).filter(LMSUser.email == "admin@example.com").first()
        
        if not admin:
            print("\n✨ Creating admin user...")
            admin = LMSUser(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=pwd_context.hash("admin123"),
                role="ADMIN",
                is_active=True,
                email_verified=True,
                organization_id="default-org"
            )
            db.add(admin)
            db.commit()
            print("✅ Created admin user")
        else:
            print(f"\n🔄 Updating existing admin user (current role: {admin.role})")
            admin.password_hash = pwd_context.hash("admin123")
            admin.role = "ADMIN"
            admin.is_active = True
            admin.email_verified = True
            if not admin.first_name:
                admin.first_name = "Admin"
            if not admin.last_name:
                admin.last_name = "User"
            if not admin.organization_id:
                admin.organization_id = "default-org"
            db.commit()
            print("✅ Updated admin user")
        
        print("\n🔐 Login credentials:")
        print("   Instructor: instructor@example.com / password123")
        print("   Admin: admin@example.com / admin123")
        
        print("\n📋 Final user list:")
        users = db.query(LMSUser).all()
        for user in users:
            print(f"   {user.email}: role={user.role}, active={user.is_active}, verified={user.email_verified}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_users()