import type { ReactNode } from "react";
import { Star } from "lucide-react";

import type { OrderStatus } from "./data";

export function Stars({ value, size = 14 }: { value: number; size?: number }) {
  return (
    <span className="inline-flex items-center gap-1" aria-label={`${value.toFixed(1)} out of 5 stars`}>
      <span className="inline-flex" aria-hidden="true">
        {[0, 1, 2, 3, 4].map((index) => (
          <Star
            key={index}
            size={size}
            className={index < Math.round(value) ? "fill-primary text-primary" : "text-border"}
          />
        ))}
      </span>
      <span className="text-xs text-muted-foreground">{value.toFixed(1)}</span>
    </span>
  );
}

const statusStyles: Record<OrderStatus, string> = {
  Confirmed: "bg-secondary text-foreground",
  Preparing: "border-accent/30 bg-accent/15 text-accent",
  "Out for delivery": "border-primary/30 bg-primary/15 text-primary",
  Delivered: "border-success/30 bg-success/15 text-success",
};

export function StatusBadge({ status }: { status: OrderStatus }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border border-transparent px-2.5 py-0.5 text-xs font-medium ${statusStyles[status]}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-70" aria-hidden="true" />
      {status}
    </span>
  );
}

export function SectionTitle({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <h2 className="font-heading text-xl font-semibold">{children}</h2>
      {action}
    </div>
  );
}

export function Eyebrow({ children, tone = "primary" }: { children: ReactNode; tone?: "primary" | "success" }) {
  return (
    <p className={`font-heading text-[11px] font-semibold uppercase tracking-[.16em] ${tone === "success" ? "text-success" : "text-primary"}`}>
      {children}
    </p>
  );
}
