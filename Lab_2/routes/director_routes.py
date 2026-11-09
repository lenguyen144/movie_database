from flask import Blueprint, request, jsonify
from database import get_connection
from datetime import datetime
import mysql.connector

director_bp = Blueprint("director", __name__)


# GET: Lấy danh sách đạo diễn
@director_bp.route("/directors", methods=["GET"])
def get_directors():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT DirectorID, FullName, DateOfBirth, Nationality
            FROM DIRECTOR
            ORDER BY DirectorID
        """)

        directors = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": directors
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# GET: Lấy thông tin một đạo diễn
@director_bp.route("/directors/<int:director_id>", methods=["GET"])
def get_director(director_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT DirectorID, FullName, DateOfBirth, Nationality
            FROM DIRECTOR
            WHERE DirectorID = %s
        """, (director_id,))

        director = cursor.fetchone()

        if director is None:
            return jsonify({
                "status": "error",
                "message": "Director not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": director
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Validate dữ liệu Director
def validate_director(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    full_name = data.get("FullName")

    if not isinstance(full_name, str) or not full_name.strip():
        return "FullName is required and must be a non-empty string"

    if len(full_name.strip()) > 100:
        return "FullName must not exceed 100 characters"

    date_of_birth = data.get("DateOfBirth")

    if date_of_birth is not None:
        if not isinstance(date_of_birth, str):
            return "DateOfBirth must be a string in YYYY-MM-DD format"

        try:
            datetime.strptime(date_of_birth, "%Y-%m-%d")
        except ValueError:
            return "DateOfBirth must be a valid date in YYYY-MM-DD format"

    nationality = data.get("Nationality")

    if nationality is not None:
        if not isinstance(nationality, str):
            return "Nationality must be a string or null"

        if len(nationality) > 50:
            return "Nationality must not exceed 50 characters"

    return None


# POST: Thêm đạo diễn
@director_bp.route("/directors", methods=["POST"])
def create_director():
    data = request.get_json(silent=True)
    error = validate_director(data)

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO DIRECTOR (FullName, DateOfBirth, Nationality)
            VALUES (%s, %s, %s)
        """, (
            data["FullName"].strip(),
            data.get("DateOfBirth"),
            data.get("Nationality")
        ))

        director_id = cursor.lastrowid
        connection.commit()

        cursor.execute("""
            SELECT DirectorID, FullName, DateOfBirth, Nationality
            FROM DIRECTOR
            WHERE DirectorID = %s
        """, (director_id,))

        director = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Director created successfully",
            "data": director
        }), 201

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        if connection:
            connection.rollback()

        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# PUT: Cập nhật đạo diễn
@director_bp.route("/directors/<int:director_id>", methods=["PUT"])
def update_director(director_id):
    data = request.get_json(silent=True)
    error = validate_director(data)

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT DirectorID
            FROM DIRECTOR
            WHERE DirectorID = %s
        """, (director_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "status": "error",
                "message": "Director not found"
            }), 404

        cursor.execute("""
            UPDATE DIRECTOR
            SET FullName = %s,
                DateOfBirth = %s,
                Nationality = %s
            WHERE DirectorID = %s
        """, (
            data["FullName"].strip(),
            data.get("DateOfBirth"),
            data.get("Nationality"),
            director_id
        ))

        connection.commit()

        cursor.execute("""
            SELECT DirectorID, FullName, DateOfBirth, Nationality
            FROM DIRECTOR
            WHERE DirectorID = %s
        """, (director_id,))

        director = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Director updated successfully",
            "data": director
        }), 200

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        if connection:
            connection.rollback()

        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# DELETE: Xóa đạo diễn
@director_bp.route("/directors/<int:director_id>", methods=["DELETE"])
def delete_director(director_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM DIRECTOR
            WHERE DirectorID = %s
        """, (director_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Director not found"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Director deleted successfully"
        }), 200

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        if connection:
            connection.rollback()

        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
