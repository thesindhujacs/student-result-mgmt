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
    # Connect without database first to create it
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS student_results")
    cursor.execute("USE student_results")
    schema_path = os.path.join(os.path.dirname(__file__), "../../database/schema.sql")
    with open(schema_path, "r") as f:
        for statement in f.read().split(";"):
            if statement.strip():
                cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()