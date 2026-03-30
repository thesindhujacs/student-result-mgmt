from flask import Blueprint, request, jsonify, session
from config.db import get_db
import hashlib

auth_bp = Blueprint("auth", __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Try admin login first (hashed password)
    hashed = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed))
    user = cursor.fetchone()

    if user:
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        session["username"] = username
        cursor.close()
        conn.close()
        return jsonify({"message": "Login successful", "role": user["role"], "username": username}), 200

    # Try student login — USN as username, DOB as password (DD-MM-YYYY)
    cursor.execute("SELECT * FROM students WHERE usn = %s AND dob = %s", (username.upper(), password))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        session["user_id"] = student["id"]
        session["role"] = "student"
        session["usn"] = student["usn"]
        return jsonify({
            "message": "Login successful",
            "role": "student",
            "username": student["name"],
            "usn": student["usn"]
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = hash_password(data.get("password", ""))
    role = data.get("role", "student")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()
