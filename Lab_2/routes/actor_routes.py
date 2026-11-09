
from flask import Blueprint, request, jsonify
from database import get_connection
from datetime import datetime
import mysql.connector

actor_bp = Blueprint("actor", __name__)


# GET: Lấy danh sách diễn viên
@actor_bp.route("/actors", methods=["GET"])
def get_actors():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT ActorID, FullName, DateOfBirth, Nationality
            FROM ACTOR
            ORDER BY ActorID
        """)

        actors = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": actors
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# GET: Lấy thông tin một diễn viên
@actor_bp.route("/actors/<int:actor_id>", methods=["GET"])
def get_actor(actor_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT ActorID, FullName, DateOfBirth, Nationality
            FROM ACTOR
            WHERE ActorID = %s
        """, (actor_id,))

        actor = cursor.fetchone()

        if actor is None:
            return jsonify({
                "status": "error",
                "message": "Actor not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": actor
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Validate dữ liệu Actor
def validate_actor(data):
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


# POST: Thêm diễn viên
@actor_bp.route("/actors", methods=["POST"])
def create_actor():
    data = request.get_json(silent=True)
    error = validate_actor(data)

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
            INSERT INTO ACTOR (FullName, DateOfBirth, Nationality)
            VALUES (%s, %s, %s)
        """, (
            data["FullName"].strip(),
            data.get("DateOfBirth"),
            data.get("Nationality")
        ))

        actor_id = cursor.lastrowid
        connection.commit()

        cursor.execute("""
            SELECT ActorID, FullName, DateOfBirth, Nationality
            FROM ACTOR
            WHERE ActorID = %s
        """, (actor_id,))

        actor = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Actor created successfully",
            "data": actor
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


# PUT: Cập nhật diễn viên
@actor_bp.route("/actors/<int:actor_id>", methods=["PUT"])
def update_actor(actor_id):
    data = request.get_json(silent=True)
    error = validate_actor(data)

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
            SELECT ActorID FROM ACTOR WHERE ActorID = %s
        """, (actor_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "status": "error",
                "message": "Actor not found"
            }), 404

        cursor.execute("""
            UPDATE ACTOR
            SET FullName = %s,
                DateOfBirth = %s,
                Nationality = %s
            WHERE ActorID = %s
        """, (
            data["FullName"].strip(),
            data.get("DateOfBirth"),
            data.get("Nationality"),
            actor_id
        ))

        connection.commit()

        cursor.execute("""
            SELECT ActorID, FullName, DateOfBirth, Nationality
            FROM ACTOR
            WHERE ActorID = %s
        """, (actor_id,))

        actor = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Actor updated successfully",
            "data": actor
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


# DELETE: Xóa diễn viên
@actor_bp.route("/actors/<int:actor_id>", methods=["DELETE"])
def delete_actor(actor_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM ACTOR
            WHERE ActorID = %s
        """, (actor_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Actor not found"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Actor deleted successfully"
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
