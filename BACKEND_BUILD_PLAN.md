# Soko — Backend Build Plan

> Marketplace backend (buyer ↔ retailer ↔ admin, shared between web and mobile).
> Written for Flask + PostgreSQL per George's Project Playbook conventions.

---

## 1. Architecture & Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | Flask 3.x (app factory + blueprints) | Proven stack, fine-grained control, matches Playbook |
| **ORM** | SQLAlchemy 2.x (async optional but start sync) | Familiar, mature, Alembic integration |
| **Migrations** | Alembic | Version-controlled schema evolution |
| **Auth** | Flask-JWT-Extended (httpOnly cookies) + Bcrypt | Matches Playbook JWT+cookie pattern |
| **Validation** | Marshmallow (or Pydantic) schemas | Enforce at API boundary; generates OpenAPI |
| **API Docs** | Flask-Smorest (Marshmallow → OpenAPI) | Auto-generated Swagger UI at `/api/docs` |
| **Realtime/Chat** | Flask-SocketIO | WebSocket chat for buyer↔seller |
| **Payments** | Stripe SDK + requests (Flutterwave/Paystack) | Server-side webhooks only |
| **Media** | Local filesystem or Cloudinary | Listing photos |
| **Testing** | pytest + factory_boy | Per-route test files, conftest fixtures |
| **Lint/Format** | ruff | Backend lint + format |
| **Deploy** | Render (web service) | Render.yaml, health endpoint |
| **CI** | GitHub Actions | Lint → tests → pip-audit → deploy |

### Why not Supabase?
The MVP plan proposes Supabase for speed. For Soko, a custom Flask backend is chosen because:
- Full control over payment webhook logic, order state machine, and payout math.
- Proven testing culture (~200 pytest tests on Agrilink).
- No vendor lock-in on edge functions or row-level security policies.
- Matches the Project Playbook's full-stack default.

---

## 2. Repository Layout

```
soko/
├─ server/
│  ├─ app.py                  # Application factory
│  ├─ config.py               # Config classes (dev/staging/prod)
│  ├─ extensions.py           # db, migrate, jwt, cors, limiter, socketio
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ profile.py
│  │  ├─ shop.py
│  │  ├─ category.py
│  │  ├─ listing.py
│  │  ├─ listing_image.py
│  │  ├─ favorite.py
│  │  ├─ conversation.py
│  │  ├─ message.py
│  │  ├─ order.py
│  │  ├─ order_item.py
│  │  ├─ payment.py
│  │  ├─ delivery.py
│  │  ├─ review.py
│  │  ├─ promotion.py
│  │  ├─ wallet.py
│  │  ├─ wallet_transaction.py
│  │  └─ notification.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ profiles.py
│  │  ├─ shops.py
│  │  ├─ categories.py
│  │  ├─ listings.py
│  │  ├─ favorites.py
│  │  ├─ search.py
│  │  ├─ chat.py
│  │  ├─ orders.py
│  │  ├─ payments.py
│  │  ├─ deliveries.py
│  │  ├─ reviews.py
│  │  ├─ promotions.py
│  │  ├─ wallets.py
│  │  ├─ notifications.py
│  │  └─ admin.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ order_state_machine.py
│  │  ├─ payment_webhooks.py
│  │  ├─ geolocation.py        # haversine, geocoding helpers
│  │  ├─ search.py             # full-text + distance query builders
│  │  ├─ notifications.py      # email + push dispatcher
│  │  └─ storage.py            # image upload/delete wrapper
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ listing.py
│  │  ├─ order.py
│  │  └─ ...                   # one per domain
│  ├─ utils/
│  │  ├─ __init__.py
│  │  ├─ validators.py
│  │  ├─ errors.py
│  │  └─ pagination.py
│  ├─ tests/
│  │  ├─ conftest.py
│  │  ├─ test_auth.py
│  │  ├─ test_listings.py
│  │  ├─ test_orders.py
│  │  ├─ test_payments.py
│  │  ├─ test_chat.py
│  │  └─ ...                   # mirror routes/
│  ├─ migrations/              # Alembic
│  ├─ static/
│  │  └─ openapi.yaml          # Generated spec (or auto-served)
│  ├─ .env.example
│  └─ wsgi.py
├─ client/                     # Ignored for this plan
└─ README.md
```

---

## 3. Data Model (SQLAlchemy)

Every table gets `id (UUID)`, `created_at`, `updated_at`.

