import { ArrowRight, Package, Plus, Settings, Star, TrendingUp, Wallet } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";

import { api, type ApiWallet } from "@/services/api";

import { listings as fallbackListings, orders as fallbackOrders, shops as fallbackShops, type Listing, type Order, type SellerListing, type Shop } from "./data";
import { Eyebrow } from "./Shared";
import { IncomingOrders } from "./IncomingOrders";
import type { ListingAction } from "./ListingActionsMenu";
import { ListingsTable, type ListingFilter } from "./ListingsTable";
import { NewListingDialog, type NewListingValues } from "./NewListingDialog";
import { ShopSettingsDialog } from "./ShopSettingsDialog";
import { StatCard } from "./StatCard";
import { WalletGrowthCard } from "./WalletGrowthCard";

interface SellerDashboardProps {
  searchQuery: string;
  onSwitchToBuyer: () => void;
  listings?: Listing[];
  shops?: Shop[];
  orders?: Order[];
  onShopUpdated?: () => void;
}

export function SellerDashboard({ searchQuery, onSwitchToBuyer, listings = fallbackListings, shops = fallbackShops, orders = fallbackOrders, onShopUpdated }: SellerDashboardProps) {
  const shop = shops[0] ?? fallbackShops[0];
  const initialListings = listings.filter((listing) => listing.shopId === shop.id);
  const [listingFilter, setListingFilter] = useState<ListingFilter>("all");
  const [sellerListings, setSellerListings] = useState<SellerListing[]>(() => initialListings.map((listing) => ({ ...listing, status: "Active" })));
  const [dialogOpen, setDialogOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [wallet, setWallet] = useState<ApiWallet>();

  useEffect(() => {
    const nextListings = listings.filter((listing) => listing.shopId === shop.id);
    if (nextListings.length > 0) setSellerListings(nextListings.map((listing) => ({ ...listing, status: "Active" })));
  }, [listings, shop.id]);

  useEffect(() => {
    let active = true;
    api.getWallet().then((result) => { if (active) setWallet(result); }).catch(() => undefined);
    return () => { active = false; };
  }, []);

  const createDraft = ({ title, price, category, condition }: NewListingValues) => {
    const draft: SellerListing = { id: `draft-${Date.now()}`, shopId: shop.id, title, price, currency: "KSh", category, condition, image: "https://picsum.photos/seed/speaker/500/500", rating: 0, sold: 0, distanceKm: shop.distanceKm, status: "Draft" };
    setSellerListings((current) => [...current, draft]);
    setListingFilter("draft");
    toast.success("Draft saved locally — publish support will use the listings API when drafts are supported.");
  };

  const handleAction = (action: ListingAction, listing: SellerListing) => toast.info(action === "promote" ? `Promotion tools are ready for ${listing.title}` : `Listing editor opened for ${listing.title}`);
  const requestPayout = () => api.requestPayout(Math.min(wallet?.balance ?? 48250, 5000), "Seller payout request").then(() => undefined);
  const balance = wallet?.balance ?? 48250;

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-7 sm:px-5 sm:py-8"><section className="flex flex-wrap items-end justify-between gap-4"><div><div className="mb-2 flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-success" aria-hidden="true" /><Eyebrow tone="success">Seller workspace</Eyebrow></div><h1 className="font-heading text-3xl font-bold leading-tight tracking-[-.035em] sm:text-[34px]">Seller dashboard</h1><p className="mt-1 font-body text-sm text-muted-foreground">{shop.name}<span className="mx-1 text-border" aria-hidden="true">·</span>Your shop is live in Nairobi</p></div><div className="flex gap-2"><Button type="button" variant="outline" className="h-10 gap-2 rounded-lg font-heading text-sm" onClick={() => setSettingsOpen(true)}><Settings className="h-4 w-4" aria-hidden="true" /> Shop settings</Button><Button type="button" className="h-10 gap-2 rounded-lg font-heading text-sm" onClick={() => setDialogOpen(true)}><Plus className="h-4 w-4" aria-hidden="true" /> New listing</Button></div></section><section aria-label="Shop performance" className="grid grid-cols-2 gap-4 lg:grid-cols-4"><StatCard icon={Wallet} label="Wallet balance" value={`KSh ${balance.toLocaleString("en-KE")}`} delta="12%" tone="bg-primary/15 text-primary" /><StatCard icon={TrendingUp} label="Sales this week" value="KSh 21,400" delta="8%" tone="bg-accent/15 text-accent" /><StatCard icon={Package} label="Open orders" value="7" note="This week" tone="bg-secondary text-foreground" /><StatCard icon={Star} label="Shop rating" value={shop.rating.toFixed(1)} note="Top rated" tone="bg-success/15 text-success" /></section><section className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_340px]"><ListingsTable listings={sellerListings} filter={listingFilter} searchQuery={searchQuery} onFilterChange={setListingFilter} onAction={handleAction} /><div className="space-y-6"><IncomingOrders orders={orders} /><WalletGrowthCard balance={balance} onRequestPayout={requestPayout} /></div></section><section className="rounded-2xl border border-border bg-card px-5 py-4 lg:hidden"><p className="font-heading text-sm font-semibold">Shopping as a buyer?</p><p className="mt-1 font-body text-xs text-muted-foreground">Preview the marketplace without leaving your seller workspace.</p><Button type="button" variant="link" size="sm" className="mt-1 gap-1 px-0 font-heading text-xs text-primary" onClick={onSwitchToBuyer}>Open buyer preview <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" /></Button></section><NewListingDialog open={dialogOpen} onOpenChange={setDialogOpen} onSubmit={createDraft} /><ShopSettingsDialog open={settingsOpen} shop={shop} onOpenChange={setSettingsOpen} onUpdated={() => onShopUpdated?.()} /></div>
  );
}
