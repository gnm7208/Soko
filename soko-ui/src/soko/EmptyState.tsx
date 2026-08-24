import { SearchX } from "lucide-react";

import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onReset: () => void;
}

export function EmptyState({ onReset }: EmptyStateProps) {
  return (
    <div className="rounded-[14px] border border-dashed border-border bg-card/50 px-6 py-12 text-center">
      <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-muted-foreground">
        <SearchX className="h-5 w-5" aria-hidden="true" />
      </span>
      <h3 className="mt-4 font-heading text-sm font-semibold">No listings match that search.</h3>
      <p className="mx-auto mt-1 max-w-sm font-body text-xs leading-relaxed text-muted-foreground">Try another product, shop, or category near Nairobi.</p>
      <Button type="button" variant="link" size="sm" className="mt-2 font-heading text-xs text-primary" onClick={onReset}>Clear search</Button>
    </div>
  );
}