### Core Tables

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `profiles` | user_id (FK auth.users), role, full_name, phone, avatar_url | Extends Flask-Login/JWT identity |
| `shops` | owner_id → profiles, name, description, logo_url, category, address, lat, lng, status, rating_avg, rating_count | status: pending\|active\|suspended |
| `categories` | name, slug, parent_id (self-ref), icon | Hierarchical |
| `listings` | shop_id, title, description, price, currency, category_id, condition, stock, status, location(lat/lng) | status: active\|sold\|hidden |
| `listing_images` | listing_id, url, position | |
| `favorites` | user_id, listing_id | Unique constraint |
| `conversations` | buyer_id, shop_id, listing_id (nullable), last_message_at | |
| `messages` | conversation_id, sender_id, body, read_at | SocketIO realtime |
| `orders` | buyer_id, shop_id, status, total, currency, payment_method, payment_status, delivery_method, delivery_address, delivery_lat/lng, rider_id | State machine enforced server-side |
| `order_items` | order_id, listing_id, title_snapshot, price_snapshot, qty | |
| `payments` | order_id, provider, provider_ref, amount, status, raw_payload(jsonb) | Webhook-only truth |
| `deliveries` | order_id, rider_id, status, pickup_lat/lng, dropoff_lat/lng, tracking_updates(jsonb) | |
| `reviews` | order_id, shop_id, buyer_id, rating(1-5), comment | DB trigger recomputes shop.rating_avg |
| `promotions` | shop_id or listing_id, type, starts_at, ends_at, discount_pct | type: featured\|discount |
| `wallets` | owner_id, balance, currency | Integer minor units |
| `wallet_transactions` | wallet_id, type, amount, ref, status | type: credit\|debit\|payout |
| `notifications` | user_id, type, payload(jsonb), read_at | |

### Order Status State Machine (server-side enforced)

```
pending → confirmed → paid → preparing → out_for_delivery → delivered
                         ↘ cancelled / refunded (side exits)
```

Implemented as a Python class (`services/order_state_machine.py`) with explicit transitions and event hooks.

### Money Handling
- Store all amounts as **integers (minor units)** with explicit `currency` column.
- Never float math on money; use `int(round(amount * 100))`.

---

## 4. Authentication & RBAC

### Roles
| Role | Decorator |
|------|-----------|
| buyer | `@buyer_required` |
| retailer | `@retailer_required` |
| rider | `@rider_required` |
| admin | `@admin_required` |

### Flow
1. **Register**: email+password or phone+password. Marshmallow schema validates. Bcrypt hash. JWT issued. Role defaults to `buyer`.
2. **Sell on Soko**: retailer upgrades profile → creates shop (status=`pending`) → admin approves → shop goes `active`.
3. **Login**: credentials check → JWT in httpOnly cookie + optional refresh token.
4. **RBAC decorators** on every route. `current_user` injected from JWT claims.

### Rate Limiting (Playbook convention)
- `/api/auth/register`: 3/min
- `/api/auth/login`: 5/min
- Other routes: standard limiter

---

## 5. API Route Map

### Auth & Profiles
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Create account, choose role |
| POST | `/api/auth/login` | — | Issue JWT cookie |
| POST | `/api/auth/logout` | any | Clear cookie |
| GET | `/api/auth/me` | any | Current profile |
| PATCH | `/api/auth/me` | any | Update profile |
| PATCH | `/api/auth/upgrade-retailer` | buyer | Create shop draft |

### Shops
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/shops` | — | List public (filters: category, near, rating) |
| GET | `/api/shops/<id>` | — | Public detail |
| PATCH | `/api/shops/<id>` | retailer(owner) | Update shop info, lat/lng |
| POST | `/api/shops` | buyer→retailer | Create shop (status=pending) |

### Categories
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/categories` | — | List tree |
| POST | `/api/categories` | admin | Create |
| PATCH | `/api/categories/<id>` | admin | Update |
| DELETE | `/api/categories/<id>` | admin | Delete |

### Listings
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/listings` | — | Browse/search (see §6) |
| GET | `/api/listings/<id>` | — | Detail |
| POST | `/api/listings` | retailer | Create |
| PATCH | `/api/listings/<id>` | retailer(owner) | Update |
| DELETE | `/api/listings/<id>` | retailer(owner) | Soft-delete (status=hidden) |
| POST | `/api/listings/<id>/images` | retailer(owner) | Upload image |

### Favorites
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/favorites/<listing_id>` | buyer | Toggle favorite |
| GET | `/api/favorites` | buyer | My favorites |

