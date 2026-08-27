# Soko

A marketplace platform connecting retailers with customers — listings, search, maps, delivery, chat, ratings, and payments.

## Live

- **App:** [soko-app-eight.vercel.app](https://soko-app-eight.vercel.app)
- **API:** [soko-api-24sn.onrender.com](https://soko-api-24sn.onrender.com)

Both are hosted on free tiers — the API sleeps after ~15 minutes idle, so the first request after a while can take 30-50s to wake up.

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
