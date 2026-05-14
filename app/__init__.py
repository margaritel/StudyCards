from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
import os

# Явно указываем путь к .env
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    CORS(app)

    # Настройки из .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///studyshare.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'studyshare-fallback-secret-key-2025')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

    db.init_app(app)
    jwt.init_app(app)

    # Подключаем роуты
    from app.routes.auth_routes import auth_bp
    from app.routes.sets_routes import sets_bp
    from app.routes.cards_routes import cards_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(sets_bp, url_prefix='/api/sets')
    app.register_blueprint(cards_bp, url_prefix='/api/cards')

    # Отдаём фронтенд
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    # Создаём таблицы при первом запуске
    with app.app_context():
        db.create_all()

    return app
