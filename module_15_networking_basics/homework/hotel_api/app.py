from flask import Flask

from models import init_db
from routes import register_routes


def create_app() -> Flask:
    """Создаёт и настраивает Flask-приложение."""
    app = Flask(__name__)
    register_routes(app)
    return app


if __name__ == '__main__':
    init_db()
    app = create_app()
    app.run(debug=True, port=5000)