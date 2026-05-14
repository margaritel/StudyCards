from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db
from app.models import CardSet, Card, Favorite, User
from app.auth import login_required

sets_bp = Blueprint('sets', __name__)


def get_current_user_id():
    """Получить user_id из JWT токена. Возвращает None если токен невалидный."""
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception:
        return None


# GET /api/sets/subjects — все уникальные предметы
@sets_bp.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = db.session.query(CardSet.subject).distinct().order_by(CardSet.subject).all()
    return jsonify([s[0] for s in subjects]), 200


# GET /api/sets/my — наборы текущего пользователя
@sets_bp.route('/my', methods=['GET'])
def my_sets():
    user_id = get_current_user_id()
    # Fallback: по username из query
    if not user_id:
        username = request.args.get('username', '')
        if not username:
            return jsonify([]), 200
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify([]), 200
        user_id = user.id
    sets = CardSet.query.filter_by(author_id=user_id).order_by(CardSet.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sets]), 200


# GET /api/sets/my-liked-ids — лайкнутые наборы
@sets_bp.route('/my-liked-ids', methods=['GET'])
def liked_ids():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify([]), 200
    favs = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([f.set_id for f in favs]), 200


# GET /api/sets/ — все наборы (с фильтрами)
@sets_bp.route('/', methods=['GET'])
def get_sets():
    subject = request.args.get('subject')
    grade = request.args.get('grade')
    search = request.args.get('search')
    sort = request.args.get('sort', 'popular')

    query = CardSet.query

    if subject:
        query = query.filter(CardSet.subject == subject)
    if grade:
        query = query.filter(CardSet.grade == grade)

    if search:
        words = search.strip().lower().split()
        all_sets = query.all()
        result = []
        for s in all_sets:
            title_lower = s.title.lower()
            match = True
            for word in words:
                stem = word[:-1] if len(word) > 3 else word
                if stem not in title_lower:
                    match = False
                    break
            if match:
                result.append(s)
        return jsonify([s.to_dict() for s in result]), 200

    if sort == 'new':
        query = query.order_by(CardSet.created_at.desc())
    else:
        query = query.order_by(CardSet.likes_count.desc())

    sets = query.all()
    return jsonify([s.to_dict() for s in sets]), 200


# GET /api/sets/<id> — один набор с карточками
@sets_bp.route('/<int:set_id>', methods=['GET'])
def get_set(set_id):
    card_set = CardSet.query.get_or_404(set_id, description='Набор не найден')
    result = card_set.to_dict()
    result['cards'] = [c.to_dict() for c in card_set.cards]
    return jsonify(result), 200


# POST /api/sets/ — создать набор
@sets_bp.route('/', methods=['POST'])
def create_set():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    title = data.get('title', '').strip()
    subject = data.get('subject', '').strip()
    grade = data.get('grade', '').strip()
    cards_data = data.get('cards', [])

    if not title:
        return jsonify({'error': 'Введите название набора'}), 400
    if not subject:
        return jsonify({'error': 'Выберите предмет'}), 400
    if not grade:
        return jsonify({'error': 'Выберите класс'}), 400
    if not cards_data:
        return jsonify({'error': 'Добавьте хотя бы одну карточку'}), 400

    for i, card in enumerate(cards_data):
        if not card.get('question', '').strip():
            return jsonify({'error': f'Карточка {i+1}: введите вопрос'}), 400
        if not card.get('answer', '').strip():
            return jsonify({'error': f'Карточка {i+1}: введите ответ'}), 400

    # Получаем автора из JWT или из username в теле
    user_id = get_current_user_id()
    if not user_id:
        username = data.get('username', '').strip()
        user = User.query.filter_by(username=username).first() if username else None
        if not user:
            return jsonify({'error': 'Нужно войти в аккаунт'}), 401
        user_id = user.id

    card_set = CardSet(title=title, subject=subject, grade=grade or None, author_id=user_id)
    db.session.add(card_set)
    db.session.flush()

    for card_data in cards_data:
        card = Card(
            set_id=card_set.id,
            question=card_data['question'].strip(),
            answer=card_data['answer'].strip()
        )
        db.session.add(card)

    db.session.commit()
    result = card_set.to_dict()
    result['cards'] = [c.to_dict() for c in card_set.cards]
    return jsonify(result), 201


# PUT /api/sets/<id> — редактировать набор
@sets_bp.route('/<int:set_id>', methods=['PUT'])
def update_set(set_id):
    card_set = CardSet.query.get_or_404(set_id, description='Набор не найден')
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    # Проверяем права
    user_id = get_current_user_id()
    if user_id and card_set.author_id != user_id:
        return jsonify({'error': 'Нет доступа'}), 403

    title = data.get('title', '').strip()
    subject = data.get('subject', '').strip()
    grade = data.get('grade', '').strip()
    cards_data = data.get('cards', [])

    if not title:
        return jsonify({'error': 'Введите название набора'}), 400
    if not subject:
        return jsonify({'error': 'Выберите предмет'}), 400
    if not cards_data:
        return jsonify({'error': 'Добавьте хотя бы одну карточку'}), 400

    card_set.title = title
    card_set.subject = subject
    card_set.grade = grade or None

    Card.query.filter_by(set_id=set_id).delete()
    for card_data in cards_data:
        if not card_data.get('question', '').strip() or not card_data.get('answer', '').strip():
            continue
        card = Card(
            set_id=set_id,
            question=card_data['question'].strip(),
            answer=card_data['answer'].strip()
        )
        db.session.add(card)

    db.session.commit()
    result = card_set.to_dict()
    result['cards'] = [c.to_dict() for c in card_set.cards]
    return jsonify(result), 200


# DELETE /api/sets/<id> — удалить набор
@sets_bp.route('/<int:set_id>', methods=['DELETE'])
def delete_set(set_id):
    card_set = CardSet.query.get_or_404(set_id, description='Набор не найден')

    user_id = get_current_user_id()
    if user_id and card_set.author_id != user_id:
        return jsonify({'error': 'Нет доступа'}), 403

    db.session.delete(card_set)
    db.session.commit()
    return jsonify({'message': 'Набор удалён'}), 200


# POST /api/sets/<id>/favorite — лайк (без авторизации, через localStorage)
@sets_bp.route('/<int:set_id>/favorite', methods=['POST'])
def toggle_favorite(set_id):
    card_set = CardSet.query.get_or_404(set_id, description='Набор не найден')
    data = request.get_json() or {}
    action = data.get('action', 'add')

    if action == 'remove':
        card_set.likes_count = max(0, card_set.likes_count - 1)
    else:
        card_set.likes_count += 1

    db.session.commit()
    return jsonify({'likes_count': card_set.likes_count}), 200


# GET /api/sets/favorites — избранные (по JWT)
@sets_bp.route('/favorites', methods=['GET'])
def favorite_sets():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify([]), 200
    favs = Favorite.query.filter_by(user_id=user_id).all()
    set_ids = [f.set_id for f in favs]
    sets = CardSet.query.filter(CardSet.id.in_(set_ids)).all()
    return jsonify([s.to_dict() for s in sets]), 200
