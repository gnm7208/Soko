# Soko — MVP Build Plan

> A marketplace app (like Jiji.com) that connects retailers of all product types with customers — with listings, search, location & directions, delivery, chat, ratings, and payments.
>
> **This document is written to be handed directly to Claude inside VS Code** (Claude Code / the VS Code extension). Work through it milestone by milestone, pasting each milestone's prompt when you get there.

---

## 1. How to use this document with Claude in VS Code

1. Create an empty folder, open it in VS Code, and open Claude.
2. First, paste **Milestone 0** (project scaffold). Let it finish and commit.
3. Then paste each following milestone's **prompt block** one at a time. Don't paste the whole doc at once — build in vertical slices so each piece is testable.
4. After each milestone, run the app, click through it, and commit to git before moving on.
5. Keep this file in the repo as `/docs/BUILD_PLAN.md` so Claude always has the full context.

**Rule of thumb for prompting Claude:** give it one milestone, tell it to (a) implement, (b) run/typecheck, and (c) tell you how to test manually before you move on.

---

## 2. Product scope (agreed)

- **Platforms:** Web **and** mobile (shared backend).
- **Payments:** All methods — mobile money (M-Pesa / Flutterwave / Paystack), cards (Stripe), and cash on delivery.
- **Scope:** Full marketplace — listings, search, retailer profiles, maps & directions, buyer↔seller chat, orders, delivery flow, ratings & reviews, promotions, wallets, and an admin dashboard.

### User roles

| Role | Can do |
|------|--------|
| **Buyer** | Browse/search listings, view retailer on map + directions, chat, place orders, pay, track delivery, review. |
| **Retailer (seller)** | Create a shop, post/manage listings, set location, receive orders, chat, manage delivery, view wallet/earnings, run promotions. |
| **Rider / delivery** | (Optional for v1) accept delivery jobs, update delivery status. |
| **Admin** | Approve retailers/listings, resolve disputes, manage categories, view metrics, handle payouts. |

---

## 3. Recommended tech stack

Chosen to be fast to build, cheap to run, and one that AI coding assistants handle very well (huge training coverage, one language end-to-end).

**Language everywhere: TypeScript.**

| Layer | Choice | Why |
|-------|--------|-----|
| **Monorepo** | Turborepo + pnpm workspaces | Share types/logic between web, mobile, and backend. |
| **Web app** | Next.js (App Router) + React + Tailwind CSS + shadcn/ui | SEO for listings, fast, great DX. |
| **Mobile app** | Expo (React Native) + NativeWind (Tailwind) | iOS + Android from one codebase; reuses React skills. |
| **Backend / data** | **Supabase** (Postgres + Auth + Storage + Realtime + Row-Level Security) | Replaces most custom backend: auth, database, file storage, and realtime chat out of the box. Massive MVP time saver. |
| **Custom server logic** | Supabase Edge Functions (Deno) **or** a small Next.js API route layer | Payment webhooks, order state machine, payout logic. |
| **Payments** | Stripe (cards) + **Flutterwave** or **Paystack** (mobile money, incl. M-Pesa) + cash-on-delivery flag | Covers "all methods." Flutterwave/Paystack cover African mobile money incl. M-Pesa. |
| **Maps & directions** | Google Maps Platform (Maps SDK + Directions API) or Mapbox | Store lat/lng per shop; show map, distance, and turn-by-turn directions. |
| **Notifications** | Expo Push (mobile) + email via Resend | Order/chat alerts. |
| **Media** | Supabase Storage (or Cloudinary for image optimization) | Listing photos. |
| **Deploy** | Vercel (web) · Supabase cloud (backend) · EAS (mobile builds) | Low ops overhead. |
| **CI / quality** | GitHub + ESLint + Prettier + TypeScript strict + Vitest/Playwright | Keep Claude's output honest. |

> **Alternative if you'd rather own the backend:** NestJS + Prisma + Postgres instead of Supabase. More control and more code. For an MVP, Supabase is the recommended path and the rest of this plan assumes it. The data model below maps cleanly to either.

---

## 4. Data model (core tables)

All in Postgres (Supabase). Every table gets `id (uuid)`, `created_at`, `updated_at`. Enforce access with Row-Level Security.

