import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Toaster } from "@/components/ui/sonner";
import { api, type ApiProfile } from "@/services/api";

import { AdminDashboard } from "./soko/AdminDashboard";
import { AppShell } from "./soko/AppShell";
import { AuthDialog } from "./soko/AuthDialog";
import { Browse } from "./soko/Browse";
import { Chat } from "./soko/Chat";
import { Checkout } from "./soko/Checkout";
import { EditProfileDialog } from "./soko/EditProfileDialog";
import { ListingDetail } from "./soko/ListingDetail";
import { Orders } from "./soko/Orders";
import { SellerDashboard } from "./soko/SellerDashboard";
import { ShopProfile } from "./soko/ShopProfile";
import { listings as fallbackListings, shops as fallbackShops, type Listing, type MarketplaceMode, type Screen, type Shop } from "./soko/data";
import { useMarketplaceData } from "./soko/useMarketplaceData";

export default function App() {
  const [screen, setScreen] = useState<Screen>("browse");
  const [mode, setMode] = useState<MarketplaceMode>("buyer");
  const [listing, setListing] = useState<Listing>(fallbackListings[0]);
  const [shop, setShop] = useState<Shop>(fallbackShops[0]);
  const [searchQuery, setSearchQuery] = useState("");
  const [profile, setProfile] = useState<ApiProfile | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [editProfileOpen, setEditProfileOpen] = useState(false);
  const [localUnread, setLocalUnread] = useState(true);

  const marketplace = useMarketplaceData(searchQuery, Boolean(profile));
  const currentShops = marketplace.shops.length > 0 ? marketplace.shops : fallbackShops;
  const currentListings = marketplace.listings.length > 0 ? marketplace.listings : fallbackListings;
  const activeShop = currentShops.find((item) => item.id === shop.id) ?? currentShops[0];
  const activeListing = currentListings.find((item) => item.id === listing.id) ?? listing;
  const chatShop = currentShops.find((item) => item.id === activeListing.shopId) ?? activeShop;
  const hasUnread = profile ? marketplace.notifications.some((item) => !item.read) : localUnread;

  useEffect(() => {
    api.getMe().then(setProfile).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (currentListings.length > 0 && !currentListings.some((item) => item.id === listing.id)) setListing(currentListings[0]);
  }, [currentListings, listing.id]);

  const navigate = (nextScreen: Screen) => {
    setScreen(nextScreen);
    window.scrollTo({ top: 0, behavior: "auto" });
  };

  const showBuyer = () => { setMode("buyer"); setSearchQuery(""); navigate("browse"); };
  const showSeller = () => { setMode("seller"); setSearchQuery(""); navigate("seller"); };
  const showAdmin = () => { setMode("admin"); setSearchQuery(""); navigate("seller"); };
  const openListing = (nextListing: Listing) => { setListing(nextListing); navigate("listing"); };
  const openShop = (nextShop: Shop) => { setShop(nextShop); setMode("buyer"); navigate("shop"); };
  const requireAuth = () => setAuthOpen(true);

  const markNotificationsRead = async () => {
    if (!profile) throw new Error("Authentication required");
    await api.markAllNotificationsRead();
    setLocalUnread(false);
  };

  const toggleFavorite = async (listingId: string, _nextValue?: boolean) => {
    if (!profile) { requireAuth(); return; }
    await api.toggleFavorite(listingId);
  };

  const authenticated = (nextProfile: ApiProfile) => {
    setProfile(nextProfile);
    setLocalUnread(false);
    if (nextProfile.role === "retailer") showSeller();
    else if (nextProfile.role === "admin") showAdmin();
  };

  const logout = async () => {
    try { await api.logout(); } catch { /* Clear local access even if the API is unavailable. */ }
    setProfile(null);
    setMode("buyer");
    navigate("browse");
    toast.success("You’ve been signed out");
  };

  const onNavigate = (nextScreen: Screen) => {
    if (nextScreen === "seller") showSeller();
    else if (nextScreen === "browse") showBuyer();
    else { setMode("buyer"); navigate(nextScreen); }
  };

  const content = mode === "admin" ? (
    <AdminDashboard />
  ) : mode === "seller" ? (
    <SellerDashboard searchQuery={searchQuery} profile={profile} listings={currentListings} shops={currentShops} orders={marketplace.orders} onSwitchToBuyer={showBuyer} onShopUpdated={marketplace.refresh} />
  ) : (
    <>
      {screen === "browse" && <Browse listings={currentListings} shops={currentShops} categories={marketplace.categories} profile={profile} searchQuery={searchQuery} onSearchChange={setSearchQuery} onOpenListing={openListing} onCheckout={(nextListing) => { setListing(nextListing); navigate("checkout"); }} onChat={(nextListing) => { if (nextListing) setListing(nextListing); navigate("chat"); }} onSell={showSeller} onRequireAuth={requireAuth} onFavoriteToggle={toggleFavorite} />}
      {screen === "listing" && <ListingDetail listing={activeListing} profile={profile} onRequireAuth={requireAuth} onFavoriteToggle={toggleFavorite} onBack={() => navigate("browse")} onChat={() => navigate("chat")} onShop={() => openShop(currentShops.find((item) => item.id === activeListing.shopId) ?? activeShop)} onCheckout={() => navigate("checkout")} onOpenListing={openListing} />}
      {screen === "shop" && <ShopProfile shop={activeShop} listings={currentListings} onBack={() => navigate("browse")} onOpenListing={openListing} onChat={() => navigate("chat")} />}
      {screen === "chat" && <Chat shop={chatShop} listing={activeListing} profile={profile} onBack={() => navigate("listing")} onRequireAuth={requireAuth} />}
      {screen === "checkout" && <Checkout listing={activeListing} profile={profile} onRequireAuth={requireAuth} onBack={() => navigate("listing")} onDone={() => { marketplace.refresh(); toast.success("Order created — payment status will update from the provider webhook."); navigate("orders"); }} />}
      {screen === "orders" && <Orders searchQuery={searchQuery} orders={marketplace.orders} onBrowse={showBuyer} />}
    </>
  );

  return (
    <>
      <AppShell mode={mode} screen={screen} searchQuery={searchQuery} hasUnread={hasUnread} notifications={marketplace.notifications} profile={profile} onSearchChange={setSearchQuery} onNavigate={onNavigate} onModeChange={setMode} onMarkNotificationsRead={markNotificationsRead} onOpenAuth={requireAuth} onOpenAdmin={showAdmin} onOpenEditProfile={() => setEditProfileOpen(true)} onLogout={logout}>
        <AnimatePresence mode="wait">
          <motion.div
            key={mode === "seller" ? "seller" : mode === "admin" ? "admin" : screen}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
          >
            {content}
          </motion.div>
        </AnimatePresence>
      </AppShell>
      <AuthDialog open={authOpen} onOpenChange={setAuthOpen} onAuthenticated={authenticated} />
      <EditProfileDialog open={editProfileOpen} profile={profile} onOpenChange={setEditProfileOpen} onUpdated={setProfile} />
      <Toaster position="bottom-center" closeButton />
    </>
  );
}
