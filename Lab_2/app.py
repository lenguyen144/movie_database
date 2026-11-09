from flask import Flask, jsonify, render_template

from routes.movie_routes import movie_bp
from routes.actor_routes import actor_bp
from routes.director_routes import director_bp
from routes.genre_routes import genre_bp
from routes.producer_routes import producer_bp
from routes.quote_routes import quote_bp

app = Flask(__name__)

# Đăng ký các API Blueprint
app.register_blueprint(movie_bp)
app.register_blueprint(actor_bp)
app.register_blueprint(director_bp)
app.register_blueprint(genre_bp)
app.register_blueprint(producer_bp)
app.register_blueprint(quote_bp)


# Trang giao diện chính
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

