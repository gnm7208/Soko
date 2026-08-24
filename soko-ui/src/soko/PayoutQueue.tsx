import { Check, Wallet, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import type { ApiPayoutRequest } from "@/services/api";
import { money } from "./data";

interface PayoutQueueProps {
  payouts: ApiPayoutRequest[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}

export function PayoutQueue({ payouts, onApprove, onReject }: PayoutQueueProps) {
  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><h2 className="font-heading text-base font-semibold">Payout requests</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">Pending seller wallet payouts</p></div>
      {payouts.length === 0 ? <div className="px-4 py-10 text-center"><Wallet className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No payouts pending</p></div> : <div className="divide-y divide-border">{payouts.map((payout) => <div key={payout.id} className="flex items-center gap-3 px-4 py-3.5"><div className="min-w-0 flex-1"><p className="font-heading text-xs font-semibold">{payout.owner_name ?? "Seller"}</p><p className="mt-0.5 font-body text-[11px] text-muted-foreground">{payout.ref ?? payout.id}</p></div><span className="shrink-0 font-heading text-sm font-semibold text-primary">{money(payout.amount)}</span><div className="flex shrink-0 gap-1.5"><Button type="button" size="sm" variant="outline" className="h-8 gap-1 border-success/35 bg-success/10 px-2.5 text-[10px] text-success" onClick={() => onApprove(payout.id)}><Check className="h-3.5 w-3.5" aria-hidden="true" /> Approve</Button><Button type="button" size="sm" variant="outline" className="h-8 gap-1 border-destructive/35 bg-destructive/10 px-2.5 text-[10px] text-destructive" onClick={() => onReject(payout.id)}><X className="h-3.5 w-3.5" aria-hidden="true" /> Reject</Button></div></div>)}</div>}
    </Card>
  );
}
