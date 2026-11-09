
from flask import Blueprint, request, jsonify
from database import get_connection
import mysql.connector

producer_bp = Blueprint("producer", __name__)


# Validate dữ liệu Producer
def validate_producer(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    company_name = data.get("CompanyName")

    if not isinstance(company_name, str) or not company_name.strip():
        return "CompanyName is required and must be a non-empty string"

    if len(company_name.strip()) > 150:
        return "CompanyName must not exceed 150 characters"

    country = data.get("Country")

    if country is not None:
        if not isinstance(country, str):
            return "Country must be a string or null"

        if len(country) > 50:
            return "Country must not exceed 50 characters"

    return None


# GET: Lấy danh sách nhà sản xuất
@producer_bp.route("/producers", methods=["GET"])
def get_producers():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT ProducerID, CompanyName, Country
            FROM PRODUCER
            ORDER BY ProducerID
        """)

        producers = cursor.fetchall()

        return jsonify({
            "status": "success",
            "data": producers
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# GET: Lấy thông tin một nhà sản xuất
@producer_bp.route("/producers/<int:producer_id>", methods=["GET"])
def get_producer(producer_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT ProducerID, CompanyName, Country
            FROM PRODUCER
            WHERE ProducerID = %s
        """, (producer_id,))

        producer = cursor.fetchone()

        if producer is None:
            return jsonify({
                "status": "error",
                "message": "Producer not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": producer
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# POST: Thêm nhà sản xuất
@producer_bp.route("/producers", methods=["POST"])
def create_producer():
    data = request.get_json(silent=True)
    error = validate_producer(data)

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
            INSERT INTO PRODUCER (CompanyName, Country)
            VALUES (%s, %s)
        """, (
            data["CompanyName"].strip(),
            data.get("Country")
        ))

        producer_id = cursor.lastrowid
        connection.commit()

        cursor.execute("""
            SELECT ProducerID, CompanyName, Country
            FROM PRODUCER
            WHERE ProducerID = %s
        """, (producer_id,))

        producer = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Producer created successfully",
            "data": producer
        }), 201

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "CompanyName already exists"
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


# PUT: Cập nhật nhà sản xuất
@producer_bp.route("/producers/<int:producer_id>", methods=["PUT"])
def update_producer(producer_id):
    data = request.get_json(silent=True)
    error = validate_producer(data)

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
            SELECT ProducerID
            FROM PRODUCER
            WHERE ProducerID = %s
        """, (producer_id,))

        if cursor.fetchone() is None:
            return jsonify({
                "status": "error",
                "message": "Producer not found"
            }), 404

        cursor.execute("""
            UPDATE PRODUCER
            SET CompanyName = %s,
                Country = %s
            WHERE ProducerID = %s
        """, (
            data["CompanyName"].strip(),
            data.get("Country"),
            producer_id
        ))

        connection.commit()

        cursor.execute("""
            SELECT ProducerID, CompanyName, Country
            FROM PRODUCER
            WHERE ProducerID = %s
        """, (producer_id,))

        producer = cursor.fetchone()

        return jsonify({
            "status": "success",
            "message": "Producer updated successfully",
            "data": producer
        }), 200

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "CompanyName already exists"
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


# DELETE: Xóa nhà sản xuất
@producer_bp.route("/producers/<int:producer_id>", methods=["DELETE"])
def delete_producer(producer_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM PRODUCER
            WHERE ProducerID = %s
        """, (producer_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Producer not found"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Producer deleted successfully"
        }), 200

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Cannot delete producer because it is being used by a movie"
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
