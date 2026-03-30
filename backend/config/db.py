import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "student_results")
    )

def init_db():
    # Schema is handled by Docker via docker-entrypoint-initdb.d
    # For local runs without Docker, create DB if not exists
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "")
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_results")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"DB init skipped: {e}")