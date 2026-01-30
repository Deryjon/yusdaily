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

План на сегодня (GET, только чтение):

```
GET /today (X-PHONE: +79990000000)
```

Прогресс (GET, только чтение):

```
GET /progress?period=week (X-PHONE: +79990000000)
GET /progress?period=month (X-PHONE: +79990000000)
```

Задумки (POST, единственный POST в боте):

```
POST /ideas (X-PHONE: +79990000000)
{
  "text": "сделать отдельный дизайн для задач",
  "source": "telegram"
}
```

## WebApp (заготовка)

```
https://app.domain.com
```