- **profiles** — extends Supabase `auth.users`. `role` (buyer|retailer|rider|admin), `full_name`, `phone`, `avatar_url`.
- **shops** — `owner_id → profiles`, `name`, `description`, `logo_url`, `category`, `address`, `lat`, `lng`, `status` (pending|active|suspended), `rating_avg`, `rating_count`.
- **categories** — `name`, `slug`, `parent_id` (self-reference for subcategories), `icon`.
- **listings** — `shop_id`, `title`, `description`, `price`, `currency`, `category_id`, `condition` (new|used), `stock`, `status` (active|sold|hidden), `location` (denormalized lat/lng from shop or custom).
- **listing_images** — `listing_id`, `url`, `position`.
- **favorites** — `user_id`, `listing_id`.
- **conversations** — `buyer_id`, `shop_id`, `listing_id` (nullable), `last_message_at`.
- **messages** — `conversation_id`, `sender_id`, `body`, `read_at`. (Realtime.)
- **orders** — `buyer_id`, `shop_id`, `status` (pending|confirmed|paid|preparing|out_for_delivery|delivered|cancelled|refunded), `total`, `currency`, `payment_method`, `payment_status`, `delivery_method` (pickup|delivery), `delivery_address`, `delivery_lat/lng`, `rider_id` (nullable).
- **order_items** — `order_id`, `listing_id`, `title_snapshot`, `price_snapshot`, `qty`.
- **payments** — `order_id`, `provider` (stripe|flutterwave|paystack|cash), `provider_ref`, `amount`, `status`, raw webhook payload.
- **deliveries** — `order_id`, `rider_id`, `status`, `pickup_lat/lng`, `dropoff_lat/lng`, `tracking_updates` (jsonb).
- **reviews** — `order_id`, `shop_id`, `buyer_id`, `rating` (1–5), `comment`. (Drives `shops.rating_avg`.)
- **promotions** — `shop_id` or `listing_id`, `type` (featured|discount), `starts_at`, `ends_at`, `discount_pct`.
- **wallets** — `owner_id`, `balance`, `currency`. **wallet_transactions** — `wallet_id`, `type` (credit|debit|payout), `amount`, `ref`, `status`.
- **notifications** — `user_id`, `type`, `payload` (jsonb), `read_at`.

**Order status machine (enforce server-side):**
`pending → confirmed → paid → preparing → out_for_delivery → delivered` with `cancelled` / `refunded` as side exits.

---

## 5. Feature specs

### 5.1 Auth & onboarding
Email/OTP + phone sign-in via Supabase Auth. Role chosen at signup (buyer default; "sell on Soko" upgrades to retailer and creates a shop). Retailers pending admin approval before listings go public.

### 5.2 Listings & search
Create/edit listing with photos, price, category, condition, stock, and location. Search by keyword + filters (category, price range, condition, distance/near me). Sort by relevance, price, newest, distance. Full-text search via Postgres `tsvector`; distance via PostGIS `earthdistance` or a haversine SQL function.

### 5.3 Retailer profile, map & directions
Public shop page: info, rating, listings, and a map pin. "Get directions" opens turn-by-turn (Directions API) and shows distance/ETA from the buyer's current location.

### 5.4 Chat (buyer ↔ seller)
Realtime 1:1 threads scoped to a shop (optionally a listing). Unread counts, push/email on new message when offline. Built on Supabase Realtime on the `messages` table.

