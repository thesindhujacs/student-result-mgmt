from flask import Blueprint, request, jsonify, session
from config.db import get_db

students_bp = Blueprint("students", __name__)

def require_admin():
    if session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None

# GET all students (admin only)
@students_bp.route("/", methods=["GET"])
def get_all_students():
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students), 200

# GET single student by USN
@students_bp.route("/<usn>", methods=["GET"])
def get_student(usn):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE usn = %s", (usn,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

# POST add new student (admin only)
@students_bp.route("/", methods=["POST"])
def add_student():
    err = require_admin()
    if err: return err

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (usn, name, email, branch, semester) VALUES (%s, %s, %s, %s, %s)",
            (data["usn"], data["name"], data.get("email"), data.get("branch"), data.get("semester"))
        )
        conn.commit()
        return jsonify({"message": "Student added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# PUT update student (admin only)
@students_bp.route("/<usn>", methods=["PUT"])
def update_student(usn):
    err = require_admin()
    if err: return err

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE students SET name=%s, email=%s, branch=%s, semester=%s WHERE usn=%s",
            (data.get("name"), data.get("email"), data.get("branch"), data.get("semester"), usn)
        )
        conn.commit()
        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# DELETE student (admin only)
@students_bp.route("/<usn>", methods=["DELETE"])
def delete_student(usn):
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE usn = %s", (usn,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Student deleted successfully"}), 200
