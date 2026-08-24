import { Button } from "@/components/ui/button";

import type { MarketplaceMode } from "./data";

interface ModeToggleProps {
  mode: MarketplaceMode;
  onChange: (mode: MarketplaceMode) => void;
}

export function ModeToggle({ mode, onChange }: ModeToggleProps) {
  return (
    <div className="flex items-center rounded-full border border-border bg-card p-0.5 text-xs" aria-label="Choose marketplace mode">
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => onChange("buyer")}
        className={`h-auto rounded-full px-3.5 py-1.5 font-heading text-xs font-semibold ${mode === "buyer" ? "bg-foreground text-background hover:bg-foreground/90 hover:text-background" : "text-muted-foreground hover:bg-secondary hover:text-foreground"}`}
        aria-pressed={mode === "buyer"}
      >
        Buy
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={() => onChange("seller")}
        className={`h-auto rounded-full px-3.5 py-1.5 font-heading text-xs font-semibold ${mode === "seller" ? "bg-foreground text-background hover:bg-foreground/90 hover:text-background" : "text-muted-foreground hover:bg-secondary hover:text-foreground"}`}
        aria-pressed={mode === "seller"}
      >
        Sell
      </Button>
    </div>
  );
}
