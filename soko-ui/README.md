# Soko — UI Prototype (ship this to Claude in VS Code)

A working React + TypeScript + Tailwind + shadcn/ui frontend for the Soko marketplace,
styled with the **Anthropic brand** (Dark #141413 · Light #faf9f5 · Orange #d97757 ·
Blue #6a9bcc · Green #788c5d; Poppins headings, Lora body).

This is the **presentation layer** for the MVP described in `../Soko-MVP-Build-Plan.md`.
The UI uses a typed Fetch adapter in `src/services/api.ts` and hydrates listings, shops,
categories, orders, notifications, wallet data, favorites, chat, and checkout from the Flask
API when it is available. It keeps the mock data in `src/soko/data.ts` as a graceful fallback
for local demos and unseeded environments.

For local development, leave `VITE_API_URL` unset: Vite proxies `/api` to Flask on port 5000.
Set `VITE_API_URL` to the deployed `/api/v1` origin when the frontend and API are hosted separately.
The frontend sends `credentials: include` and the Flask CSRF cookie token on unsafe requests.

## Live

- **App:** [soko-app-eight.vercel.app](https://soko-app-eight.vercel.app)
- **API:** [soko-api-24sn.onrender.com](https://soko-api-24sn.onrender.com)

## Run it

```bash
pnpm install
pnpm dev        # open the printed localhost URL
pnpm build      # typechecks + production build (passes clean)
```

(Or just open `../soko-ui-preview.html` in a browser — a single self-contained file, no install.)

## Screens (all navigable via the top bar + Buy/Sell switch)

| File | Screen | Wire to (build plan) |
|------|--------|----------------------|
| `src/soko/Browse.tsx` | Home / search / categories / featured grid | `listings`, `categories`, full-text + distance search (§5.2) |
| `src/soko/ListingDetail.tsx` | Product page, seller card, buy/chat | `listings`, `shops` (§5.2–5.3) |
| `src/soko/ShopProfile.tsx` | Retailer profile + map + directions | `shops`, Google Maps/Directions (§5.3) |
| `src/soko/Chat.tsx` | Realtime buyer↔seller chat | `messages`, Supabase Realtime (§5.4) |
| `src/soko/Checkout.tsx` | Delivery method + M-Pesa/Card/Cash | `orders`, `payments` (§5.5–5.6) |
| `src/soko/Orders.tsx` | Buyer orders + delivery tracker | `orders`, `deliveries` (§5.7) |
| `src/soko/SellerDashboard.tsx` | Sales, wallet, listings, incoming orders | `wallets`, `orders`, `promotions` (§5.9) |
| `src/App.tsx` | App shell, nav, Buy/Sell mode | routing / auth (§5.1) |

## Suggested first prompt to Claude in VS Code

> "This is the Soko UI prototype. Read `../Soko-MVP-Build-Plan.md`. Set up Supabase per
> Milestone 1, generate the SQL migrations for the data model in §4, then replace the mock
> imports from `src/soko/data.ts` with live Supabase queries, starting with Browse and
> ListingDetail. Keep the existing components and Anthropic styling."

## Notes
- Theme lives in `src/index.css` (CSS variables) + `tailwind.config.js`.
- Brand accents: `primary` = orange, `accent` = blue, `success` = green.
- Product images use picsum.photos placeholders — swap for Supabase Storage URLs.
