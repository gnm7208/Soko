import { SearchX, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

import type { SellerListing } from "./data";
import { money } from "./data";
import { ListingActionsMenu, type ListingAction } from "./ListingActionsMenu";

export type ListingFilter = "all" | "featured" | "draft";

interface ListingsTableProps {
  listings: SellerListing[];
  filter: ListingFilter;
  searchQuery: string;
  onFilterChange: (filter: ListingFilter) => void;
  onAction: (action: ListingAction, listing: SellerListing) => void;
}

export function ListingsTable({ listings, filter, searchQuery, onFilterChange, onAction }: ListingsTableProps) {
  const query = searchQuery.trim().toLowerCase();
  const visibleListings = listings.filter((listing) => {
    const filterMatch = filter === "all" || (filter === "featured" ? listing.featured : listing.status === "Draft");
    const searchMatch = !query || `${listing.title} ${listing.category} ${listing.status}`.toLowerCase().includes(query);
    return filterMatch && searchMatch;
  });

  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-4"><div><h2 className="font-heading text-base font-semibold">Your listings</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">{visibleListings.length} {visibleListings.length === 1 ? "product" : "products"} shown</p></div><Tabs value={filter} onValueChange={(value) => onFilterChange(value as ListingFilter)}><TabsList className="h-auto rounded-lg bg-background p-1"><TabsTrigger value="all" className="px-2.5 py-1.5 font-heading text-[11px] data-[state=active]:bg-card">All</TabsTrigger><TabsTrigger value="featured" className="px-2.5 py-1.5 font-heading text-[11px] data-[state=active]:bg-card">Featured</TabsTrigger><TabsTrigger value="draft" className="px-2.5 py-1.5 font-heading text-[11px] data-[state=active]:bg-card">Drafts</TabsTrigger></TabsList></Tabs></div>
      {visibleListings.length === 0 ? <div className="px-4 py-12 text-center"><SearchX className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No listings found</p><p className="mt-1 font-body text-[11px] text-muted-foreground">Try another search or filter.</p></div> : <div className="overflow-x-auto"><table className="min-w-[620px] w-full text-left"><thead><tr className="border-b border-border bg-background/70 font-heading text-[10px] font-semibold uppercase tracking-[.1em] text-muted-foreground"><th className="px-4 py-2.5 font-medium">Product</th><th className="px-4 py-2.5 font-medium">Performance</th><th className="px-4 py-2.5 font-medium">Price</th><th className="w-12 px-4 py-2.5" /></tr></thead><tbody>{visibleListings.map((listing) => <tr key={listing.id} className="border-b border-border last:border-0 hover:bg-background"><td className="px-4 py-3.5"><div className="flex min-w-0 items-center gap-3"><img src={listing.image} alt={listing.title} loading="lazy" decoding="async" className="h-11 w-11 shrink-0 rounded-lg object-cover" /><div className="min-w-0"><p className="truncate font-body text-sm font-medium">{listing.title}</p><div className="mt-1 flex items-center gap-2 font-body text-[10px] text-muted-foreground"><span>{listing.category}</span><span aria-hidden="true">·</span><span className={listing.status === "Draft" ? "text-primary" : "text-success"}>{listing.status}</span></div></div></div></td><td className="px-4 py-3.5"><p className="font-heading text-xs font-semibold">{listing.sold} sold</p><p className="mt-1 font-body text-[10px] text-muted-foreground">{listing.status === "Draft" ? "Not published" : "All time"}</p></td><td className="px-4 py-3.5"><p className="font-heading text-sm font-semibold text-primary">{money(listing.price)}</p>{listing.featured && <Badge className="mt-1 gap-1 rounded-md bg-primary/10 px-1.5 py-0.5 font-heading text-[9px] text-primary hover:bg-primary/10"><Sparkles className="h-2.5 w-2.5" aria-hidden="true" /> Featured</Badge>}</td><td className="px-4 py-3.5"><ListingActionsMenu listing={listing} onAction={onAction} /></td></tr>)}</tbody></table></div>}
    </Card>
  );
}