### 5.5 Cart, checkout & orders
Cart per shop (an order can't span multiple shops in v1). Checkout collects delivery method (pickup or delivery + address/pin) and payment method. Creates an order + payment intent.

### 5.6 Payments (all methods)
- **Cards:** Stripe PaymentIntent + webhook → mark order `paid`.
- **Mobile money (incl. M-Pesa):** Flutterwave or Paystack charge + webhook → mark `paid`.
- **Cash on delivery:** order goes to `confirmed`; marked `paid` when rider/seller confirms receipt.
All payment confirmations happen **server-side via webhooks**, never trusted from the client.

### 5.7 Delivery flow
Seller marks `preparing` → assigns/accepts a rider (or self-delivery) → `out_for_delivery` with live status updates → buyer confirms/`delivered`. Simple tracking timeline in v1; live GPS is a stretch goal.

### 5.8 Ratings & reviews
Buyer can review a shop after `delivered`. Recompute `rating_avg`/`rating_count` on insert (trigger).

### 5.9 Promotions & wallets
Sellers pay to "feature" listings (surface first in search) or set discounts. Wallet accrues sale proceeds (minus platform fee) and supports payout requests handled by admin.

### 5.10 Admin dashboard (web only)
Approve shops/listings, manage categories, view orders/GMV/user metrics, resolve disputes, approve payouts.

---

## 6. Build milestones (paste each prompt into Claude in VS Code)

Each milestone is a shippable vertical slice. Commit after each.

### Milestone 0 — Scaffold
> **Prompt:** "Set up a Turborepo monorepo with pnpm. Create three workspaces: `apps/web` (Next.js App Router + TypeScript + Tailwind + shadcn/ui), `apps/mobile` (Expo + React Native + NativeWind + TypeScript), and `packages/shared` (shared TypeScript types and a Supabase client). Add ESLint, Prettier, and TypeScript strict mode across all workspaces. Initialize git and add a `.gitignore`. Give me the commands to run each app."

### Milestone 1 — Supabase + data model + auth
> **Prompt:** "Add Supabase. Create SQL migrations for these tables: profiles, shops, categories, listings, listing_images, favorites, conversations, messages, orders, order_items, payments, deliveries, reviews, promotions, wallets, wallet_transactions, notifications — using the schema in `/docs/BUILD_PLAN.md` section 4. Add Row-Level Security policies (users read public listings; only owners edit their shop/listings; only order participants see their orders). Implement email/OTP + phone auth in both web and mobile with a shared Supabase client from `packages/shared`. Add role selection at signup."

### Milestone 2 — Listings & search
> **Prompt:** "Build listing create/edit (with multi-image upload to Supabase Storage) for retailers, and a public browse/search screen for buyers with category, price, condition, and 'near me' distance filters plus sorting. Add Postgres full-text search and a haversine distance function. Implement on both web and mobile, reusing shared types."

### Milestone 3 — Shop profile + maps & directions
> **Prompt:** "Build the public shop profile page (info, rating, listings, map pin) and integrate Google Maps: show the shop location, compute distance from the buyer, and a 'Get directions' action using the Directions API (web: embedded map; mobile: react-native-maps + open native maps). Store lat/lng on shops and let retailers set their location by pin or address geocoding."

### Milestone 4 — Chat
> **Prompt:** "Implement realtime buyer↔seller chat using Supabase Realtime on the messages table. Conversation list, thread view, unread counts, and 'message seller' from a listing. Web and mobile."

### Milestone 5 — Cart, checkout & orders
> **Prompt:** "Build a per-shop cart, a checkout flow (delivery method + address/pin, payment method selection), and order creation with the order status state machine from section 4. Add a buyer 'My Orders' view and a seller 'Incoming Orders' view. No real payment yet — stub payment as pending."

### Milestone 6 — Payments (all methods)
> **Prompt:** "Integrate payments via server-side webhooks only: Stripe for cards, Flutterwave (or Paystack) for mobile money including M-Pesa, and a cash-on-delivery path. On successful webhook, advance the order to 'paid'. Never trust payment status from the client. Put secrets in env vars and document them."

### Milestone 7 — Delivery flow
> **Prompt:** "Implement the delivery lifecycle: seller marks preparing → out_for_delivery → buyer confirms delivered, with a status timeline. Add an optional rider role that can accept and update deliveries. Trigger push/email notifications on status changes."

### Milestone 8 — Ratings, promotions, wallets
> **Prompt:** "Add post-delivery shop reviews (1–5 + comment) with a trigger that recomputes shop rating. Add promotions (featured listings surface first in search; percentage discounts). Add seller wallets that accrue sale proceeds minus a platform fee, with payout requests."

### Milestone 9 — Admin dashboard
> **Prompt:** "Build a web-only admin dashboard (protected by admin role): approve shops/listings, manage categories, view orders/GMV/user metrics, resolve disputes, and approve payouts."

### Milestone 10 — Hardening & launch prep
> **Prompt:** "Add input validation (zod), error handling, loading/empty states, unit tests (Vitest) for the order state machine and payment webhooks, and a Playwright happy-path e2e (signup → list → order → pay → deliver → review). Set up env var docs, seed data, and deployment configs for Vercel (web) and EAS (mobile)."

---

## 7. Non-functional requirements

- **Security:** RLS on every table; validate all input server-side; verify webhook signatures; secrets only in env vars.
- **Performance:** paginate listings; index search/distance columns; optimize images.
- **Money handling:** store amounts as integers (minor units) with an explicit currency; never do float math on money.
- **Observability:** basic logging + Sentry.
- **Accessibility & i18n:** structure copy for future translation (Swahili/English); semantic components.

---

## 8. Suggested repo structure

```
soko/
├─ apps/
│  ├─ web/                 # Next.js (buyers, sellers, admin)
│  └─ mobile/              # Expo React Native (buyers, sellers, riders)
├─ packages/
│  ├─ shared/              # types, zod schemas, supabase client, order state machine
│  └─ ui/                  # (optional) shared design tokens
├─ supabase/
│  ├─ migrations/          # SQL schema + RLS
│  └─ functions/           # edge functions (payment webhooks, payouts)
├─ docs/
│  └─ BUILD_PLAN.md        # this file
└─ turbo.json
```

---

## 9. Definition of done for the MVP

A buyer can sign up, search listings near them, view a shop on a map and get directions, chat with the seller, place an order, pay (card / mobile money / cash), track delivery, and leave a review — while a retailer can register a shop, get approved, post listings, receive and fulfill orders, and see earnings, and an admin can approve and monitor the marketplace.
