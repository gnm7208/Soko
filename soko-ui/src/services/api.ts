import type { DeliveryMethod, PaymentMethod } from "@/soko/data";

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? "/api/v1").replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 8_000;
// Free-tier hosts (e.g. Render) spin down after inactivity and can take
// 30-50s to wake on the first request. The app's very first data fetch on
// load gets this much longer budget so a cold backend doesn't silently look
// like "no data" and fall back to placeholders — later interactions keep the
// snappier default above.
const COLD_START_TIMEOUT_MS = 45_000;

export interface ApiErrorPayload {
  error?: string;
  message?: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly payload?: ApiErrorPayload;

  constructor(message: string, status: number, payload?: ApiErrorPayload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export interface ApiListing {
  id: string;
  shop_id: string;
  title: string;
  description?: string | null;
  price: number;
  currency?: string;
  category_id?: string | null;
  condition?: "new" | "used" | string;
  stock?: number;
  status?: string;
  image_url?: string | null;
  location?: string | null;
  lat?: number | null;
  lng?: number | null;
  created_at?: string;
}

export interface ApiShop {
  id: string;
  owner_id?: string;
  name: string;
  description?: string | null;
  logo_url?: string | null;
  cover_url?: string | null;
  category: string;
  address?: string | null;
  lat?: number | null;
  lng?: number | null;
  status?: string;
  rating_avg?: number;
  rating_count?: number;
  created_at?: string;
}

export interface ApiCategory {
  id: string;
  name: string;
  slug: string;
  parent_id?: string | null;
  icon?: string | null;
  children?: ApiCategory[];
}

export interface ApiOrder {
  id: string;
  buyer_id?: string;
  shop_id: string;
  status: string;
  total: number;
  currency?: string;
  payment_method: "stripe" | "flutterwave" | "paystack" | "cash" | string;
  payment_status?: string;
  delivery_method?: DeliveryMethod;
  delivery_address?: string | null;
  delivery_lat?: number | null;
  delivery_lng?: number | null;
  rider_id?: string | null;
  created_at?: string;
}

export interface ApiMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  body: string;
  read?: boolean;
  created_at?: string;
}

export interface ApiConversation {
  id: string;
  shop_id: string;
  buyer_id: string;
  listing_id?: string | null;
  last_message?: string | null;
  unread_count?: number;
  created_at?: string;
  messages?: ApiMessage[];
}

export interface ApiNotification {
  id: string;
  user_id: string;
  type: "order" | "message" | "promotion" | "system" | string;
  title?: string | null;
  body?: string | null;
  read: boolean;
  created_at?: string;
}

export interface ApiWallet {
  id: string;
  user_id: string;
  balance: number;
  currency: string;
  created_at?: string;
}

export interface ApiPayment {
  id: string;
  order_id: string;
  provider: string;
  provider_ref?: string | null;
  amount: number;
  status: string;
  created_at?: string;
}

export interface ApiProfile {
  id: string;
  user_id?: string;
  role: "buyer" | "retailer" | "rider" | "admin";
  full_name: string;
  phone?: string | null;
  avatar_url?: string | null;
}

export interface ApiAdminUser {
  id: string;
  user_id: string;
  full_name: string;
  phone?: string | null;
  avatar_url?: string | null;
  role: string;
  created_at?: string;
}

export interface ApiDispute {
  id: string;
  order_id: string;
  raised_by: string;
  reason: string;
  status: "open" | "resolved" | "rejected" | string;
  resolution_note?: string | null;
  resolved_by?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ApiPayoutRequest {
  id: string;
  wallet_id: string;
  amount: number;
  status: string;
  ref?: string | null;
  created_at?: string;
  owner_name?: string | null;
}

export interface ApiMetrics {
  total_orders: number;
  total_revenue: number;
  total_shops: number;
  total_users: number;
  total_listings: number;
  period?: string | null;
}

interface PaginatedResponse<T> {
  items: T[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

interface RequestOptions extends RequestInit {
  query?: Record<string, string | number | undefined | null>;
  timeoutMs?: number;
}

let accessToken: string | undefined;

export function setAccessToken(token?: string) {
  accessToken = token;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { query, headers, body, timeoutMs, ...init } = options;
  const url = API_BASE_URL.startsWith("http")
    ? new URL(`${API_BASE_URL}${path}`)
    : new URL(`${API_BASE_URL}${path}`, window.location.origin);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  });

  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs ?? REQUEST_TIMEOUT_MS);
  const requestHeaders = new Headers(headers);
  if (body && !requestHeaders.has("Content-Type")) requestHeaders.set("Content-Type", "application/json");
  if (accessToken && !requestHeaders.has("Authorization")) requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  const isUnsafeMethod = ["POST", "PUT", "PATCH", "DELETE"].includes((init.method ?? "GET").toUpperCase());
  if (isUnsafeMethod && !requestHeaders.has("X-CSRF-TOKEN")) {
    const csrfToken = readCookie("csrf_access_token");
    if (csrfToken) requestHeaders.set("X-CSRF-TOKEN", csrfToken);
  }

