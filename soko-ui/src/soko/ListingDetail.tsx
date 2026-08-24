import { useState } from "react";
import { ArrowLeft, Heart, MapPin, MessageCircle, ShieldCheck, Store, Truck } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

import { listings, money, shops, type Listing } from "./data";
import { ListingCard } from "./ListingCard";
import { Stars } from "./Shared";

interface ListingDetailProps {
  listing: Listing;
  onBack: () => void;
  onChat: () => void;
  onShop: () => void;
  onCheckout: () => void;
  onOpenListing: (listing: Listing) => void;
  profile: import("@/services/api").ApiProfile | null;
  onRequireAuth: () => void;
  onFavoriteToggle?: (listingId: string, nextValue: boolean) => Promise<void>;
}

export function ListingDetail({ listing, onBack, onChat, onShop, onCheckout, onOpenListing, profile, onRequireAuth, onFavoriteToggle }: ListingDetailProps) {
  const shop = shops.find((item) => item.id === listing.shopId) ?? shops[0];
  const more = listings.filter((item) => item.shopId === shop.id && item.id !== listing.id).slice(0, 4);
  const [isFavorite, setIsFavorite] = useState(false);

  const toggleFavorite = async () => {
    if (!profile) { onRequireAuth(); return; }
    const nextValue = !isFavorite;
    setIsFavorite(nextValue);
    try {
      await onFavoriteToggle?.(listing.id, nextValue);
      toast.success(nextValue ? "Saved to favorites" : "Removed from favorites");
    } catch {
      setIsFavorite(!nextValue);
      toast.error("We couldn’t update favorites. Please try again.");
    }
  };

  return (
    <div className="mx-auto max-w-[1180px] space-y-8 px-4 py-6 sm:px-6 sm:py-8">
      <Button type="button" variant="ghost" size="sm" onClick={onBack} className="gap-1 text-muted-foreground"><ArrowLeft className="h-4 w-4" aria-hidden="true" /> Back to browse</Button>
      <div className="grid gap-8 lg:grid-cols-2">
        <Card className="overflow-hidden rounded-2xl border-border bg-secondary shadow-none"><img src={listing.image.replace("/500/500", "/800/800")} alt={listing.title} loading="eager" decoding="async" className="aspect-square w-full object-cover" /></Card>
        <div>
          <div className="flex items-center gap-2"><Badge variant="secondary" className="rounded-md">{listing.category}</Badge><Badge variant="outline" className="rounded-md text-muted-foreground">{listing.condition}</Badge></div>
          <h1 className="mt-3 font-heading text-3xl font-bold leading-tight tracking-[-.035em]">{listing.title}</h1>
          <div className="mt-3 flex items-center gap-4"><Stars value={listing.rating} size={16} /><span className="font-body text-sm text-muted-foreground">{listing.sold} sold</span></div>
          <p className="mt-5 font-heading text-4xl font-bold tracking-[-.04em] text-primary">{money(listing.price)}</p>
          <div className="mt-5 flex flex-wrap gap-4 font-body text-sm text-muted-foreground"><span className="inline-flex items-center gap-1.5"><Truck className="h-4 w-4 text-accent" aria-hidden="true" /> Delivery {money(shop.deliveryFee)}</span><span className="inline-flex items-center gap-1.5"><MapPin className="h-4 w-4 text-accent" aria-hidden="true" /> {listing.distanceKm} km away</span><span className="inline-flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-success" aria-hidden="true" /> Buyer protection</span></div>
          <p className="mt-5 font-body text-[15px] leading-relaxed text-foreground/90">Genuine quality item from a verified Soko retailer. Ships from {shop.address}. Pay securely with M-Pesa, card, or cash on delivery. Message the seller for colours, bulk pricing, or pickup.</p>
          <Button type="button" variant="ghost" className="mt-6 h-auto w-full justify-start gap-3 rounded-xl border border-border bg-card p-3 text-left hover:border-primary/50 hover:bg-card" onClick={onShop}><img src={shop.logo} alt={shop.name} loading="lazy" decoding="async" className="h-11 w-11 rounded-lg object-cover" /><span className="min-w-0 flex-1"><span className="flex items-center gap-1.5 font-heading text-sm font-medium">{shop.name}{shop.verified && <ShieldCheck className="h-3.5 w-3.5 text-accent" aria-label="Verified retailer" />}</span><span className="mt-1 block font-body text-xs text-muted-foreground">{shop.eta} · {shop.reviews} reviews</span></span><Store className="h-[18px] w-[18px] text-muted-foreground" aria-hidden="true" /></Button>
          <div className="mt-6 flex gap-3"><Button type="button" size="lg" className="h-11 flex-1 rounded-lg font-heading text-xs" onClick={onCheckout}>Buy now</Button><Tooltip><TooltipTrigger asChild><Button type="button" size="lg" variant="outline" className="h-11 rounded-lg" onClick={onChat} aria-label="Message seller"><MessageCircle className="h-[18px] w-[18px]" aria-hidden="true" /></Button></TooltipTrigger><TooltipContent>Message seller</TooltipContent></Tooltip><Tooltip><TooltipTrigger asChild><Button type="button" size="lg" variant="outline" className={`h-11 rounded-lg ${isFavorite ? "text-primary" : ""}`} onClick={toggleFavorite} aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}><Heart className={`h-[18px] w-[18px] ${isFavorite ? "fill-primary" : ""}`} aria-hidden="true" /></Button></TooltipTrigger><TooltipContent>{isFavorite ? "Remove from favorites" : "Add to favorites"}</TooltipContent></Tooltip></div>
        </div>
      </div>
      {more.length > 0 && <section><h2 className="mb-4 font-heading text-xl font-semibold">More from {shop.name}</h2><div className="grid grid-cols-2 gap-3.5 sm:grid-cols-4">{more.map((item) => <ListingCard key={item.id} listing={item} shop={shop} onOpen={onOpenListing} />)}</div></section>}
    </div>
  );
}
