import type { ApiCategory, ApiListing, ApiMessage, ApiNotification, ApiOrder, ApiShop } from "@/services/api";

import { categories as fallbackCategories, CURRENCY, listings as fallbackListings, money, orders as fallbackOrders, shops as fallbackShops, type Category, type Listing, type Message, type NotificationItem, type Order, type Shop } from "./data";

const imageSeeds = ["head", "dress", "basket", "tv", "boots", "juice", "speaker", "bag"];

export function flattenCategories(tree: ApiCategory[]): ApiCategory[] {
  return tree.flatMap((category) => [category, ...flattenCategories(category.children ?? [])]);
}

export function normalizeCategoryOptions(tree: ApiCategory[]): Category[] {
  const flat = flattenCategories(tree);
  return flat.length > 0 ? flat.map((category, index) => ({ name: category.name, icon: category.icon ?? fallbackCategories[index % fallbackCategories.length]?.icon ?? "Sparkles", id: category.id })) : fallbackCategories.map((category, index) => ({ ...category, id: `mock-category-${index}` }));
}

function displayCurrency(currency?: string) {
  return currency === "KES" || currency === "KSh" || !currency ? CURRENCY : currency;
}

function displayCondition(condition?: string): Listing["condition"] {
  return condition?.toLowerCase() === "used" ? "Used" : "New";
}

function findFallbackShop(index: number, rawId?: string) {
  return fallbackShops.find((shop) => shop.id === rawId) ?? fallbackShops[index % fallbackShops.length] ?? fallbackShops[0];
}

export function normalizeShop(raw: ApiShop, index = 0): Shop {
  const fallback = findFallbackShop(index, raw.id);
  return {
    ...fallback,
    id: raw.id,
    name: raw.name || fallback.name,
    category: raw.category || fallback.category,
    rating: raw.rating_avg ?? fallback.rating,
    reviews: raw.rating_count ?? fallback.reviews,
    address: raw.address || fallback.address,
    verified: raw.status ? raw.status === "approved" || raw.status === "active" : fallback.verified,
    logo: raw.logo_url || fallback.logo,
    cover: raw.cover_url || fallback.cover,
  };
}

export function normalizeListing(raw: ApiListing, shopMap: Map<string, Shop>, categoryMap: Map<string, string>, index = 0): Listing {
  const fallback = fallbackListings[index % fallbackListings.length] ?? fallbackListings[0];
  const shop = shopMap.get(raw.shop_id) ?? findFallbackShop(index, raw.shop_id);
  return {
    ...fallback,
    id: raw.id,
    shopId: raw.shop_id,
    title: raw.title || fallback.title,
    price: raw.price ?? fallback.price,
    currency: displayCurrency(raw.currency),
    category: categoryMap.get(raw.category_id ?? "") ?? shop.category ?? fallback.category,
    condition: displayCondition(raw.condition),
    image: raw.image_url || `https://picsum.photos/seed/${imageSeeds[index % imageSeeds.length]}/500/500`,
    rating: shop.rating || fallback.rating,
    sold: fallback.sold,
    featured: fallback.featured ?? index < 3,
    distanceKm: fallback.distanceKm,
  };
}

function normalizeOrderStatus(status: string): Order["status"] {
  if (status === "preparing") return "Preparing";
  if (status === "out_for_delivery") return "Out for delivery";
  if (status === "delivered") return "Delivered";
  return "Confirmed";
}

function displayPayment(provider?: string): Order["payment"] {
  if (provider === "cash") return "Cash on delivery";
  if (provider === "flutterwave" || provider === "paystack") return "M-Pesa";
  return "Card";
}

function displayDate(value?: string, fallback = "Recently") {
  if (!value) return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fallback;
  return date.toLocaleString("en-KE", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export function normalizeOrder(raw: ApiOrder, shopMap: Map<string, Shop>, index = 0): Order {
  const fallback = fallbackOrders.find((order) => order.id === raw.id) ?? fallbackOrders[index % fallbackOrders.length] ?? fallbackOrders[0];
  const shop = shopMap.get(raw.shop_id);
  const status = normalizeOrderStatus(raw.status);
  return {
    ...fallback,
    id: raw.id,
    listingTitle: fallback.listingTitle,
    shopName: shop?.name ?? fallback.shopName,
    total: raw.total ?? fallback.total,
    currency: displayCurrency(raw.currency),
    status,
    payment: displayPayment(raw.payment_method),
    date: displayDate(raw.created_at, fallback.date),
    eta: status === "Delivered" ? undefined : fallback.eta,
  };
}

export function normalizeNotification(raw: ApiNotification): NotificationItem {
  return { id: raw.id, type: raw.type, title: raw.title ?? "Soko update", body: raw.body ?? "You have a new marketplace update.", read: raw.read, createdAt: raw.created_at };
}

export function normalizeMessage(raw: ApiMessage, currentUserId?: string): Message {
  return { id: raw.id, from: currentUserId && raw.sender_id === currentUserId ? "me" : "them", text: raw.body, time: displayDate(raw.created_at, "now") };
}

export function formatWalletBalance(balance: number, currency?: string) {
  return money(balance, displayCurrency(currency));
}
