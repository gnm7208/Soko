import { motion, useReducedMotion } from "motion/react";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export type OrderFilter = "all" | "progress" | "delivered";

interface OrderStatusTabsProps {
  value: OrderFilter;
  counts: Record<OrderFilter, number>;
  onChange: (value: OrderFilter) => void;
}

const labels: Record<OrderFilter, string> = {
  all: "All orders",
  progress: "In progress",
  delivered: "Delivered",
};

export function OrderStatusTabs({ value, counts, onChange }: OrderStatusTabsProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <Tabs value={value} onValueChange={(next) => onChange(next as OrderFilter)} className="w-full">
      <TabsList className="no-scrollbar h-auto w-full justify-start gap-6 overflow-x-auto rounded-none border-b border-border bg-transparent p-0">
        {(Object.keys(labels) as OrderFilter[]).map((filter) => (
          <TabsTrigger key={filter} value={filter} className="group relative h-auto shrink-0 rounded-none bg-transparent px-0 pb-3 pt-0 font-heading text-[13px] font-medium text-muted-foreground shadow-none hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:font-semibold data-[state=active]:text-foreground data-[state=active]:shadow-none">
            {labels[filter]} <span className="ml-1 text-[11px] text-muted-foreground">{counts[filter]}</span>
            {filter === value && (
              <motion.span
                layoutId="order-status-indicator"
                className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-primary"
                transition={shouldReduceMotion ? { duration: 0 } : { type: "spring", visualDuration: 0.3, bounce: 0.15 }}
              />
            )}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
