import { Check, RotateCcw, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";

export type QuickFilter = "near" | "new" | null;

interface FilterPanelProps {
  quickFilter: QuickFilter;
  onChange: (filter: QuickFilter) => void;
  onReset: () => void;
}

export function FilterPanel({ quickFilter, onChange, onReset }: FilterPanelProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-card/70 p-2.5">
      <span className="inline-flex items-center gap-1.5 px-1.5 font-body text-[11px] text-muted-foreground">
        <SlidersHorizontal className="h-3.5 w-3.5" aria-hidden="true" />
        Quick filters
      </span>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className={`h-8 rounded-full text-[10px] ${quickFilter === "near" ? "border-primary bg-primary/10 text-primary hover:bg-primary/15" : "bg-card"}`}
        onClick={() => onChange(quickFilter === "near" ? null : "near")}
        aria-pressed={quickFilter === "near"}
      >
        {quickFilter === "near" && <Check className="h-3 w-3" aria-hidden="true" />}
        Within 5 km
      </Button>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className={`h-8 rounded-full text-[10px] ${quickFilter === "new" ? "border-primary bg-primary/10 text-primary hover:bg-primary/15" : "bg-card"}`}
        onClick={() => onChange(quickFilter === "new" ? null : "new")}
        aria-pressed={quickFilter === "new"}
      >
        {quickFilter === "new" && <Check className="h-3 w-3" aria-hidden="true" />}
        New items
      </Button>
      <Button type="button" variant="ghost" size="sm" className="h-8 gap-1.5 text-[10px] text-muted-foreground" onClick={onReset}>
        <RotateCcw className="h-3 w-3" aria-hidden="true" />
        Reset
      </Button>
    </div>
  );
}
