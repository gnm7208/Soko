import { Check, ShieldOff, Store } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import type { ApiShop } from "@/services/api";

const statusStyles: Record<string, string> = {
  pending: "border-accent/30 bg-accent/15 text-accent",
  approved: "border-success/30 bg-success/15 text-success",
  active: "border-success/30 bg-success/15 text-success",
  suspended: "border-destructive/30 bg-destructive/15 text-destructive",
};

interface ShopApprovalQueueProps {
  shops: ApiShop[];
  onApprove: (id: string) => void;
  onSuspend: (id: string) => void;
}

export function ShopApprovalQueue({ shops, onApprove, onSuspend }: ShopApprovalQueueProps) {
  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><h2 className="font-heading text-base font-semibold">Shop approvals</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">Review new and flagged shops before they go live</p></div>
      {shops.length === 0 ? <div className="px-4 py-10 text-center"><Store className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No shops need review</p><p className="mt-1 font-body text-[11px] text-muted-foreground">You’re all caught up.</p></div> : <div className="divide-y divide-border">{shops.map((shop) => <div key={shop.id} className="flex items-center gap-3 px-4 py-3.5"><img src={shop.logo_url ?? undefined} alt="" className="h-10 w-10 shrink-0 rounded-lg bg-secondary object-cover" /><div className="min-w-0 flex-1"><p className="font-heading text-xs font-semibold">{shop.name}</p><p className="mt-0.5 truncate font-body text-[11px] text-muted-foreground">{shop.category}{shop.address ? ` · ${shop.address}` : ""}</p></div><Badge variant="outline" className={`shrink-0 rounded-full text-[10px] ${statusStyles[shop.status ?? "pending"] ?? ""}`}>{shop.status ?? "pending"}</Badge><div className="flex shrink-0 gap-1.5"><Button type="button" size="sm" variant="outline" className="h-8 gap-1 border-success/35 bg-success/10 px-2.5 text-[10px] text-success" onClick={() => onApprove(shop.id)}><Check className="h-3.5 w-3.5" aria-hidden="true" /> Approve</Button><Button type="button" size="sm" variant="outline" className="h-8 gap-1 border-destructive/35 bg-destructive/10 px-2.5 text-[10px] text-destructive" onClick={() => onSuspend(shop.id)}><ShieldOff className="h-3.5 w-3.5" aria-hidden="true" /> Suspend</Button></div></div>)}</div>}
    </Card>
  );
}
