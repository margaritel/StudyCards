from app import db
from datetime import datetime

# Таблица пользователей
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Связи
    sets = db.relationship('CardSet', backref='author', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username
        }


# Таблица наборов карточек
class CardSet(db.Model):
    __tablename__ = 'sets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(20), nullable=True)  # класс, например "7 класс"
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)

    # Связи
    cards = db.relationship('Card', backref='card_set', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='card_set', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, author_username=None):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'grade': self.grade,
            'author_id': self.author_id,
            'author_username': author_username or (self.author.username if self.author else None),
            'created_at': self.created_at.isoformat(),
            'likes_count': self.likes_count,
            'cards_count': len(self.cards)
        }


# Таблица карточек
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'set_id': self.set_id,
            'question': self.question,
            'answer': self.answer
        }


# Таблица избранного
class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Нельзя добавить один набор в избранное дважды
    __table_args__ = (db.UniqueConstraint('user_id', 'set_id', name='unique_favorite'),)
