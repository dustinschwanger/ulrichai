#!/usr/bin/env python3
"""Clean up existing types and run migration"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import subprocess

load_dotenv()

def clean_database():
    """Clean up existing enum types"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Drop existing enum types if they exist
        conn.execute(text("DROP TYPE IF EXISTS questiontype CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS quizstatus CASCADE"))
        conn.commit()
        print("✓ Cleaned up existing enum types")

def run_migration():
    """Run the Alembic migration"""
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Migration completed successfully")
    else:
        print(f"✗ Migration failed:\n{result.stderr}")
        return False
    return True

if __name__ == "__main__":
    try:
        clean_database()
        if run_migration():
            print("\n✓ Database is ready with quiz tables!")
        else:
            print("\n✗ Migration failed. Please check the error above.")
    except Exception as e:
        print(f"Error: {e}")