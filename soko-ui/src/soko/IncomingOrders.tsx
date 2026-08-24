import { Clock3, Inbox } from "lucide-react";
import { useState } from "react";

import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import type { Order, OrderStatus } from "./data";
import { money } from "./data";
import { StatusBadge } from "./Shared";

type SellerOrderFilter = "all" | OrderStatus;

interface IncomingOrdersProps {
  orders: Order[];
}

const filters: Array<{ value: SellerOrderFilter; label: string }> = [
  { value: "all", label: "All" },
  { value: "Preparing", label: "Preparing" },
  { value: "Out for delivery", label: "On the way" },
  { value: "Delivered", label: "Delivered" },
];

export function IncomingOrders({ orders }: IncomingOrdersProps) {
  const [filter, setFilter] = useState<SellerOrderFilter>("all");
  const visibleOrders = filter === "all" ? orders : orders.filter((order) => order.status === filter);

  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><div className="flex items-center justify-between"><h2 className="font-heading text-base font-semibold">Incoming orders</h2><span className="rounded-full bg-primary/10 px-2 py-1 font-heading text-[10px] font-semibold text-primary">7 open</span></div><p className="mt-0.5 font-body text-xs text-muted-foreground">Keep your customers moving</p></div>
      <Tabs value={filter} onValueChange={(value) => setFilter(value as SellerOrderFilter)}><TabsList className="h-auto w-full justify-start gap-1 overflow-x-auto rounded-none border-b border-border bg-transparent px-3 py-2"><span className="sr-only">Order status filters</span>{filters.map((item) => <TabsTrigger key={item.value} value={item.value} className="shrink-0 rounded-full px-2.5 py-1.5 font-heading text-[10px] font-medium text-muted-foreground shadow-none data-[state=active]:bg-foreground data-[state=active]:text-background data-[state=active]:shadow-none">{item.label}</TabsTrigger>)}</TabsList></Tabs>
      {visibleOrders.length === 0 ? <div className="px-4 py-10 text-center"><Inbox className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No orders in this view</p><p className="mt-1 font-body text-[11px] text-muted-foreground">You’re all caught up.</p></div> : <div className="divide-y divide-border">{visibleOrders.map((order) => <div key={order.id} className="px-4 py-3.5"><div className="flex items-start gap-3"><img src={order.image} alt={order.listingTitle} loading="lazy" decoding="async" className="h-10 w-10 shrink-0 rounded-lg object-cover" /><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-2"><div className="min-w-0"><p className="font-heading text-xs font-semibold">{order.id}</p><p className="mt-1 truncate font-body text-[11px] text-muted-foreground">{order.listingTitle}</p></div><StatusBadge status={order.status} /></div><div className="mt-2 flex items-center justify-between gap-2"><span className="font-body text-[10px] text-muted-foreground">{order.payment} · {order.date}</span><span className="font-heading text-xs font-semibold text-primary">{money(order.total)}</span></div>{order.eta && <p className="mt-2 inline-flex items-center gap-1 font-heading text-[10px] font-semibold text-primary"><Clock3 className="h-3 w-3" aria-hidden="true" />{order.eta}</p>}</div></div></div>)}</div>}
    </Card>
  );
}
