from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

# Декоратор для защиты роутов — просто вешаем @login_required на любой роут
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': 'Нужно войти в аккаунт'}), 401
        return f(*args, **kwargs)
    return decorated


# Декоратор для проверки что пользователь является автором набора
def author_required(get_set_func):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({'error': 'Нужно войти в аккаунт'}), 401

            current_user_id = get_jwt_identity()
            card_set = get_set_func(*args, **kwargs)

            if card_set is None:
                return jsonify({'error': 'Набор не найден'}), 404

            if card_set.author_id != current_user_id:
                return jsonify({'error': 'Нет доступа — вы не автор этого набора'}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
