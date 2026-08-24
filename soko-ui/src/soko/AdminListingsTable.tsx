import { EyeOff, PackageSearch, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import type { ApiListing } from "@/services/api";
import { money } from "./data";

const statusStyles: Record<string, string> = {
  active: "border-success/30 bg-success/15 text-success",
  hidden: "border-muted-foreground/30 bg-muted text-muted-foreground",
  sold: "border-accent/30 bg-accent/15 text-accent",
};

interface AdminListingsTableProps {
  listings: ApiListing[];
  onSetStatus: (id: string, status: "active" | "hidden") => void;
}

export function AdminListingsTable({ listings, onSetStatus }: AdminListingsTableProps) {
  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><h2 className="font-heading text-base font-semibold">Listing moderation</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">{listings.length} listings across all shops</p></div>
      {listings.length === 0 ? <div className="px-4 py-10 text-center"><PackageSearch className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No listings to review</p></div> : <div className="overflow-x-auto"><table className="min-w-[620px] w-full text-left"><thead><tr className="border-b border-border text-[10px] uppercase tracking-[.08em] text-muted-foreground"><th className="px-4 py-2.5 font-heading font-medium">Listing</th><th className="px-4 py-2.5 font-heading font-medium">Price</th><th className="px-4 py-2.5 font-heading font-medium">Status</th><th className="px-4 py-2.5 font-heading font-medium">Actions</th></tr></thead><tbody>{listings.map((listing) => <tr key={listing.id} className="border-b border-border last:border-0 hover:bg-background"><td className="px-4 py-3 font-body text-xs">{listing.title}</td><td className="px-4 py-3 font-heading text-xs font-semibold text-primary">{money(listing.price)}</td><td className="px-4 py-3"><Badge variant="outline" className={`rounded-full text-[10px] ${statusStyles[listing.status ?? "active"] ?? ""}`}>{listing.status ?? "active"}</Badge></td><td className="px-4 py-3"><div className="flex gap-1.5">{listing.status !== "hidden" ? <Button type="button" size="sm" variant="outline" className="h-7 gap-1 px-2 text-[10px] text-muted-foreground" onClick={() => onSetStatus(listing.id, "hidden")}><EyeOff className="h-3 w-3" aria-hidden="true" /> Hide</Button> : <Button type="button" size="sm" variant="outline" className="h-7 gap-1 border-success/35 bg-success/10 px-2 text-[10px] text-success" onClick={() => onSetStatus(listing.id, "active")}><ShieldCheck className="h-3 w-3" aria-hidden="true" /> Restore</Button>}</div></td></tr>)}</tbody></table></div>}
    </Card>
  );
}
