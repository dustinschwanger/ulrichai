#!/usr/bin/env python3
"""Test script to verify LMS tables were created"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
# from tabulate import tabulate  # Not needed

# Load environment variables
load_dotenv()

def test_lms_tables():
    """Test that LMS tables were created successfully"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False

    # Fix for SQLAlchemy compatibility
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")

    try:
        engine = create_engine(database_url)

        # Query to get all LMS tables
        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'lms_%'
            ORDER BY table_name;
        """)

        with engine.connect() as conn:
            result = conn.execute(query)
            tables = result.fetchall()

            if tables:
                print("✅ LMS tables created successfully!\n")
                print("Found the following LMS tables:")
                print("-" * 40)
                for table in tables:
                    print(f"  • {table[0]}")
                print("-" * 40)
                print(f"Total: {len(tables)} tables")

                # Test a sample insert
                print("\n📝 Testing data insertion...")

                # Create a test organization
                org_insert = text("""
                    INSERT INTO lms_organizations (name, slug)
                    VALUES ('Test Organization', 'test-org')
                    ON CONFLICT (slug) DO NOTHING
                    RETURNING id, name;
                """)

                result = conn.execute(org_insert)
                org = result.fetchone()

                if org:
                    print(f"✅ Successfully created test organization: {org[1]}")
                else:
                    print("ℹ️  Test organization already exists")

                conn.commit()

                return True
            else:
                print("❌ No LMS tables found")
                return False

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False


if __name__ == "__main__":
    success = test_lms_tables()
    sys.exit(0 if success else 1)