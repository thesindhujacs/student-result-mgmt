from flask import Blueprint, request, jsonify, session
from config.db import get_db

results_bp = Blueprint("results", __name__)

def calculate_grade(marks):
    if marks >= 90: return "O"
    elif marks >= 80: return "A+"
    elif marks >= 70: return "A"
    elif marks >= 60: return "B+"
    elif marks >= 50: return "B"
    elif marks >= 40: return "C"
    else: return "F"

def require_admin():
    if session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None

# GET results for a student by USN
@results_bp.route("/<usn>", methods=["GET"])
def get_results(usn):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, s.usn, s.name, sub.code, sub.name AS subject,
               r.marks_obtained, r.grade, r.academic_year
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN subjects sub ON r.subject_id = sub.id
        WHERE s.usn = %s
    """, (usn,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results), 200

# GET all results (admin only)
@results_bp.route("/", methods=["GET"])
def get_all_results():
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, s.usn, s.name, sub.code, sub.name AS subject,
               r.marks_obtained, r.grade, r.academic_year
        FROM results r
        JOIN students s ON r.student_id = s.id
        JOIN subjects sub ON r.subject_id = sub.id
        ORDER BY s.usn
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results), 200

# POST add result (admin only)
@results_bp.route("/", methods=["POST"])
def add_result():
    err = require_admin()
    if err: return err

    data = request.get_json()
    marks = int(data["marks_obtained"])
    grade = calculate_grade(marks)

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Resolve USN to student_id
    cursor.execute("SELECT id FROM students WHERE usn = %s", (data["usn"],))
    student = cursor.fetchone()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    # Resolve subject code to subject_id
    cursor.execute("SELECT id FROM subjects WHERE code = %s", (data["subject_code"],))
    subject = cursor.fetchone()
    if not subject:
        return jsonify({"error": "Subject not found"}), 404

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO results (student_id, subject_id, marks_obtained, grade, academic_year) VALUES (%s, %s, %s, %s, %s)",
            (student["id"], subject["id"], marks, grade, data.get("academic_year", "2025-26"))
        )
        conn.commit()
        return jsonify({"message": "Result added", "grade": grade}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# PUT update result (admin only)
@results_bp.route("/<int:result_id>", methods=["PUT"])
def update_result(result_id):
    err = require_admin()
    if err: return err

    data = request.get_json()
    marks = int(data["marks_obtained"])
    grade = calculate_grade(marks)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE results SET marks_obtained=%s, grade=%s WHERE id=%s",
            (marks, grade, result_id)
        )
        conn.commit()
        return jsonify({"message": "Result updated", "grade": grade}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# DELETE result (admin only)
@results_bp.route("/<int:result_id>", methods=["DELETE"])
def delete_result(result_id):
    err = require_admin()
    if err: return err

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = %s", (result_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Result deleted"}), 200
