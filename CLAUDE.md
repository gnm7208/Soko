# CLAUDE.md — Soko Backend

> Guidance for AI assistants working on the Soko backend.

## Overview

Soko is a marketplace backend (Flask + PostgreSQL) powering both web (Next.js) and mobile (Expo) clients.

## Architecture

- **App factory pattern:** `server/app.py` creates and configures the Flask app.
- **Blueprints:** Each domain has its own blueprint in `server/routes/`.
- **Models:** SQLAlchemy 2.x models in `server/models/`.
- **Services:** Business logic extracted to `server/services/`.
- **Schemas:** Marshmallow schemas in `server/schemas/` for validation + serialization.
- **Extensions:** DB, migrate, JWT, CORS, limiter, SocketIO wired in `server/extensions.py`.

## Conventions

- **Commits:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`).
- **Files:** One route file per domain, one test file per route file, one schema file per domain.
- **Money:** Always integer minor units (e.g., cents). Never float math.
- **Auth:** JWT in httpOnly cookies. RBAC decorators on every route.
- **Payments:** Server-side webhooks only. Never trust client on payment success.
- **Order state machine:** All transitions go through `services/order_state_machine.py`.
- **Comments:** Explain *why*, not *what*.

## Commands

```bash
# Setup
cp .env.example .env
docker compose up -d
pip install -r requirements.txt
alembic upgrade head

# Dev
flask run

# Test
pytest server/tests/ -v

# Lint
ruff check server/
ruff format server/

# Migrations
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Database

- PostgreSQL 16 via Docker Compose locally.
- Migrations in `server/migrations/`.
- Seed with `flask seed`.

## API Versioning

All routes prefixed with `/api/v1/`.

## Security

- Rate limits: register 3/min, login 5/min.
- CORS origins from env.
- Flask-Talisman security headers in production.
- Webhook signature verification required.
- XSS escaping on all user content.
- File uploads: whitelist types, size limits, random names.