  try {
    const response = await fetch(url, { ...init, body, headers: requestHeaders, credentials: "include", signal: controller.signal });
    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json") ? await response.json() : undefined;
    if (!response.ok) {
      const errorPayload = (payload ?? {}) as ApiErrorPayload;
      throw new ApiError(errorPayload.message ?? "Request failed", response.status, errorPayload);
    }
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") throw new ApiError("The Soko API took too long to respond", 408);
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}

function jsonBody(value: unknown): RequestInit {
  return { method: "POST", body: JSON.stringify(value) };
}

async function requestMultipart<T>(path: string, formData: FormData): Promise<T> {
  const url = API_BASE_URL.startsWith("http")
    ? new URL(`${API_BASE_URL}${path}`)
    : new URL(`${API_BASE_URL}${path}`, window.location.origin);

  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  const requestHeaders = new Headers();
  if (accessToken) requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  const csrfToken = readCookie("csrf_access_token");
  if (csrfToken) requestHeaders.set("X-CSRF-TOKEN", csrfToken);

  try {
    const response = await fetch(url, { method: "POST", body: formData, headers: requestHeaders, credentials: "include", signal: controller.signal });
    const contentType = response.headers.get("content-type") ?? "";
    const payload = contentType.includes("application/json") ? await response.json() : undefined;
    if (!response.ok) {
      const errorPayload = (payload ?? {}) as ApiErrorPayload;
      throw new ApiError(errorPayload.message ?? "Request failed", response.status, errorPayload);
    }
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") throw new ApiError("The Soko API took too long to respond", 408);
    throw error;
  } finally {
    window.clearTimeout(timer);
  }
}

function readCookie(name: string) {
  const prefix = `${name}=`;
  return document.cookie.split("; ").find((cookie) => cookie.startsWith(prefix))?.slice(prefix.length);
}

export const api = {
  getMe: () => request<ApiProfile>("/auth/me"),
  register: async (payload: { email: string; password: string; full_name: string; phone?: string; role?: "buyer" | "retailer" }) => {
    const result = await request<{ access_token?: string; refresh_token?: string; profile: ApiProfile }>("/auth/register", { ...jsonBody(payload) });
    setAccessToken(result.access_token);
    return result;
  },
  login: async (email: string, password: string) => {
    const result = await request<{ access_token?: string; refresh_token?: string; profile: ApiProfile }>("/auth/login", { ...jsonBody({ email, password }) });
    setAccessToken(result.access_token);
    return result;
  },
  logout: async () => {
    const result = await request<{ message: string }>("/auth/logout", { method: "POST" });
    setAccessToken(undefined);
    return result;
  },
  getListings: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiListing>>("/listings", { query }),
  searchListings: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiListing>>("/search", { query }),
  getListing: (id: string) => request<ApiListing>(`/listings/${id}`),
  createListing: (payload: { title: string; price: number; category_id?: string; condition?: "new" | "used"; stock?: number; description?: string }) => request<ApiListing>("/listings", { method: "POST", body: JSON.stringify(payload) }),
  updateListing: (id: string, payload: Partial<{ title: string; price: number; category_id: string; condition: "new" | "used"; stock: number; description: string }>) => request<ApiListing>(`/listings/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  getShops: (query: Record<string, string | number | undefined | null> = {}, options?: { timeoutMs?: number }) => request<PaginatedResponse<ApiShop>>("/shops", { query, timeoutMs: options?.timeoutMs }),
  getShop: (id: string) => request<ApiShop>(`/shops/${id}`),
  getCategories: (options?: { timeoutMs?: number }) => request<ApiCategory[]>("/categories", { timeoutMs: options?.timeoutMs }),
  toggleFavorite: (listingId: string) => request<{ favorited: boolean }>(`/favorites/${listingId}`, { method: "POST" }),
  getFavorites: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiListing>>("/favorites", { query }),
  getOrders: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiOrder>>("/orders", { query }),
  getOrder: (id: string) => request<ApiOrder>(`/orders/${id}`),
  createOrder: (payload: { shop_id: string; items: Array<{ listing_id: string; qty: number }>; delivery_method: DeliveryMethod; delivery_address?: string; payment_method: "stripe" | "flutterwave" | "paystack" | "cash" }) => request<ApiOrder>("/orders", { method: "POST", body: JSON.stringify(payload) }),
  createPaymentIntent: (payload: { order_id: string; provider: "stripe" | "flutterwave" | "paystack" }) => request<ApiPayment>("/payments/intent", { method: "POST", body: JSON.stringify(payload) }),
  getConversations: () => request<ApiConversation[]>("/conversations"),
  getConversation: (id: string) => request<ApiConversation>(`/conversations/${id}`),
  startConversation: (payload: { shop_id: string; listing_id?: string; body: string }) => request<ApiConversation>("/conversations", { ...jsonBody(payload) }),
  sendMessage: (conversationId: string, body: string) => request<ApiMessage>(`/conversations/${conversationId}/messages`, { ...jsonBody({ body }) }),
  getNotifications: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiNotification>>("/notifications", { query }),
  markNotificationRead: (id: string) => request<ApiNotification>(`/notifications/${id}/read`, { method: "PATCH" }),
  markAllNotificationsRead: () => request<{ message: string }>("/notifications/mark-all-read", { method: "POST" }),
  getWallet: () => request<ApiWallet>("/wallets/me"),
  requestPayout: (amount: number, note?: string) => request<{ id: string; wallet_id: string; amount: number; status: string; note?: string }>("/wallets/payout-request", { ...jsonBody({ amount, note }) }),
  updateProfile: (payload: Partial<{ full_name: string; phone: string }>) => request<ApiProfile>("/auth/me", { method: "PATCH", body: JSON.stringify(payload) }),
  uploadAvatar: (file: File) => { const form = new FormData(); form.append("file", file); return requestMultipart<ApiProfile>("/auth/me/avatar", form); },
  updateShop: (id: string, payload: Partial<{ name: string; description: string; category: string; address: string; lat: number; lng: number; logo_url: string; cover_url: string }>) => request<ApiShop>(`/shops/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  uploadShopImage: (shopId: string, file: File, kind: "logo" | "cover") => { const form = new FormData(); form.append("file", file); form.append("kind", kind); return requestMultipart<ApiShop>(`/shops/${shopId}/images`, form); },
  createDispute: (payload: { order_id: string; reason: string }) => request<ApiDispute>("/disputes", { ...jsonBody(payload) }),
  getMyDisputes: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiDispute>>("/disputes/mine", { query }),
  getAdminMetrics: () => request<ApiMetrics>("/admin/metrics"),
  getAdminShops: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiShop>>("/admin/shops", { query }),
  approveShop: (id: string) => request<{ id: string; name: string; status: string }>(`/admin/shops/${id}/approve`, { method: "PATCH" }),
  suspendShop: (id: string) => request<{ id: string; name: string; status: string }>(`/admin/shops/${id}/suspend`, { method: "PATCH" }),
  getAdminUsers: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiAdminUser>>("/admin/users", { query }),
  getAdminListings: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiListing>>("/admin/listings", { query }),
  adminUpdateListing: (id: string, payload: Partial<{ title: string; status: string }>) => request<{ id: string; title: string; status: string }>(`/admin/listings/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  getAdminPayouts: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiPayoutRequest>>("/admin/payouts", { query }),
  updateAdminPayout: (id: string, status: string) => request<{ id: string; wallet_id: string; type: string; amount: number; status: string }>(`/admin/payouts/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
  getAdminDisputes: (query: Record<string, string | number | undefined | null> = {}) => request<PaginatedResponse<ApiDispute>>("/admin/disputes", { query }),
  resolveDispute: (id: string, payload: { status: "resolved" | "rejected"; resolution_note?: string }) => request<ApiDispute>(`/admin/disputes/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
};

export type { PaymentMethod };
export { COLD_START_TIMEOUT_MS };
