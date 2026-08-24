import * as DialogPrimitive from "@radix-ui/react-dialog";
import { ArrowRight, Heart, MapPin, MessageCircle, ShieldCheck, Star, Store, Truck, X } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogDescription, DialogHeader, DialogOverlay, DialogPortal, DialogTitle } from "@/components/ui/dialog";

import type { Listing, Shop } from "./data";
import { money } from "./data";

const uiEase = [0.22, 1, 0.36, 1] as const;

interface ProductDrawerProps {
  listing?: Listing;
  shop?: Shop;
  open: boolean;
  isFavorite: boolean;
  onOpenChange: (open: boolean) => void;
  onBuy: (listing: Listing) => void;
  onMessage: () => void;
  onViewDetails: (listing: Listing) => void;
  onFavorite: (listingId: string) => void | Promise<void>;
}

export function ProductDrawer({ listing, shop, open, isFavorite, onOpenChange, onBuy, onMessage, onViewDetails, onFavorite }: ProductDrawerProps) {
  const shouldReduceMotion = useReducedMotion();
  if (!listing || !shop) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <DialogPortal forceMount>
            <DialogOverlay forceMount asChild>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} />
            </DialogOverlay>
            <DialogPrimitive.Content forceMount asChild>
              <motion.div
                initial={shouldReduceMotion ? { opacity: 0 } : { x: "100%", opacity: 0.6 }}
                animate={{ x: 0, opacity: 1 }}
                exit={shouldReduceMotion ? { opacity: 0 } : { x: "100%", opacity: 0.6 }}
                transition={{ duration: 0.28, ease: uiEase }}
                className="fixed right-0 top-0 z-50 h-screen w-full max-w-[420px] overflow-y-auto rounded-none border-y-0 border-r-0 border-l border-border bg-background p-5 shadow-[-15px_0_36px_rgba(20,20,19,.17)]"
              >
        <DialogHeader className="text-left">
          <p className="font-heading text-[11px] font-semibold uppercase tracking-[.16em] text-primary">Product details</p>
          <DialogTitle className="sr-only">{listing.title}</DialogTitle>
          <DialogDescription className="sr-only">Product details and actions for {listing.title} from {shop.name}.</DialogDescription>
        </DialogHeader>

        <div className="mt-2 overflow-hidden rounded-2xl bg-secondary">
          <img src={listing.image} alt={listing.title} loading="lazy" decoding="async" className="h-[310px] w-full object-cover" />
        </div>

        <div className="space-y-4 pt-1">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="rounded-md px-2 py-1 text-[10px]">{listing.category}</Badge>
            <Badge variant="outline" className="rounded-md px-2 py-1 text-[10px] text-muted-foreground">{listing.condition}</Badge>
          </div>
          <div>
            <h2 className="font-heading text-[25px] font-semibold leading-tight tracking-[-.04em]">{listing.title}</h2>
            <p className="mt-3 font-heading text-[27px] font-bold tracking-[-.035em] text-primary">{money(listing.price)}</p>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-2 font-body text-[11px] text-muted-foreground">
            <span className="inline-flex items-center gap-1.5"><Star className="h-3.5 w-3.5 fill-primary text-primary" aria-hidden="true" />{listing.rating.toFixed(1)}</span>
            <span className="inline-flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-accent" aria-hidden="true" />{listing.distanceKm} km away</span>
            <span className="inline-flex items-center gap-1.5"><Truck className="h-3.5 w-3.5 text-accent" aria-hidden="true" />Delivery {money(shop.deliveryFee)}</span>
          </div>
          <p className="font-body text-sm leading-relaxed text-foreground/90">Genuine quality item from a verified Soko retailer. Ships from {shop.address}. Pay securely with M-Pesa, card, or cash on delivery.</p>

          <div className="flex items-center gap-3 rounded-xl border border-border bg-card p-3">
            <img src={shop.logo} alt={shop.name} loading="lazy" decoding="async" className="h-10 w-10 rounded-lg object-cover" />
            <div className="min-w-0 flex-1">
              <p className="flex items-center gap-1.5 font-heading text-[11px] font-semibold">{shop.name}{shop.verified && <ShieldCheck className="h-3.5 w-3.5 text-accent" aria-label="Verified retailer" />}</p>
              <p className="mt-1 font-body text-[10px] text-muted-foreground">Verified retailer · {shop.eta}</p>
            </div>
            <Store className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          </div>

          <div className="flex gap-2">
            <Button type="button" className="h-11 flex-1 rounded-lg font-heading text-xs" onClick={() => onBuy(listing)}>
              Buy now <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Button>
            <Button type="button" variant="outline" className="h-11 rounded-lg font-heading text-xs" onClick={onMessage}>
              <MessageCircle className="h-4 w-4" aria-hidden="true" />
              <span className="sr-only">Message seller</span>
            </Button>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <Button type="button" variant="ghost" size="sm" className={`px-0 font-heading text-xs ${isFavorite ? "text-primary" : "text-muted-foreground"}`} onClick={() => onFavorite(listing.id)}>
              <Heart className={`h-3.5 w-3.5 ${isFavorite ? "fill-primary" : ""}`} aria-hidden="true" />
              {isFavorite ? "Saved to favorites" : "Add to favorites"}
            </Button>
            <Button type="button" variant="link" size="sm" className="px-0 font-heading text-xs text-accent" onClick={() => onViewDetails(listing)}>View full listing <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" /></Button>
          </div>
        </div>
                <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
                  <X className="h-4 w-4" />
                  <span className="sr-only">Close</span>
                </DialogPrimitive.Close>
              </motion.div>
            </DialogPrimitive.Content>
          </DialogPortal>
        )}
      </AnimatePresence>
    </Dialog>
  );
}
