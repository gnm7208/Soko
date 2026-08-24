import { ChevronRight, MapPin, Navigation, ShoppingBag, Truck } from "lucide-react";

import type { Order } from "./data";

interface DeliveryMapProps {
  order: Order;
}

export function DeliveryMap({ order }: DeliveryMapProps) {
  const delivered = order.status === "Delivered";
  return (
    <div className="rounded-xl bg-background p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-heading text-[11px] font-semibold uppercase tracking-[.14em] text-primary">{delivered ? "Delivery complete" : "Live delivery"}</p>
          <h3 className="mt-1 font-heading text-base font-semibold">{delivered ? "Delivered safely" : "Your order is on the way"}</h3>
        </div>
        <span className={`flex h-8 w-8 items-center justify-center rounded-full ${delivered ? "bg-success/15" : "bg-primary/15"}`}>
          {delivered ? <Navigation className="h-4 w-4 text-success" aria-hidden="true" /> : <Navigation className="h-4 w-4 text-primary" aria-hidden="true" />}
        </span>
      </div>

      <div className="mt-4 overflow-hidden rounded-xl border border-border bg-secondary/70">
        <div className="relative h-[138px] overflow-hidden soko-map-grid">
          <span className="absolute left-[-10px] top-[55px] h-3.5 w-[280px] rotate-[15deg] rounded-full bg-background/90 shadow-[0_0_0_1px_hsl(var(--border)/.4)]" aria-hidden="true" />
          <span className="absolute left-[110px] top-[5px] h-3.5 w-[170px] rotate-[79deg] rounded-full bg-background/90 shadow-[0_0_0_1px_hsl(var(--border)/.4)]" aria-hidden="true" />
          <span className="absolute left-[145px] top-[112px] h-3.5 w-[160px] rotate-[-32deg] rounded-full bg-background/90 shadow-[0_0_0_1px_hsl(var(--border)/.4)]" aria-hidden="true" />
          <span className="absolute left-[24%] top-[34%] flex h-7 w-7 items-center justify-center rounded-full border-4 border-background bg-accent shadow-sm">
            <MapPin className="h-3.5 w-3.5 text-background" aria-hidden="true" />
          </span>
          <span className="absolute right-[19%] top-[25%] flex h-8 w-8 items-center justify-center rounded-full border-4 border-background bg-primary shadow-sm">
            <ShoppingBag className="h-3.5 w-3.5 text-background" aria-hidden="true" />
          </span>
          <span className="absolute bottom-2 left-2 rounded-md bg-background/95 px-2 py-1 font-heading text-[9px] font-semibold text-muted-foreground shadow-sm">{delivered ? "Kilimani drop-off" : "Kilimani · Nairobi"}</span>
        </div>
        <div className="flex items-center gap-2 border-t border-border bg-card/80 px-3 py-2">
          <MapPin className="h-3 w-3 text-primary" aria-hidden="true" />
          <span className="font-body text-[10px] text-muted-foreground">Kilimani, Nairobi</span>
          <span className="ml-auto font-heading text-[10px] font-semibold text-foreground">{delivered ? "Delivered" : "1.2 km away"}</span>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <div className="flex items-center gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10"><Truck className="h-3.5 w-3.5 text-primary" aria-hidden="true" /></span>
          <div className="min-w-0 flex-1"><p className="font-heading text-[11px] font-semibold">{delivered ? "Order handed over" : "Rider is heading to you"}</p><p className="mt-0.5 font-body text-[10px] text-muted-foreground">{delivered ? "Delivered just now" : "M-Pesa payment confirmed"}</p></div>
          <span className={`font-heading text-[10px] font-semibold ${delivered ? "text-success" : "text-primary"}`}>{delivered ? "Done" : "12 min"}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-secondary"><Navigation className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" /></span>
          <div className="min-w-0 flex-1"><p className="font-heading text-[11px] font-semibold">{delivered ? "Delivery details" : "Need help with delivery?"}</p><p className="mt-0.5 font-body text-[10px] text-muted-foreground">{delivered ? "Leave a review for the shop" : `Chat with ${order.shopName}`}</p></div>
          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}