### Search
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/search` | — | Keyword + filters (category, price, condition, distance, sort) |

### Chat
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/conversations` | any | My threads |
| GET | `/api/conversations/<id>` | participant | Messages |
| POST | `/api/conversations` | buyer | Start thread (shop_id, optional listing_id) |
| POST | `/api/conversations/<id>/messages` | participant | Send message |
| WS | `/ws/chat/<conversation_id>` | participant | Realtime messages via SocketIO |

### Orders
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/orders` | any | My orders (role-scoped) |
| GET | `/api/orders/<id>` | participant | Detail |
| POST | `/api/orders` | buyer | Create from cart items |
| PATCH | `/api/orders/<id>/status` | seller\|rider\|admin | Advance state machine |
| POST | `/api/orders/<id>/cancel` | buyer\|seller | Cancel if allowed |

### Payments (Webhooks)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/webhooks/stripe` | — | Verify signature, mark paid |
| POST | `/api/webhooks/flutterwave` | — | Verify signature, mark paid |
| POST | `/api/webhooks/paystack` | — | Verify signature, mark paid |
| POST | `/api/payments/intent` | buyer | Create payment intent (client gets client_secret) |

### Deliveries
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/deliveries` | rider\|admin | Available / assigned jobs |
| PATCH | `/api/deliveries/<id>` | rider\|seller | Update status, tracking |
| POST | `/api/deliveries/<id>/assign` | seller\|admin | Assign rider |

### Reviews
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/reviews` | buyer(fulfilled_order) | Submit rating + comment |
| GET | `/api/shops/<id>/reviews` | — | Shop reviews |

### Promotions
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/promotions` | retailer | Create featured/discount |
| GET | `/api/promotions` | retailer | My promotions |
| DELETE | `/api/promotions/<id>` | retailer | Cancel |

### Wallets
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/wallets/me` | retailer\|rider | Balance |
| GET | `/api/wallets/me/transactions` | retailer\|rider | Ledger |
| POST | `/api/wallets/payout-request` | retailer | Request payout |

### Notifications
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/notifications` | any | My notifications |
| PATCH | `/api/notifications/<id>/read` | any | Mark read |
| POST | `/api/notifications/mark-all-read` | any | Bulk read |

### Admin
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/admin/metrics` | admin | GMV, users, orders |
| PATCH | `/api/admin/shops/<id>/approve` | admin | Approve retailer |
| PATCH | `/api/admin/shops/<id>/suspend` | admin | Suspend retailer |
| PATCH | `/api/admin/listings/<id>` | admin | Force hide/approve |
| PATCH | `/api/admin/payouts/<id>` | admin | Approve payout request |

---

## 6. Search & Geolocation

### Full-text search
- `tsvector` column on `listings.title || ' ' || listings.description`.
- GIN index. `@@ plainto_tsquery('english', :q)`.
- Ranked by relevance (`ts_rank`).

### Distance / "near me"
- Haversine SQL function or PostGIS `earthdistance` extension.
- Filter: `haversine(listing.lat, listing.lng, :user_lat, :user_lng) < :radius_km`.
- Index on `(lat, lng)` for performance.

### Combined search API
`GET /api/search?q=phone&category=electronics&min_price=100&max_price=5000&condition=new&lat=-1.29&lng=36.82&radius=10&sort=distance&page=1&per_page=20`

---

## 7. Payments (Server-Side Webhooks Only)

### Trust boundary
- **Client never tells server "payment succeeded".**
- Client gets a `client_secret` / `payment_intent_id` from `/api/payments/intent`.
- Provider redirects or confirms on client.
- Provider sends webhook → server verifies signature → server advances order.

### Providers
| Provider | Use | Webhook Path |
|----------|-----|--------------|
| Stripe | Cards | `/api/webhooks/stripe` |
| Flutterwave | Mobile money (M-Pesa, etc.) | `/api/webhooks/flutterwave` |
| Paystack | Mobile money (Africa) | `/api/webhooks/paystack` |
| Cash on delivery | COD flag on order | Seller/rider confirms receipt → `paid` |

### Cash on delivery flow
1. Order created with `payment_method=cash`, `payment_status=pending`.
2. Seller marks `preparing` → rider picks up → buyer confirms `delivered`.
3. Seller or rider marks cash received → order `paid`.
4. Wallet credit triggered.

---

## 8. Realtime Chat

