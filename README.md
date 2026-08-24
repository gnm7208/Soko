# Soko

A marketplace platform connecting retailers with customers — listings, search, maps, delivery, chat, ratings, and payments.

## Stack

- **Backend:** Flask 3.x + SQLAlchemy 2.x + Alembic + PostgreSQL
- **Auth:** JWT in httpOnly cookies + Bcrypt
- **Validation:** Marshmallow schemas
- **Realtime:** Flask-SocketIO
- **Payments:** Stripe + Flutterwave/Paystack webhooks
- **Testing:** pytest + factory_boy
- **Lint:** ruff

## Quick Start

```bash
cp .env.example .env
docker compose up -d
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
flask run
```

## API Docs

Swagger UI available at `http://localhost:5000/api/docs` when running.

## Environment

See `.env.example` for all required variables.

## Testing

```bash
pytest server/tests/ -v
```

## Lint

```bash
ruff check server/
ruff format server/
```
