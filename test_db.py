import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Testing connection to database...")

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f"Connected successfully! PostgreSQL version: {record[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")