- **Flask-SocketIO** with JWT auth on connect.
- Rooms keyed by `conversation_{id}`.
- Events: `send_message`, `receive_message`, `mark_read`.
- Unread count stored in `conversations` table (incremented server-side).
- Fallback: REST poll `/api/conversations/<id>/messages` for mobile if SocketIO reconnect is flaky.

---

## 9. Order State Machine

`services/order_state_machine.py`

```python
class OrderStateMachine:
    TRANSITIONS = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["paid", "cancelled"],
        "paid": ["preparing", "refunded"],
        "preparing": ["out_for_delivery"],
        "out_for_delivery": ["delivered", "cancelled"],
        "delivered": ["refunded"],
        "cancelled": [],
        "refunded": [],
    }

    def advance(self, order, new_status):
        if new_status not in self.TRANSITIONS.get(order.status, []):
            raise BadTransition(...)
        order.status = new_status
        self._emit_event(order, new_status)
```

Every status change goes through this class. No route bypasses it.

---

## 10. File Storage

### Listing images
- Upload endpoint: `POST /api/listings/<id>/images` (multipart/form-data).
- Wrapper `services/storage.py` supports:
  - Local filesystem (dev).
  - Cloudinary (prod) — recommended for optimization.
- Store returned URL in `listing_images.url`.
- Max 5 images per listing, max 5MB each, type check (image/jpeg, image/png, image/webp).

### Shop logos / avatars
- Separate upload endpoints under `/api/shops/<id>/logo` and `/api/auth/me/avatar`.

---

## 11. Testing Strategy

Follow Agrilink pattern: **one test file per route file**, pytest + factory_boy.

### Coverage targets
| Domain | Min coverage |
|--------|-------------|
| Auth & RBAC | 100% (every decorator path) |
| Order state machine | 100% |
| Payment webhooks | 100% (signature verification + state transitions) |
| Routes | 80% |

### Critical test cases
- Invalid status transitions are rejected.
- Webhook with bad signature is rejected (401).
- Buyer cannot access another buyer's order.
- Retailer cannot edit another retailer's listing.
- Search returns zero results for empty query with no filters.
- Money amounts stored as integers; no float in payment flow.

### CI (GitHub Actions)
```yaml
jobs:
  lint:
    runs: ruff check server/
  test:
    runs: pytest server/tests/ --cov=server --cov-fail-under=80
  security:
    runs: pip-audit
```

---

## 12. Security Checklist (Playbook + Roadmap)

- **Rate limiting** on auth routes (register 3/min, login 5/min).
- **CORS**: origins from env var, no wildcard in prod.
- **Security headers**: `Flask-Talisman` (CSP, HSTS, X-Frame-Options).
- **Input validation**: Marshmallow schemas on every request body + query params.
- **XSS escaping**: all user-generated content escaped before storage or rendering.
- **CSRF**: same-site cookies, double-submit token for non-GET non-AJAX (if any).
- **Webhook signature verification**: Stripe (`stripe-signature`), Flutterwave, Paystack.
- **Secrets**: never committed; `.env.example` documents all required vars.
- **JWT**: httpOnly, secure, sameSite=strict; short access + longer refresh.
- **File upload**: whitelist types, size limits, random filenames, no path traversal.

---

## 13. Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/soko

# JWT
JWT_SECRET_KEY=...
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=2592000

# CORS
CORS_ORIGINS=https://soko-web.vercel.app,https://soko-mobile

# Payments
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
FLUTTERWAVE_SECRET_KEY=...
FLUTTERWAVE_WEBHOOK_SECRET=...
PAYSTACK_SECRET_KEY=...
PAYSTACK_WEBHOOK_SECRET=...

# Storage
CLOUDINARY_URL=...
# or
STORAGE_PATH=./uploads

# App
ENV=development|staging|production
PORT=5000
LOG_LEVEL=info

