# tg-bot-service

Telegram bot (aiogram 3) + FastAPI backend + PostgreSQL.

## Требования

- Python 3.11+
- PostgreSQL

## Установка

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Конфигурация

Скопируйте и заполните `.env`:

```
BOT_TOKEN=...
CRM_BASE_URL=http://127.0.0.1:8000
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tg_bot
```

## Миграции

```bash
python -m alembic -c alembic.ini upgrade head
```

## Запуск

Backend:

```bash
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```

Bot:

```bash
python -m app.main
```

## API

Регистрация (бот, /start):

```
POST /api/tg/profile
{
  "tg_id": 123456,
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
GET /today?tg_id=123456
```

Прогресс (GET, только чтение):

```
GET /progress?tg_id=123456&period=week
GET /progress?tg_id=123456&period=month
```

Задумки (POST, единственный POST в боте):

```
POST /ideas
{
  "tg_id": 123456,
  "text": "сделать отдельный дизайн для задач",
  "source": "telegram"
}
```

## WebApp (заготовка)

Планируемый URL:

```
https://app.domain.com?tg_id=123456
```
