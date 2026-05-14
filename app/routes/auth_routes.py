from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app import db
from app.models import User
from app.auth import login_required
import bcrypt

auth_bp = Blueprint('auth', __name__)


# POST /api/auth/register — регистрация
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Валидация
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm = data.get('confirm_password', '')

    if not username:
        return jsonify({'error': 'Введите имя пользователя'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Имя пользователя минимум 3 символа'}), 400
    if not username.replace('_', '').isalnum():
        return jsonify({'error': 'Только буквы, цифры и _'}), 400
    if not password:
        return jsonify({'error': 'Введите пароль'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Пароль минимум 6 символов'}), 400
    if password != confirm:
        return jsonify({'error': 'Пароли не совпадают'}), 400

    # Проверяем уникальность
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Такое имя пользователя уже занято'}), 409

    # Хешируем пароль
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': user.to_dict()}), 201


# POST /api/auth/login — вход
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Введите имя пользователя и пароль'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401

    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': user.to_dict()}), 200


# GET /api/auth/me — получить текущего пользователя
@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    return jsonify(user.to_dict()), 200