# Notifications
RESEND_API_KEY=...
EXPO_PUSH_ACCESS_TOKEN=...
```

---

## 14. Build Milestones (Backend Only)

Each milestone is a shippable vertical slice. Commit after each.

### Milestone 0 — Scaffold
- Repo init, README, CLAUDE.md, `.gitignore`.
- Flask app factory (`app.py`, `config.py`, `extensions.py`).
- SQLAlchemy + Alembic initialized.
- pytest + factory_boy + conftest.
- ruff configured.
- GitHub Actions CI (lint + test).
- Health endpoint (`GET /api/health`).
- Docker + docker-compose for local Postgres.

### Milestone 1 — Auth + RBAC + Profiles
- `profiles` table + Alembic migration.
- JWT auth (register/login/logout) with httpOnly cookies.
- Role selection at signup.
- RBAC decorators (`@buyer_required`, `@retailer_required`, `@admin_required`).
- Profile CRUD (`/api/auth/me`).
- "Upgrade to retailer" creates pending shop.
- Tests: register, login, RBAC denial, profile update.

### Milestone 2 — Core Domain Models
- Migrations for all 17 tables.
- SQLAlchemy models with relationships.
- Admin seed command (creates first admin user).
- Seed script for categories, demo shops, demo listings.
- Tests: model relationships, cascade deletes.

### Milestone 3 — Shops + Listings + Search
- Shop CRUD (retailer owns, public reads).
- Listing CRUD with multi-image upload.
- Category tree endpoint.
- Full-text search (`tsvector` + GIN).
- Haversine distance function.
- Search endpoint with filters + pagination.
- Tests: listing creation, search ranking, distance filter.

### Milestone 4 — Orders + Order State Machine
- Order creation from cart items (per-shop cart enforced).
- Order state machine class with transition validation.
- Buyer "My Orders", Seller "Incoming Orders", Admin "All Orders".
- Webhook stubs (log payload, don't process).
- Tests: state machine transitions, invalid transitions rejected, role-scoped access.

### Milestone 5 — Payments (Webhooks)
- Stripe webhook handler (signature verify → mark paid).
- Flutterwave webhook handler.
- Paystack webhook handler.
- Cash-on-delivery confirmation flow (seller/rider marks cash received).
- Payment intent creation endpoint.
- Tests: webhook signature rejection, successful payment advances order, COD flow.

### Milestone 6 — Chat (Realtime)
- Conversation CRUD.
- Message REST endpoints.
- Flask-SocketIO integration (JWT auth on connect).
- Unread count logic.
- Tests: SocketIO message delivery, unread count, unauthorized access blocked.

### Milestone 7 — Delivery + Reviews + Ratings
- Delivery lifecycle (assign rider, status updates, tracking JSONB).
- Review submission (post-delivery only).
- DB trigger to recompute `shops.rating_avg` / `rating_count`.
- Tests: review only after delivered, rating math, rider assignment.

### Milestone 8 — Promotions + Wallets
- Promotion CRUD (featured/discount).
- Wallet model + transaction ledger.
- Payout request flow.
- Admin payout approval.
- Platform fee calculation on sale (integer math).
- Tests: wallet credit on delivery, fee math, payout approval.

### Milestone 9 — Admin + Hardening
- Admin metrics endpoint (GMV, users, orders).
- Admin approve/suspend shops.
- Admin force-hide listings.
- Input validation schemas (Marshmallow) on all routes.
- Pagination on all list endpoints.
- Error handling middleware (consistent JSON error format).
- Tests: admin metrics, RBAC on all admin routes.

### Milestone 10 — Notifications + Launch Prep
- Notification model + endpoints.
- Email dispatcher (Resend) for order/chat alerts.
- Push notification dispatcher (Expo Push).
- Seed data script (`seed_demo.py`).
- `.env.example` fully documented.
- Render deploy config.
- Load testing script for critical paths.
- OpenAPI spec finalized.

---

## 15. Non-Functional Requirements

| Requirement | Implementation |
|-------------|---------------|
| **Security** | Talisman, CORS from env, rate limits, webhook sig verify, JWT httpOnly cookies, pip-audit in CI |
| **Performance** | Paginate all lists (cursor-based where possible), GIN index on search, index on `(lat, lng)` |
| **Money** | Integer minor units everywhere, explicit currency, no float math |
| **Observability** | Structured JSON logs (request ID via `req.id` middleware), Sentry SDK, `/api/health` with DB check |
| **i18n-ready** | Copy in en/sw, structured for future translation |
| **API versioning** | `/api/v1/` prefix from day one |

---

## 16. Definition of Done

- All 10 milestones committed, each green on CI.
- Buyer can: register → search listings → view shop → chat seller → place order → pay (card/mobile/COD) → track delivery → review shop.
- Retailer can: register shop → get approved → post listings → receive orders → fulfill → see earnings/wallet.
- Admin can: approve shops → moderate listings → view metrics → approve payouts.
- Backend serves API to **both** web (Next.js) and mobile (Expo) without changes.
- All payment confirmations happen **server-side via verified webhooks**.
- Order state machine enforced in code; no client trust on status.
- All amounts in integer minor units with explicit currency.
- README documents setup, env vars, deploy, API endpoints, and roles.
