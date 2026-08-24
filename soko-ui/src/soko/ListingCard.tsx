import { MapPin, Sparkles } from "lucide-react";
import { motion, useReducedMotion, type Variants } from "motion/react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

import type { Listing, Shop } from "./data";
import { money } from "./data";
import { Stars } from "./Shared";

interface ListingCardProps {
  listing: Listing;
  shop: Shop;
  onOpen: (listing: Listing) => void;
}

const cardEase = [0.22, 1, 0.36, 1] as const;

export const listingCardItemVariants: Variants = {
  hidden: { opacity: 0, y: 12, scale: 0.97 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.28, ease: cardEase } },
};

export function ListingCard({ listing, shop, onOpen }: ListingCardProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      variants={listingCardItemVariants}
      whileHover={shouldReduceMotion ? undefined : { y: -4, scale: 1.01 }}
      whileTap={shouldReduceMotion ? undefined : { scale: 0.98 }}
      transition={{ duration: 0.18, ease: cardEase }}
    >
      <Card className="group overflow-hidden rounded-xl border-border/70 bg-card shadow-sm transition-colors hover:border-primary/40 hover:shadow-md">
        <button
          type="button"
          className="flex h-full w-full flex-col items-stretch text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          onClick={() => onOpen(listing)}
          aria-label={`View ${listing.title}`}
        >
          <div className="relative aspect-[1/.92] overflow-hidden bg-secondary">
            <img
              src={listing.image}
              alt={listing.title}
              loading="lazy"
              decoding="async"
              className="soko-photo h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.045]"
            />
            {listing.featured && (
              <Badge className="absolute left-2.5 top-2.5 gap-1 rounded-md bg-[hsl(var(--gold))] px-2 py-1 text-[10px] text-foreground hover:bg-[hsl(var(--gold))]">
                <Sparkles className="h-3 w-3" aria-hidden="true" />
                Featured
              </Badge>
            )}
            <span className="absolute bottom-2.5 left-2.5 inline-flex items-center gap-1 rounded-md bg-foreground/80 px-2 py-1 font-heading text-[10px] text-background backdrop-blur-sm">
              <MapPin className="h-3 w-3" aria-hidden="true" />
              {listing.distanceKm} km
            </span>
          </div>
          <div className="flex flex-1 flex-col gap-2 p-3.5">
            <p className="line-clamp-2 min-h-[2.65rem] font-body text-[13px] leading-snug text-foreground">{listing.title}</p>
            <p className="font-heading tabular-nums text-[17px] font-bold tracking-[-.035em] text-primary">{money(listing.price)}</p>
            <div className="flex items-center justify-between gap-2">
              <Stars value={listing.rating} size={13} />
              <span className="font-body text-[10px] text-muted-foreground">{listing.sold} sold</span>
            </div>
            <p className="truncate pt-0.5 font-body text-[10px] text-muted-foreground">{shop.name}</p>
          </div>
        </button>
      </Card>
    </motion.div>
  );
}
