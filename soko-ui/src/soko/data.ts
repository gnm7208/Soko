// Soko mock data + shared types. Replace the data adapter with the Flask API when auth is connected.
export type Role = "buyer" | "retailer";
export type MarketplaceMode = "buyer" | "seller" | "admin";
export type Screen = "browse" | "listing" | "shop" | "chat" | "checkout" | "orders" | "seller";
export type OrderStatus = "Confirmed" | "Preparing" | "Out for delivery" | "Delivered";

export interface Category {
  id: string;
  name: string;
  icon: string;
}

export interface NotificationItem {
  id: string;
  type: string;
  title: string;
  body: string;
  read: boolean;
  createdAt?: string;
}
export type PaymentMethod = "M-Pesa" | "Card" | "Cash on delivery";
export type DeliveryMethod = "delivery" | "pickup";

export interface Shop {
  id: string; name: string; category: string; rating: number; reviews: number;
  distanceKm: number; address: string; verified: boolean; cover: string; logo: string;
  eta: string; deliveryFee: number;
}

export interface Listing {
  id: string; shopId: string; title: string; price: number; currency: string;
  category: string; condition: "New" | "Used"; image: string; rating: number;
  sold: number; featured?: boolean; distanceKm: number;
}

export interface SellerListing extends Listing {
  status: "Active" | "Draft";
}

export interface Order {
  id: string; listingTitle: string; shopName: string; total: number; currency: string;
  status: OrderStatus; payment: PaymentMethod; date: string; image: string; eta?: string;
}

export interface Message { id: string; from: "me" | "them"; text: string; time: string; }

export const CURRENCY = "KSh";

export const categories = [
  { name: "Electronics", icon: "Smartphone" },
  { name: "Fashion", icon: "Shirt" },
  { name: "Home", icon: "Sofa" },
  { name: "Groceries", icon: "Apple" },
  { name: "Beauty", icon: "Sparkles" },
  { name: "Vehicles", icon: "Car" },
  { name: "Services", icon: "Wrench" },
  { name: "Kids", icon: "Baby" },
] as const;

export const shops: Shop[] = [
  { id: "s1", name: "Mama Njeri Electronics", category: "Electronics", rating: 4.8, reviews: 214, distanceKm: 1.2, address: "Biashara St, Nairobi CBD", verified: true, cover: "https://picsum.photos/seed/sokoshop1/800/300", logo: "https://picsum.photos/seed/logo1/80/80", eta: "25–35 min", deliveryFee: 150 },
  { id: "s2", name: "Kilimani Fresh Grocers", category: "Groceries", rating: 4.6, reviews: 98, distanceKm: 2.6, address: "Argwings Kodhek Rd", verified: true, cover: "https://picsum.photos/seed/sokoshop2/800/300", logo: "https://picsum.photos/seed/logo2/80/80", eta: "15–25 min", deliveryFee: 100 },
  { id: "s3", name: "Threadline Fashion House", category: "Fashion", rating: 4.9, reviews: 331, distanceKm: 3.9, address: "Westgate Mall, Westlands", verified: true, cover: "https://picsum.photos/seed/sokoshop3/800/300", logo: "https://picsum.photos/seed/logo3/80/80", eta: "30–45 min", deliveryFee: 200 },
];

export const listings: Listing[] = [
  { id: "l1", shopId: "s1", title: "Wireless Noise-Cancelling Headphones", price: 6800, currency: CURRENCY, category: "Electronics", condition: "New", image: "https://picsum.photos/seed/head/500/500", rating: 4.7, sold: 142, featured: true, distanceKm: 1.2 },
  { id: "l2", shopId: "s3", title: "Handwoven Cotton Kitenge Dress", price: 3500, currency: CURRENCY, category: "Fashion", condition: "New", image: "https://picsum.photos/seed/dress/500/500", rating: 4.9, sold: 87, featured: true, distanceKm: 3.9 },
  { id: "l3", shopId: "s2", title: "Fresh Produce Basket (Weekly)", price: 1200, currency: CURRENCY, category: "Groceries", condition: "New", image: "https://picsum.photos/seed/basket/500/500", rating: 4.6, sold: 260, distanceKm: 2.6 },
  { id: "l4", shopId: "s1", title: "Smart LED TV 43\" 4K", price: 28900, currency: CURRENCY, category: "Electronics", condition: "New", image: "https://picsum.photos/seed/tv/500/500", rating: 4.5, sold: 34, distanceKm: 1.2 },
  { id: "l5", shopId: "s3", title: "Leather Ankle Boots", price: 4900, currency: CURRENCY, category: "Fashion", condition: "New", image: "https://picsum.photos/seed/boots/500/500", rating: 4.8, sold: 51, distanceKm: 3.9 },
  { id: "l6", shopId: "s2", title: "Cold-Pressed Juice 6-Pack", price: 1800, currency: CURRENCY, category: "Groceries", condition: "New", image: "https://picsum.photos/seed/juice/500/500", rating: 4.4, sold: 120, distanceKm: 2.6 },
  { id: "l7", shopId: "s1", title: "Bluetooth Party Speaker", price: 5400, currency: CURRENCY, category: "Electronics", condition: "New", image: "https://picsum.photos/seed/speaker/500/500", rating: 4.6, sold: 76, distanceKm: 1.2 },
  { id: "l8", shopId: "s3", title: "Beaded Maasai Handbag", price: 2600, currency: CURRENCY, category: "Fashion", condition: "New", image: "https://picsum.photos/seed/bag/500/500", rating: 5.0, sold: 43, featured: true, distanceKm: 3.9 },
];

export const orders: Order[] = [
  { id: "SOKO-2481", listingTitle: "Wireless Noise-Cancelling Headphones", shopName: "Mama Njeri Electronics", total: 6950, currency: CURRENCY, status: "Out for delivery", payment: "M-Pesa", date: "Today, 14:20", image: "https://picsum.photos/seed/head/120/120", eta: "Arriving in ~12 min" },
  { id: "SOKO-2470", listingTitle: "Fresh Produce Basket (Weekly)", shopName: "Kilimani Fresh Grocers", total: 1300, currency: CURRENCY, status: "Delivered", payment: "Card", date: "Yesterday, 09:05", image: "https://picsum.photos/seed/basket/120/120" },
  { id: "SOKO-2455", listingTitle: "Beaded Maasai Handbag", shopName: "Threadline Fashion House", total: 2800, currency: CURRENCY, status: "Preparing", payment: "Cash on delivery", date: "Today, 11:48", image: "https://picsum.photos/seed/bag/120/120", eta: "Preparing for dispatch" },
];

export const messages: Message[] = [
  { id: "m1", from: "them", text: "Hi! Thanks for your interest in the headphones 🎧", time: "14:02" },
  { id: "m2", from: "me", text: "Are they available in black? And do you deliver to Kilimani?", time: "14:03" },
  { id: "m3", from: "them", text: "Yes, black is in stock. Delivery to Kilimani is KSh 150, arrives in ~30 min.", time: "14:04" },
  { id: "m4", from: "me", text: "Perfect, I'll place the order now.", time: "14:05" },
];

export const money = (n: number, c = CURRENCY) => `${c} ${n.toLocaleString("en-KE")}`;
