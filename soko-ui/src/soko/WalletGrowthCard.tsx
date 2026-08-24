import { ArrowUpRight, WalletCards } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { money } from "./data";

interface WalletGrowthCardProps {
  balance: number;
  onRequestPayout: () => Promise<void>;
}

export function WalletGrowthCard({ balance, onRequestPayout }: WalletGrowthCardProps) {
  const requestPayout = async () => {
    try {
      await onRequestPayout();
      toast.success("Payout request started — we’ll confirm it shortly");
    } catch {
      toast.info("Sign in as a retailer to request a payout");
    }
  };

  return (
    <Card className="overflow-hidden rounded-2xl border-0 bg-foreground text-background shadow-none"><div className="flex items-start gap-3 px-4 py-4"><span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-primary"><WalletCards className="h-[17px] w-[17px]" aria-hidden="true" /></span><div className="min-w-0"><p className="font-heading text-sm font-semibold">Wallet & growth</p><p className="mt-1 font-body text-xs leading-relaxed text-background/60">Turn today’s sales into tomorrow’s stock.</p></div></div><div className="border-t border-background/10 px-4 py-3"><div className="flex items-end justify-between gap-3"><div><p className="font-heading text-lg font-bold">{money(balance)}</p><p className="mt-0.5 font-body text-[10px] text-background/55">Available to withdraw</p></div><Button type="button" variant="secondary" size="sm" className="rounded-lg bg-background/10 font-heading text-[10px] text-background hover:bg-background/20" onClick={requestPayout}>Request payout</Button></div></div><div className="border-t border-background/10 px-4 py-3"><div className="flex items-center justify-between gap-3"><div><p className="font-heading text-xs font-semibold">Feature a listing</p><p className="mt-0.5 font-body text-[10px] text-background/55">Reach more local buyers</p></div><Button type="button" variant="link" size="sm" className="h-auto gap-1 p-0 font-heading text-[10px] font-semibold text-primary hover:text-primary/80" onClick={() => toast.info("Choose a listing to feature from the overflow menu")}>Promote <ArrowUpRight className="h-3 w-3" aria-hidden="true" /></Button></div></div></Card>
  );
}
