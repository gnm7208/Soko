import { ArrowLeft, ArrowUpRight, SearchX, ShoppingBag } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";

import { orders as fallbackOrders, type Order } from "./data";
import { Eyebrow } from "./Shared";
import { OrderCard } from "./OrderCard";
import { OrderStatusTabs, type OrderFilter } from "./OrderStatusTabs";

interface OrdersProps {
  searchQuery: string;
  orders?: Order[];
  onBrowse: () => void;
}

export function Orders({ searchQuery, orders = fallbackOrders, onBrowse }: OrdersProps) {
  const [orderItems, setOrderItems] = useState<Order[]>(() => orders.map((order) => ({ ...order })));
  const [filter, setFilter] = useState<OrderFilter>("all");
  const [expandedIds, setExpandedIds] = useState<string[]>([orders[0]?.id ?? fallbackOrders[0].id]);

  useEffect(() => {
    setOrderItems(orders.map((order) => ({ ...order })));
  }, [orders]);

  const counts = useMemo(() => ({ all: orderItems.length, progress: orderItems.filter((order) => order.status !== "Delivered").length, delivered: orderItems.filter((order) => order.status === "Delivered").length }), [orderItems]);
  const visibleOrders = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return orderItems.filter((order) => {
      const matchesFilter = filter === "all" || (filter === "delivered" ? order.status === "Delivered" : order.status !== "Delivered");
      const searchable = `${order.id} ${order.listingTitle} ${order.shopName} ${order.status} ${order.payment}`.toLowerCase();
      return matchesFilter && (!query || searchable.includes(query));
    });
  }, [filter, orderItems, searchQuery]);

  const toggleOrder = (id: string) => setExpandedIds((ids) => ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id]);
  const markDelivered = (id: string) => setOrderItems((current) => current.map((order) => order.id === id ? { ...order, status: "Delivered", eta: undefined } : order));

  return (
    <div className="mx-auto max-w-[1040px] px-4 pb-16 pt-8 sm:px-6 sm:pt-10"><div className="mb-8 flex flex-wrap items-end justify-between gap-4"><div><Eyebrow>Your Soko activity</Eyebrow><h1 className="mt-2 font-heading text-[32px] font-bold leading-tight tracking-[-.035em]">My orders</h1><p className="mt-2 font-body text-sm text-muted-foreground">{searchQuery ? `${visibleOrders.length} ${visibleOrders.length === 1 ? "order" : "orders"} matching “${searchQuery}”.` : "Keep an eye on your deliveries, from checkout to doorstep."}</p></div><Button type="button" variant="outline" className="h-10 gap-2 rounded-lg bg-card font-heading text-xs" onClick={onBrowse}><ArrowLeft className="h-4 w-4 text-primary" aria-hidden="true" /> Back to browse</Button></div><div className="mb-7"><OrderStatusTabs value={filter} counts={counts} onChange={setFilter} /></div>{visibleOrders.length === 0 ? <div className="rounded-2xl border border-dashed border-border bg-card/50 px-6 py-16 text-center"><span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-muted-foreground"><SearchX className="h-5 w-5" aria-hidden="true" /></span><h2 className="mt-4 font-heading text-lg font-semibold">No orders found</h2><p className="mt-1 font-body text-sm text-muted-foreground">Try another search or switch to a different status.</p><Button type="button" variant="link" size="sm" className="mt-2 font-heading text-xs text-primary" onClick={() => setFilter("all")}>Show all orders</Button></div> : <section className="space-y-4" aria-live="polite">{visibleOrders.map((order, index) => <OrderCard key={order.id} order={order} featured={index === 0 && order.id === orders[0]?.id} expanded={expandedIds.includes(order.id)} onToggle={toggleOrder} onDeliver={markDelivered} />)}</section>}<div className="mt-9 flex flex-col items-start justify-between gap-4 rounded-2xl bg-foreground px-6 py-5 text-background sm:flex-row sm:items-center"><div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/20 text-primary"><ShoppingBag className="h-4 w-4" aria-hidden="true" /></span><div><p className="font-heading text-sm font-semibold">Need something else?</p><p className="mt-0.5 font-body text-xs text-background/60">Discover trusted retailers near you.</p></div></div><Button type="button" className="gap-1.5 rounded-lg font-heading text-xs" onClick={onBrowse}>Browse marketplace <ArrowUpRight className="h-3.5 w-3.5" aria-hidden="true" /></Button></div></div>
  );
}
