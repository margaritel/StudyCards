from flask import Blueprint, jsonify
from app.models import Card

cards_bp = Blueprint('cards', __name__)

# GET /api/cards/<id> — одна карточка (на всякий случай)
@cards_bp.route('/<int:card_id>', methods=['GET'])
def get_card(card_id):
    card = Card.query.get_or_404(card_id, description='Карточка не найдена')
    return jsonify(card.to_dict()), 200
