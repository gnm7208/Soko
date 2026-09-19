# Soko

A marketplace platform connecting retailers with customers — listings, search, maps, delivery, chat, ratings, and payments.

## Live

- **App:** [soko-app-eight.vercel.app](https://soko-app-eight.vercel.app)
- **API:** [soko-api-24sn.onrender.com](https://soko-api-24sn.onrender.com)

Both are hosted on free tiers — the API sleeps after ~15 minutes idle, so the first request after a while can take 30-50s to wake up.

## Install as an app

Soko is a Progressive Web App. The web build in `soko-ui/` is also what ships to the app stores — there is no separate mobile codebase.

| Platform | How |
|---|---|
| **Android / desktop Chrome** | Open <https://soko-app-eight.vercel.app> → browser menu → **Install app** (or **Add to Home screen**). |
| **Android APK** | Download the latest signed APK from [GitHub Releases](https://github.com/gnm7208/Soko/releases) and open it (allow "install from this source" once). |
| **Microsoft Store** | Listed as **Soko** (packaged from the PWA with PWABuilder). |
| **Google Play / Amazon / Samsung** | Same Android package (`com.gnm7208.soko`); listings go live per store — check Releases for status. |

Privacy policy: <https://soko-app-eight.vercel.app/privacy.html> (also linked from every store listing; deletion requests are handled by email as described there).

**How it works.** `soko-ui/public/manifest.webmanifest` declares the app (name, colours, PNG + maskable icons), `soko-ui/public/sw.js` caches the app shell so it opens with no signal (API responses are deliberately never cached), and `soko-ui/src/lib/register-sw.ts` registers the worker in production builds only. `soko-ui/public/.well-known/assetlinks.json` links the site to the Android signing key so the Android app opens full-screen without browser chrome; the Android project itself lives outside this repo in `../store-packaging/` (Bubblewrap TWA) and the signing key in `~/.android-signing/` — never commit either.

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

Account deletion is in-app: `DELETE /api/v1/auth/me` with `{"password": "…"}` re-checks the password (403 on mismatch) and is refused with 409 while the person has orders in progress or a wallet balance; otherwise it removes their orders, chats, favourites, notifications, wallet and — for retailers — the shop with its listings, promotions and reviews.

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
