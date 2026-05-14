# StudyShare

Платформа для обмена учебными карточками. Школьники и студенты создают наборы карточек и делятся ими.

## Технологии

- Backend: Python + Flask
- База данных: PostgreSQL + SQLAlchemy
- Frontend: HTML + Bootstrap 5 + Vanilla JS
- Авторизация: JWT
- Деплой: Docker + Gunicorn + Nginx

## Запуск через Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone <url>
cd studyshare

# 2. Запустить
docker-compose up --build
```

Сайт будет доступен на http://localhost:5000

## Запуск локально (без Docker)

```bash
# 1. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать базу данных PostgreSQL и настроить .env.local
# Скопировать .env.local в .env и заменить данные подключения

# 4. Запустить
python run.py
```

## Структура проекта

```
studyshare/
├── app/
│   ├── __init__.py        # Создание Flask приложения
│   ├── models.py          # Модели базы данных
│   ├── auth.py            # Декораторы авторизации
│   └── routes/
│       ├── auth_routes.py # Регистрация и вход
│       ├── sets_routes.py # CRUD для наборов
│       └── cards_routes.py
├── frontend/              # HTML/CSS/JS
├── .env                   # Переменные окружения
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
