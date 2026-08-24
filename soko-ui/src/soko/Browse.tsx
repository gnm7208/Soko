import { ArrowDownRight, ArrowRight, Filter, MapPin, Plus } from "lucide-react";
import { motion } from "motion/react";
import { useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { listings as fallbackListings, shops as fallbackShops, type Category, type Listing, type Shop } from "./data";
import type { ApiProfile } from "@/services/api";
import { CategoryChips } from "./CategoryChips";
import { EmptyState } from "./EmptyState";
import { FilterPanel, type QuickFilter } from "./FilterPanel";
import { ListingCard } from "./ListingCard";
import { ProductDrawer } from "./ProductDrawer";
import { Eyebrow, SectionTitle } from "./Shared";

interface BrowseProps {
  listings?: Listing[];
  shops?: Shop[];
  categories?: Category[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onOpenListing: (listing: Listing) => void;
  onCheckout: (listing: Listing) => void;
  onChat: (listing?: Listing) => void;
  onSell: () => void;
  profile: ApiProfile | null;
  onRequireAuth: () => void;
  onFavoriteToggle?: (listingId: string, nextValue: boolean) => Promise<void>;
}

type SortValue = "relevance" | "price-low" | "price-high";

const gridContainerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.045 } },
};

export function Browse({ listings = fallbackListings, shops = fallbackShops, categories = [], searchQuery, onSearchChange, onOpenListing, onCheckout, onChat, onSell, profile, onRequireAuth, onFavoriteToggle }: BrowseProps) {
  const [activeCategory, setActiveCategory] = useState("All");
  const [quickFilter, setQuickFilter] = useState<QuickFilter>(null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [sort, setSort] = useState<SortValue>("relevance");
  const [selectedListing, setSelectedListing] = useState<Listing>();
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);
  const categoriesRef = useRef<HTMLElement>(null);

  const matches = (listing: Listing) => {
    const query = searchQuery.trim().toLowerCase();
    const shop = shops.find((item) => item.id === listing.shopId);
    const searchable = `${listing.title} ${listing.category} ${shop?.name ?? ""}`.toLowerCase();
    const categoryMatches = activeCategory === "All" || listing.category === activeCategory;
    const queryMatches = !query || searchable.includes(query);
    const quickMatches = quickFilter === "near" ? listing.distanceKm <= 5 : quickFilter === "new" ? listing.condition === "New" : true;
    return categoryMatches && queryMatches && quickMatches;
  };

  const visibleListings = useMemo(() => {
    const filtered = listings.filter(matches);
    if (sort === "price-low") return [...filtered].sort((a, b) => a.price - b.price);
    if (sort === "price-high") return [...filtered].sort((a, b) => b.price - a.price);
    return filtered;
  // The filter values are the stable dependencies for this derived collection.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCategory, quickFilter, searchQuery, sort, listings, shops]);

  const featuredListings = useMemo(() => visibleListings.filter((listing) => listing.featured), [visibleListings]);
  const showFeatured = activeCategory === "All" && !searchQuery.trim() && !quickFilter && featuredListings.length > 0;
  const selectedShop = selectedListing ? shops.find((shop) => shop.id === selectedListing.shopId) : undefined;
  const listingLabel = `${visibleListings.length} ${visibleListings.length === 1 ? "product" : "products"}${activeCategory !== "All" ? ` in ${activeCategory}` : ""}${quickFilter === "near" ? " within 5 km" : quickFilter === "new" ? " with new items" : ""} around Nairobi`;

  const resetFilters = () => { setActiveCategory("All"); setQuickFilter(null); onSearchChange(""); };
  const openDrawer = (listing: Listing) => setSelectedListing(listing);
  const toggleFavorite = async (id: string) => {
    if (!profile) { onRequireAuth(); return; }
    const nextValue = !favoriteIds.includes(id);
    setFavoriteIds((ids) => nextValue ? [...ids, id] : ids.filter((item) => item !== id));
    try {
      await onFavoriteToggle?.(id, nextValue);
    } catch {
      setFavoriteIds((ids) => nextValue ? ids.filter((item) => item !== id) : [...ids, id]);
    }
  };

  return (
    <div className="mx-auto max-w-[1180px] space-y-8 px-4 py-6 sm:px-6 sm:py-8">
      <section className="relative flex min-h-[274px] items-center overflow-hidden rounded-3xl bg-foreground px-6 py-10 text-background sm:px-12" aria-labelledby="browse-hero-title"><div className="relative z-10 max-w-[575px]"><Eyebrow>Soko marketplace</Eyebrow><h1 id="browse-hero-title" className="mt-3 max-w-[600px] font-heading text-3xl font-bold leading-[1.1] tracking-[-.045em] sm:text-[38px]">Everything your neighbourhood sells — in one place.</h1><p className="mt-4 max-w-[515px] font-body text-sm leading-relaxed text-background/70">Find local retailers, get directions, chat, and pay by M-Pesa, card, or cash on delivery.</p><div className="mt-6 flex flex-wrap gap-2.5"><Button type="button" size="lg" className="h-11 rounded-lg font-heading text-xs" onClick={() => categoriesRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}>Start shopping <ArrowDownRight className="h-3.5 w-3.5" aria-hidden="true" /></Button><Button type="button" size="lg" variant="outline" className="h-11 rounded-lg border-background/30 bg-transparent font-heading text-xs text-background hover:bg-background/10 hover:text-background" onClick={onSell}>Sell on Soko <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" /></Button></div></div><div className="pointer-events-none absolute -right-10 -top-12 h-56 w-56 rounded-full bg-primary/30 blur-3xl" aria-hidden="true" /><div className="pointer-events-none absolute -bottom-16 right-28 h-44 w-44 rounded-full bg-accent/30 blur-3xl" aria-hidden="true" /><div className="pointer-events-none absolute right-16 top-8 h-[270px] w-[270px] rounded-full border border-background/10" aria-hidden="true" /></section>

      <section ref={categoriesRef} className="scroll-mt-24" aria-labelledby="categories-title"><SectionTitle action={<Button type="button" variant={filtersOpen ? "secondary" : "ghost"} size="sm" className="gap-2 text-xs text-muted-foreground" onClick={() => setFiltersOpen((open) => !open)} aria-expanded={filtersOpen}><Filter className="h-3.5 w-3.5" aria-hidden="true" /> Filters</Button>}><span id="categories-title">Browse categories</span></SectionTitle><p className="-mt-3 mb-3 font-body text-[11px] text-muted-foreground">Showing all listings near Nairobi</p>{filtersOpen && <div className="mb-4"><FilterPanel quickFilter={quickFilter} onChange={setQuickFilter} onReset={resetFilters} /></div>}<CategoryChips categories={categories} activeCategory={activeCategory} onChange={setActiveCategory} /></section>

      {showFeatured && <section aria-labelledby="featured-title"><SectionTitle action={<span className="inline-flex items-center gap-1 font-body text-[11px] text-muted-foreground"><MapPin className="h-3.5 w-3.5 text-primary" aria-hidden="true" /> Nairobi</span>}><span><Eyebrow>For you</Eyebrow><span id="featured-title" className="mt-1 block">Featured near you</span></span></SectionTitle><motion.div variants={gridContainerVariants} initial="hidden" animate="show" className="grid grid-cols-2 gap-3.5 sm:grid-cols-3">{featuredListings.map((listing) => <ListingCard key={listing.id} listing={listing} shop={shops.find((shop) => shop.id === listing.shopId) ?? shops[0]} onOpen={openDrawer} />)}</motion.div></section>}

      <section aria-labelledby="all-listings-title"><SectionTitle action={<Select value={sort} onValueChange={(value) => setSort(value as SortValue)}><SelectTrigger className="h-8 w-[116px] border-0 bg-transparent px-2 text-[11px] text-muted-foreground shadow-none"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="relevance">Relevance</SelectItem><SelectItem value="price-low">Price: low</SelectItem><SelectItem value="price-high">Price: high</SelectItem></SelectContent></Select>}><span><span id="all-listings-title">{activeCategory === "All" ? "All listings" : activeCategory}</span><span className="mt-1 block font-body text-[11px] font-normal text-muted-foreground">{listingLabel}</span></span></SectionTitle>{visibleListings.length > 0 ? <motion.div key={`${activeCategory}-${quickFilter}-${sort}`} variants={gridContainerVariants} initial="hidden" whileInView="show" viewport={{ once: true, margin: "-80px" }} className="grid grid-cols-2 gap-3.5 sm:grid-cols-3 lg:grid-cols-4">{visibleListings.map((listing) => <ListingCard key={listing.id} listing={listing} shop={shops.find((shop) => shop.id === listing.shopId) ?? shops[0]} onOpen={openDrawer} />)}</motion.div> : <EmptyState onReset={resetFilters} />}</section>

      <section className="overflow-hidden rounded-2xl bg-foreground text-background" aria-label="Sell on Soko"><div className="flex flex-col items-start justify-between gap-5 px-6 py-7 sm:flex-row sm:items-end sm:px-8"><div><Eyebrow>Soko seller space</Eyebrow><h2 className="mt-2 font-heading text-2xl font-semibold leading-tight tracking-[-.04em]">Turn your stock into your next customer.</h2><p className="mt-2 max-w-xl font-body text-xs leading-relaxed text-background/65">Your shop dashboard is ready for listings, orders, promotions, and wallet payouts — all in one place.</p></div><Button type="button" className="shrink-0 rounded-lg font-heading text-xs" onClick={onSell}><Plus className="h-3.5 w-3.5" aria-hidden="true" /> New listing</Button></div><div className="grid grid-cols-2 gap-px bg-background/10 sm:grid-cols-4"><div className="bg-background/[.045] p-5"><span className="font-heading text-[10px] text-background/55">Shop</span><strong className="mt-2 block font-heading text-base">{shops[0]?.name ?? "Local retailer"}</strong></div><div className="bg-background/[.045] p-5"><span className="font-heading text-[10px] text-background/55">Wallet balance</span><strong className="mt-2 block font-heading text-xl text-primary">KSh 48,250</strong></div><div className="bg-background/[.045] p-5"><span className="font-heading text-[10px] text-background/55">Sales this week</span><strong className="mt-2 block font-heading text-xl">KSh 21,400</strong></div><div className="bg-background/[.045] p-5"><span className="font-heading text-[10px] text-background/55">Shop rating</span><strong className="mt-2 block font-heading text-xl text-success">{shops[0]?.rating.toFixed(1) ?? "4.8"} ★</strong></div></div></section>

      <ProductDrawer listing={selectedListing} shop={selectedShop} open={Boolean(selectedListing)} isFavorite={selectedListing ? favoriteIds.includes(selectedListing.id) : false} onOpenChange={(open) => !open && setSelectedListing(undefined)} onBuy={(nextListing) => { setSelectedListing(undefined); onCheckout(nextListing); }} onMessage={() => { const nextListing = selectedListing; setSelectedListing(undefined); onChat(nextListing); }} onViewDetails={(nextListing) => { setSelectedListing(undefined); onOpenListing(nextListing); }} onFavorite={toggleFavorite} />
    </div>
  );
}
