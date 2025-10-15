from flask import Flask, jsonify
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"]}})

    @app.get("/api/hello")
    def hello_world() -> tuple[dict[str, str], int]:
        return jsonify(message="Hello from Flask"), 200

    @app.get("/api/health")
    def healthcheck() -> tuple[dict[str, str], int]:
        return jsonify(status="ok"), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
