from flask import Blueprint, request, jsonify
from database import get_connection
import mysql.connector

genre_bp = Blueprint("genre", __name__)


# Validate dữ liệu Genre
def validate_genre(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    genre_name = data.get("GenreName")

    if not isinstance(genre_name, str) or not genre_name.strip():
        return "GenreName is required and must be a non-empty string"

    if len(genre_name.strip()) > 50:
        return "GenreName must not exceed 50 characters"

    return None


# GET: Lấy danh sách thể loại
@genre_bp.route("/genres", methods=["GET"])
def get_genres():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT GenreID, GenreName
            FROM GENRE
            ORDER BY GenreID
        """)

        genres = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": genres
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# GET: Lấy thông tin một thể loại
@genre_bp.route("/genres/<int:genre_id>", methods=["GET"])
def get_genre(genre_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT GenreID, GenreName
            FROM GENRE
            WHERE GenreID = %s
        """, (genre_id,))

        genre = cursor.fetchone()

        if genre is None:
            return jsonify({
                "status": "error",
                "message": "Genre not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": genre
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# POST: Thêm thể loại
@genre_bp.route("/genres", methods=["POST"])
def create_genre():
    data = request.get_json(silent=True)
    error = validate_genre(data)

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
            INSERT INTO GENRE (GenreName)
            VALUES (%s)
        """, (data["GenreName"].strip(),))

        genre_id = cursor.lastrowid
        connection.commit()

        cursor.execute("""
            SELECT GenreID, GenreName
            FROM GENRE
            WHERE GenreID = %s
        """, (genre_id,))

        genre = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Genre created successfully",
            "data": genre
        }), 201

    except mysql.connector.IntegrityError as e:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "GenreName already exists"
        }), 409

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


# PUT: Cập nhật thể loại
@genre_bp.route("/genres/<int:genre_id>", methods=["PUT"])
def update_genre(genre_id):
    data = request.get_json(silent=True)
    error = validate_genre(data)

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
            SELECT GenreID
            FROM GENRE
            WHERE GenreID = %s
        """, (genre_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "status": "error",
                "message": "Genre not found"
            }), 404

        cursor.execute("""
            UPDATE GENRE
            SET GenreName = %s
            WHERE GenreID = %s
        """, (data["GenreName"].strip(), genre_id))

        connection.commit()

        cursor.execute("""
            SELECT GenreID, GenreName
            FROM GENRE
            WHERE GenreID = %s
        """, (genre_id,))

        genre = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Genre updated successfully",
            "data": genre
        }), 200

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "GenreName already exists"
        }), 409

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


# DELETE: Xóa thể loại
@genre_bp.route("/genres/<int:genre_id>", methods=["DELETE"])
def delete_genre(genre_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM GENRE
            WHERE GenreID = %s
        """, (genre_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Genre not found"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Genre deleted successfully"
        }), 200

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Cannot delete genre because it is being used by a movie"
        }), 409

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
