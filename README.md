# tg-bot-service

Telegram bot (aiogram 3) + FastAPI backend + PostgreSQL.

## Требования

- Python 3.11+
- PostgreSQL

## Установка

Бот:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r bot-requirements.txt
```

Backend:

```bash
pip install -r backend/requirements.txt
```

## Конфигурация

Скопируйте `.env.example` в `.env` и заполните значения.
Для токенов требуется `JWT_SECRET`.

## Миграции

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

## Запуск

Backend:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Bot:

```bash
python -m bot.main
```

## Docker

```bash
docker-compose up --build
```

## API

Регистрация (бот, /start):

```
POST /api/tg/profile
{
  "username": "user",
  "phone": "+79990000000",
  "first_name": "Иван",
  "last_name": "Иванов",
  "birth_year": 1999,
  "gender": "male"
}
```

Логин (телефон):

```
POST /api/auth/login
{
  "phone": "+79990000000"
}
```

Логин из Telegram WebApp (initData):

```
POST /api/auth/telegram
{
  "phone": "+79990000000",
  "initData": "query_id=..."
}
```

Профиль (GET, только чтение):

```
GET /api/profile (Authorization: Bearer <token>)
```

План на сегодня (GET, только чтение):

```
GET /today (Authorization: Bearer <token>)
```

Прогресс (GET, только чтение):

```
GET /progress?period=week (Authorization: Bearer <token>)
GET /progress?period=month (Authorization: Bearer <token>)
```

Задумки (POST, единственный POST в боте):

```
POST /ideas (Authorization: Bearer <token>)
{
  "text": "сделать отдельный дизайн для задач",
  "source": "telegram"
}
```

## WebApp (заготовка)

```
https://app.domain.com
```
