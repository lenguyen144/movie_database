
from flask import Blueprint, request, jsonify
from database import get_connection
import mysql.connector

quote_bp = Blueprint("quote", __name__)


# Kiểm tra dữ liệu đầu vào
def validate_quote(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    movie_id = data.get("MovieID")
    actor_id = data.get("ActorID")
    quote_text = data.get("QuoteText")

    if (
        not isinstance(movie_id, int)
        or isinstance(movie_id, bool)
        or movie_id <= 0
    ):
        return "MovieID must be a positive integer."

    if (
        not isinstance(actor_id, int)
        or isinstance(actor_id, bool)
        or actor_id <= 0
    ):
        return "ActorID must be a positive integer."

    if not isinstance(quote_text, str) or not quote_text.strip():
        return "QuoteText must be a non-empty string."

    return None


# GET: Lấy danh sách tất cả câu thoại
@quote_bp.route("/quotes", methods=["GET"])
def get_quotes():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT QuoteID, MovieID, ActorID, QuoteText
            FROM MOVIE_QUOTE
            ORDER BY QuoteID
        """)

        quotes = cursor.fetchall()
        return jsonify(quotes), 200

    finally:
        cursor.close()
        connection.close()


# GET: Lấy câu thoại theo QuoteID
@quote_bp.route("/quotes/<int:quote_id>", methods=["GET"])
def get_quote(quote_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT QuoteID, MovieID, ActorID, QuoteText
            FROM MOVIE_QUOTE
            WHERE QuoteID = %s
        """, (quote_id,))

        quote = cursor.fetchone()

        if quote is None:
            return jsonify({"error": "Quote not found"}), 404

        return jsonify(quote), 200

    finally:
        cursor.close()
        connection.close()


# POST: Thêm câu thoại mới
@quote_bp.route("/quotes", methods=["POST"])
def create_quote():
    data = request.get_json(silent=True)
    error = validate_quote(data)

    if error:
        return jsonify({"error": error}), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO MOVIE_QUOTE (MovieID, ActorID, QuoteText)
            VALUES (%s, %s, %s)
        """, (
            data["MovieID"],
            data["ActorID"],
            data["QuoteText"].strip()
        ))

        connection.commit()

        return jsonify({
            "message": "Quote created successfully",
            "QuoteID": cursor.lastrowid
        }), 201

    except mysql.connector.IntegrityError:
        connection.rollback()
        return jsonify({
            "error": "MovieID and ActorID must reference an existing movie-actor relationship."
        }), 409

    except Exception:
        connection.rollback()
        return jsonify({"error": "Failed to create quote"}), 500

    finally:
        cursor.close()
        connection.close()


# PUT: Cập nhật câu thoại
@quote_bp.route("/quotes/<int:quote_id>", methods=["PUT"])
def update_quote(quote_id):
    data = request.get_json(silent=True)
    error = validate_quote(data)

    if error:
        return jsonify({"error": error}), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT QuoteID
            FROM MOVIE_QUOTE
            WHERE QuoteID = %s
        """, (quote_id,))

        if cursor.fetchone() is None:
            return jsonify({"error": "Quote not found"}), 404

        cursor.execute("""
            UPDATE MOVIE_QUOTE
            SET MovieID = %s,
                ActorID = %s,
                QuoteText = %s
            WHERE QuoteID = %s
        """, (
            data["MovieID"],
            data["ActorID"],
            data["QuoteText"].strip(),
            quote_id
        ))

        connection.commit()

        return jsonify({
            "message": "Quote updated successfully"
        }), 200

    except mysql.connector.IntegrityError:
        connection.rollback()
        return jsonify({
            "error": "MovieID and ActorID must reference an existing movie-actor relationship."
        }), 409

    except Exception:
        connection.rollback()
        return jsonify({"error": "Failed to update quote"}), 500

    finally:
        cursor.close()
        connection.close()


# DELETE: Xóa câu thoại
@quote_bp.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM MOVIE_QUOTE
            WHERE QuoteID = %s
        """, (quote_id,))

        if cursor.rowcount == 0:
            return jsonify({"error": "Quote not found"}), 404

        connection.commit()

        return jsonify({
            "message": "Quote deleted successfully"
        }), 200

    except Exception:
        connection.rollback()
        return jsonify({"error": "Failed to delete quote"}), 500

    finally:
        cursor.close()
        connection.close()
