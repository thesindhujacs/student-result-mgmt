from flask import Blueprint, request, jsonify, session
from config.db import get_db

subjects_bp = Blueprint("subjects", __name__)

def require_admin():
    if session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None

# GET all subjects
@subjects_bp.route("/", methods=["GET"])
def get_all_subjects():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects ORDER BY semester, code")
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(subjects), 200

# POST add subject (admin only)
@subjects_bp.route("/", methods=["POST"])
def add_subject():
    err = require_admin()
    if err: return err

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO subjects (code, name, semester, max_marks) VALUES (%s, %s, %s, %s)",
            (data["code"], data["name"], data["semester"], data.get("max_marks", 100))
        )
        conn.commit()
        return jsonify({"message": "Subject added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# DELETE subject (admin only)
@subjects_bp.route("/<int:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Subject deleted"}), 200
