import { CheckCircle2, ClipboardCheck, PackageOpen, Truck } from "lucide-react";

import type { Order, OrderStatus } from "./data";

const steps: Array<{ label: OrderStatus; icon: typeof ClipboardCheck }> = [
  { label: "Confirmed", icon: ClipboardCheck },
  { label: "Preparing", icon: PackageOpen },
  { label: "Out for delivery", icon: Truck },
  { label: "Delivered", icon: CheckCircle2 },
];

interface OrderTrackerProps {
  order: Order;
  compact?: boolean;
}

export function OrderTracker({ order, compact = false }: OrderTrackerProps) {
  const currentIndex = steps.findIndex((step) => step.label === order.status);
  const progressLabel = order.status === "Delivered" ? "Complete" : `${Math.max(currentIndex, 0) + 1} of ${steps.length}`;

  return (
    <div className={compact ? "mt-4" : "mt-5"}>
      <div className="mb-2 flex items-center justify-between font-heading text-[10px] font-medium text-muted-foreground">
        <span>Order progress</span>
        <span>{progressLabel}</span>
      </div>
      <div className="flex items-start gap-0.5">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const complete = index <= currentIndex;
          return (
            <div key={step.label} className={`flex min-w-0 items-start ${index === steps.length - 1 ? "flex-none" : "flex-1"}`}>
              <div className="flex min-w-0 flex-col items-center gap-1.5">
                <span className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors duration-300 ${complete ? "bg-primary text-primary-foreground" : "border border-border bg-card text-muted-foreground"}`}>
                  <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                </span>
                <span className={`w-16 text-center font-heading text-[9px] leading-tight ${complete ? "font-semibold text-foreground" : "text-muted-foreground"}`}>{step.label}</span>
              </div>
              {index < steps.length - 1 && <span className={`mt-3.5 h-0.5 min-w-[18px] flex-1 transition-colors duration-300 ${index < currentIndex ? "bg-primary" : "bg-secondary"}`} aria-hidden="true" />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
