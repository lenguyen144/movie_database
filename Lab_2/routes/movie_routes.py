from flask import Blueprint, request, jsonify
from database import get_connection
import mysql.connector

movie_bp = Blueprint("movie", __name__)


# GET /movies
# Lấy danh sách phim
@movie_bp.route("/movies", methods=["GET"])
def get_movies():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                m.MovieID,
                m.Title,
                m.Duration,
                m.Plot,
                m.ReleaseYear,
                m.ProducerID,
                p.CompanyName
            FROM MOVIE m
            JOIN PRODUCER p ON m.ProducerID = p.ProducerID
            ORDER BY m.MovieID
        """

        cursor.execute(sql)
        movies = cursor.fetchall()

        return jsonify({
            "status": "success",
            "total": len(movies),
            "data": movies
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "status": "error",
            "message": "Cannot retrieve movies"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# GET /movies/<id>
# Lấy thông tin chi tiết một phim
@movie_bp.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        sql = """
            SELECT
                m.MovieID,
                m.Title,
                m.Duration,
                m.Plot,
                m.ReleaseYear,
                m.ProducerID,
                p.CompanyName
            FROM MOVIE m
            JOIN PRODUCER p ON m.ProducerID = p.ProducerID
            WHERE m.MovieID = %s
        """

        cursor.execute(sql, (movie_id,))
        movie = cursor.fetchone()

        if not movie:
            return jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 404

        return jsonify({
            "status": "success",
            "data": movie
        }), 200

    except mysql.connector.Error:
        return jsonify({
            "status": "error",
            "message": "Cannot retrieve movie"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# POST /movies
# Thêm phim mới
@movie_bp.route("/movies", methods=["POST"])
def create_movie():
    connection = None
    cursor = None

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Request body must be a JSON object"
            }), 400

        title = data.get("Title")
        duration = data.get("Duration")
        producer_id = data.get("ProducerID")
        plot = data.get("Plot")
        release_year = data.get("ReleaseYear")

        if not title or not isinstance(title, str):
            return jsonify({
                "status": "error",
                "message": "Title is required"
            }), 400

        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            return jsonify({
                "status": "error",
                "message": "Duration must be a positive integer"
            }), 400

        if not isinstance(producer_id, int) or isinstance(producer_id, bool):
            return jsonify({
                "status": "error",
                "message": "ProducerID must be an integer"
            }), 400

        if release_year is not None and (
            not isinstance(release_year, int)
            or isinstance(release_year, bool)
            or release_year <= 0
        ):
            return jsonify({
                "status": "error",
                "message": "ReleaseYear must be a positive integer or null"
            }), 400

        connection = get_connection()
        cursor = connection.cursor()

        sql = """
            INSERT INTO MOVIE
                (Title, Duration, Plot, ReleaseYear, ProducerID)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (title, duration, plot, release_year, producer_id)

        cursor.execute(sql, values)
        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Movie created successfully",
            "MovieID": cursor.lastrowid
        }), 201

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Cannot create movie. Check ProducerID and database constraints."
        }), 400

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# PUT /movies/<id>
# Cập nhật thông tin phim
@movie_bp.route("/movies/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    connection = None
    cursor = None

    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Request body must be a JSON object"
            }), 400

        required_fields = ["Title", "Duration", "ProducerID"]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"{field} is required"
                }), 400

        title = data["Title"]
        duration = data["Duration"]
        producer_id = data["ProducerID"]
        plot = data.get("Plot")
        release_year = data.get("ReleaseYear")

        if not isinstance(title, str) or not title.strip():
            return jsonify({
                "status": "error",
                "message": "Title must be a non-empty string"
            }), 400

        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            return jsonify({
                "status": "error",
                "message": "Duration must be a positive integer"
            }), 400

        if not isinstance(producer_id, int) or isinstance(producer_id, bool):
            return jsonify({
                "status": "error",
                "message": "ProducerID must be an integer"
            }), 400

        if release_year is not None and (
            not isinstance(release_year, int)
            or isinstance(release_year, bool)
            or release_year <= 0
        ):
            return jsonify({
                "status": "error",
                "message": "ReleaseYear must be a positive integer or null"
            }), 400

        connection = get_connection()
        cursor = connection.cursor()

        # Kiểm tra phim có tồn tại không
        cursor.execute(
            "SELECT MovieID FROM MOVIE WHERE MovieID = %s",
            (movie_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 404

        sql = """
            UPDATE MOVIE
            SET Title = %s,
                Duration = %s,
                Plot = %s,
                ReleaseYear = %s,
                ProducerID = %s
            WHERE MovieID = %s
        """

        values = (
            title,
            duration,
            plot,
            release_year,
            producer_id,
            movie_id
        )

        cursor.execute(sql, values)
        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Movie updated successfully"
        }), 200

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Cannot update movie. Check ProducerID and database constraints."
        }), 400

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# DELETE /movies/<id>
# Xóa phim
@movie_bp.route("/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM MOVIE WHERE MovieID = %s",
            (movie_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Movie deleted successfully"
        }), 200

    except mysql.connector.Error:
        if connection:
            connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Cannot delete movie"
        }), 400

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()