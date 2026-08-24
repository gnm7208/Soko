import { ArrowLeft, Clock, MapPin, MessageCircle, Navigation, ShieldCheck } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { listings as fallbackListings, type Listing, type Shop } from "./data";
import { ListingCard } from "./ListingCard";
import { Stars } from "./Shared";

function MapCard({ shop }: { shop: Shop }) {
  const openDirections = () => toast.info(`Directions to ${shop.name} are ready to open from Nairobi.`);

  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none"><div className="relative h-56 overflow-hidden soko-map-grid bg-secondary/40"><svg className="absolute inset-0 h-full w-full" preserveAspectRatio="none" aria-hidden="true"><path d="M0,120 C120,90 240,150 400,110 L400,140 L0,140 Z" fill="rgba(239,230,216,.8)" /><path d="M0,120 C120,90 240,150 400,110" stroke="rgba(228,217,199,.85)" strokeWidth="10" fill="none" /><path d="M180,0 L210,260" stroke="rgba(228,217,199,.85)" strokeWidth="8" fill="none" /></svg><div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-full"><div className="flex flex-col items-center"><div className="rounded-full bg-primary p-2 text-primary-foreground shadow-lg ring-8 ring-primary/15"><MapPin className="h-[18px] w-[18px]" aria-hidden="true" /></div><div className="-mt-0.5 h-2 w-2 rotate-45 bg-primary" aria-hidden="true" /></div></div><div className="absolute bottom-3 left-3 rounded-lg bg-card/95 px-3 py-1.5 text-xs shadow-sm backdrop-blur"><span className="inline-flex items-center gap-1"><MapPin className="h-3 w-3 text-primary" aria-hidden="true" /> {shop.address}</span></div></div><div className="flex items-center justify-between gap-3 p-4"><div className="font-body text-sm"><p className="inline-flex items-center gap-1.5 font-heading text-xs font-medium"><Clock className="h-3.5 w-3.5 text-accent" aria-hidden="true" /> {shop.eta}</p><p className="mt-1 text-muted-foreground">{shop.distanceKm} km · Delivery from KSh {shop.deliveryFee}</p></div><Button type="button" className="gap-2 rounded-lg font-heading text-xs" onClick={openDirections}><Navigation className="h-4 w-4" aria-hidden="true" /> Get directions</Button></div></Card>
  );
}

interface ShopProfileProps {
  shop: Shop;
  listings?: Listing[];
  onBack: () => void;
  onOpenListing: (listing: Listing) => void;
  onChat: () => void;
}

export function ShopProfile({ shop, listings = fallbackListings, onBack, onOpenListing, onChat }: ShopProfileProps) {
  const shopListings = listings.filter((listing) => listing.shopId === shop.id);

  return (
    <div className="mx-auto max-w-[1180px] space-y-6 px-4 py-6 sm:px-6 sm:py-8"><Button type="button" variant="ghost" size="sm" onClick={onBack} className="gap-1 text-muted-foreground"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back</Button><div className="overflow-hidden rounded-2xl border border-border bg-card"><div className="h-40 w-full bg-secondary sm:h-52"><img src={shop.cover} alt="" loading="lazy" decoding="async" className="h-full w-full object-cover" /></div><div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center"><img src={shop.logo} alt={shop.name} loading="lazy" decoding="async" className="-mt-12 h-20 w-20 rounded-2xl border-4 border-card object-cover" /><div className="flex-1"><h1 className="flex items-center gap-2 font-heading text-2xl font-bold tracking-[-.03em]">{shop.name}{shop.verified && <ShieldCheck className="h-[18px] w-[18px] text-accent" aria-label="Verified retailer" />}</h1><div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-body text-sm text-muted-foreground"><Stars value={shop.rating} /><span>{shop.reviews} reviews</span><span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" aria-hidden="true" /> {shop.address}</span></div></div><Button type="button" variant="outline" className="gap-2 rounded-lg font-heading text-xs" onClick={onChat}><MessageCircle className="h-4 w-4" aria-hidden="true" /> Message</Button></div></div><div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]"><div><h2 className="mb-4 font-heading text-xl font-semibold">{shopListings.length} listings</h2><div className="grid grid-cols-2 gap-3.5 sm:grid-cols-3">{shopListings.map((listing) => <ListingCard key={listing.id} listing={listing} shop={shop} onOpen={onOpenListing} />)}</div></div><div className="space-y-4"><MapCard shop={shop} /><Card className="rounded-2xl border-border p-4 shadow-none"><p className="mb-2 font-heading font-semibold">Ratings</p><div className="flex items-center gap-3"><span className="font-heading text-4xl font-bold">{shop.rating}</span><div><Stars value={shop.rating} size={16} /><p className="font-body text-xs text-muted-foreground">{shop.reviews} verified reviews</p></div></div></Card></div></div></div>
  );
}

