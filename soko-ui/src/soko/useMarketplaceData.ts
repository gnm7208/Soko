import { useEffect, useState } from "react";

import { api, COLD_START_TIMEOUT_MS } from "@/services/api";

import { categories as fallbackCategories, listings as fallbackListings, orders as fallbackOrders, shops as fallbackShops, type Category, type Listing, type NotificationItem, type Order, type Shop } from "./data";
import { flattenCategories, normalizeCategoryOptions, normalizeListing, normalizeNotification, normalizeOrder, normalizeShop } from "./normalizers";

interface MarketplaceData {
  listings: Listing[];
  shops: Shop[];
  categories: Category[];
  orders: Order[];
  notifications: NotificationItem[];
  loading: boolean;
  remote: boolean;
  listingsRemote: boolean;
  refresh: () => void;
}

const fallbackCategoryOptions: Category[] = fallbackCategories.map((category, index) => ({ ...category, id: `mock-category-${index}` }));

export function useMarketplaceData(searchQuery = "", isAuthenticated = false): MarketplaceData {
  const [refreshToken, setRefreshToken] = useState(0);
  const [data, setData] = useState<MarketplaceData>({ listings: fallbackListings, shops: fallbackShops, categories: fallbackCategoryOptions, orders: fallbackOrders, notifications: [], loading: true, remote: false, listingsRemote: false, refresh: () => undefined });
  const [remoteShops, setRemoteShops] = useState<Shop[]>(fallbackShops);
  const [categoryTree, setCategoryTree] = useState<ReturnType<typeof flattenCategories>>([]);

  useEffect(() => {
    let active = true;
    // Only the very first load gets the generous cold-start budget — a free-tier
    // backend asleep on first visit shouldn't silently look like "no data" and
    // fall back to placeholders. Later refreshes (post-checkout, shop-settings
    // save, etc.) hit an already-warm backend, so they keep the snappier default.
    const timeoutMs = refreshToken === 0 ? COLD_START_TIMEOUT_MS : undefined;
    const ordersRequest = isAuthenticated ? api.getOrders({ page: 1, per_page: 100 }) : Promise.reject(new Error("Authentication required"));
    const notificationsRequest = isAuthenticated ? api.getNotifications({ page: 1, per_page: 50 }) : Promise.reject(new Error("Authentication required"));
    Promise.allSettled([api.getShops({ page: 1, per_page: 100 }, { timeoutMs }), api.getCategories({ timeoutMs }), ordersRequest, notificationsRequest]).then(([shopsResult, categoriesResult, ordersResult, notificationsResult]) => {
      if (!active) return;
      const shops = shopsResult.status === "fulfilled" ? shopsResult.value.items.map((shop, index) => normalizeShop(shop, index)) : fallbackShops;
      const tree = categoriesResult.status === "fulfilled" ? categoriesResult.value : [];
      const shopMap = new Map(shops.map((shop) => [shop.id, shop]));
      const orders = ordersResult.status === "fulfilled" ? ordersResult.value.items.map((order, index) => normalizeOrder(order, shopMap, index)) : fallbackOrders;
      const notifications = notificationsResult.status === "fulfilled" ? notificationsResult.value.items.map(normalizeNotification) : [];
      setRemoteShops(shops.length > 0 ? shops : fallbackShops);
      setCategoryTree(flattenCategories(tree));
      setData((current) => ({ ...current, shops: shops.length > 0 ? shops : fallbackShops, categories: tree.length > 0 ? normalizeCategoryOptions(tree) : current.categories, orders: ordersResult.status === "fulfilled" ? orders : fallbackOrders, notifications, loading: false, remote: shopsResult.status === "fulfilled" || categoriesResult.status === "fulfilled" || ordersResult.status === "fulfilled" || notificationsResult.status === "fulfilled" }));
    });
    return () => { active = false; };
  }, [isAuthenticated, refreshToken]);

  useEffect(() => {
    let active = true;
    const timer = window.setTimeout(() => {
      const query = searchQuery.trim();
      const request = api.searchListings({ q: query || undefined, page: 1, per_page: 100, sort: "newest" });
      request.then((response) => {
        if (!active) return;
        const shopMap = new Map(remoteShops.map((shop) => [shop.id, shop]));
        const categoryMap = new Map(categoryTree.map((category) => [category.id, category.name]));
        const normalized = response.items.map((listing, index) => normalizeListing(listing, shopMap, categoryMap, index));
        setData((current) => ({ ...current, listings: normalized, loading: false, remote: true, listingsRemote: true }));
      }).catch(() => {
        if (active) setData((current) => ({ ...current, loading: false }));
      });
    }, searchQuery.trim() ? 250 : 0);
    return () => { active = false; window.clearTimeout(timer); };
  }, [categoryTree, remoteShops, searchQuery]);

  return { ...data, refresh: () => setRefreshToken((value) => value + 1) };
}
