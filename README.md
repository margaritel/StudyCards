# StudyCards / StudyShare

Карточки для запоминаний. Платформа для обмена учебными карточками: школьники и студенты создают наборы и делятся ими.

[Описание проекта](https://docs.google.com/document/d/1y9ZyheFPgr88VxvDkFa59h4pxbegmJZWTSDW1h6YOKo/edit?usp=sharing)

[Ссылка на выложенный проект](https://studyshare.silaeder.space/)

## Технологии

- Backend: Python + Flask
- База данных: PostgreSQL + SQLAlchemy (SQLite для локальной разработки)
- Frontend: HTML + Bootstrap 5 + Vanilla JS
- Авторизация: JWT
- Деплой: Docker + Gunicorn + Nginx

## Запуск через Docker (рекомендуется)

```bash
git clone git@github.com:margaritel/StudyCards.git
cd StudyCards
docker-compose up --build
```

Сайт будет доступен на http://localhost:5000

## Запуск локально (без Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Скопируй .env.example в .env и заполни DATABASE_URL и JWT_SECRET_KEY
python run.py
```

## Структура проекта

```
studyshare/
├── app/
│   ├── __init__.py        # Создание Flask приложения
│   ├── models.py          # Модели БД
│   ├── auth.py            # Декораторы авторизации
│   └── routes/
│       ├── auth_routes.py # Регистрация и вход
│       ├── sets_routes.py # CRUD для наборов
│       └── cards_routes.py
├── frontend/              # HTML / CSS / JS
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
└── requirements.txt
```

## API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход |
| GET | /api/auth/me | Текущий пользователь |
| GET | /api/sets/ | Все наборы |
| GET | /api/sets/:id | Один набор с карточками |
| POST | /api/sets/ | Создать набор |
| PUT | /api/sets/:id | Редактировать набор |
| DELETE | /api/sets/:id | Удалить набор |
| POST | /api/sets/:id/favorite | Добавить/убрать из избранного |
| GET | /api/sets/my | Мои наборы |
| GET | /api/sets/favorites | Избранные наборы |
