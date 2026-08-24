import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Home, MapPin, MessageCircle, Package, Search, ShieldCheck, Store, UserRound } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { TooltipProvider } from "@/components/ui/tooltip";

import type { ApiProfile } from "@/services/api";

import type { MarketplaceMode, NotificationItem, Screen } from "./data";
import { ModeToggle } from "./ModeToggle";
import { NotificationPopover } from "./NotificationPopover";

interface AppShellProps {
  children: ReactNode;
  mode: MarketplaceMode;
  screen: Screen;
  searchQuery: string;
  hasUnread: boolean;
  notifications?: NotificationItem[];
  profile: ApiProfile | null;
  onSearchChange: (query: string) => void;
  onNavigate: (screen: Screen) => void;
  onModeChange: (mode: MarketplaceMode) => void;
  onMarkNotificationsRead: () => void | Promise<void>;
  onOpenAuth: () => void;
  onOpenAdmin: () => void;
  onOpenEditProfile: () => void;
  onLogout: () => void;
}

const buyerNav: Array<{ id: Screen; label: string; icon: typeof Home }> = [
  { id: "browse", label: "Browse", icon: Home },
  { id: "orders", label: "Orders", icon: Package },
  { id: "chat", label: "Messages", icon: MessageCircle },
];

function initials(name?: string) {
  return name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "GM";
}

export function AppShell({
  children,
  mode,
  screen,
  searchQuery,
  hasUnread,
  notifications,
  profile,
  onSearchChange,
  onNavigate,
  onModeChange,
  onMarkNotificationsRead,
  onOpenAuth,
  onOpenAdmin,
  onOpenEditProfile,
  onLogout,
}: AppShellProps) {
  const signedIn = Boolean(profile);
  const changeMode = (nextMode: MarketplaceMode) => {
    onModeChange(nextMode);
    onNavigate(nextMode === "seller" ? "seller" : "browse");
  };

  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 4);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <TooltipProvider delayDuration={400}>
      <div className="min-h-screen bg-background text-foreground">
        <header className={`sticky top-0 z-40 border-b bg-background/95 backdrop-blur-xl transition-colors duration-200 ${scrolled ? "border-border/70 shadow-sm" : "border-transparent shadow-none"}`}>
          <div className="mx-auto flex min-h-[72px] max-w-[1180px] flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
            <Button variant="ghost" className="group h-auto shrink-0 gap-2.5 rounded-xl p-0 hover:bg-transparent" onClick={() => onNavigate(mode === "seller" ? "seller" : "browse")} aria-label="Go to Soko home">
              <span className="relative flex h-9 w-9 items-center justify-center">
                <span className={`flex h-9 w-9 items-center justify-center rounded-[11px] font-heading text-lg font-bold text-background ${mode === "seller" ? "bg-primary" : "bg-foreground"}`}>S</span>
                <span className="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full bg-[hsl(var(--gold))] ring-2 ring-background" aria-hidden="true" />
              </span>
              <span className="hidden font-heading text-[21px] font-bold tracking-[-.03em] sm:block">Soko</span>
            </Button>

            <div className="relative order-3 min-w-full flex-1 sm:order-none sm:min-w-0 sm:max-w-[440px]">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
              <Input type="search" value={searchQuery} onChange={(event) => onSearchChange(event.target.value)} placeholder={screen === "orders" ? "Search your orders" : "Search products, shops, categories…"} className="h-10 rounded-full bg-card/80 pl-9 pr-4 text-sm" aria-label={screen === "orders" ? "Search your orders" : "Search marketplace"} />
            </div>

            <Button variant="secondary" size="sm" className="hidden h-9 gap-1.5 rounded-full px-3 text-xs text-muted-foreground md:inline-flex">
              <MapPin className="h-3.5 w-3.5 text-primary" aria-hidden="true" /> Nairobi
            </Button>

            {mode === "buyer" && (
              <nav aria-label="Primary navigation" className="order-2 ml-auto flex items-center gap-1 sm:order-none sm:ml-0">
                {buyerNav.map(({ id, label, icon: Icon }) => (
                  <Button key={id} variant={screen === id ? "secondary" : "ghost"} size="sm" className="gap-2 rounded-lg px-2.5 text-xs lg:px-3" onClick={() => onNavigate(id)}>
                    <Icon className="h-4 w-4" aria-hidden="true" />
                    <span className="hidden lg:inline">{label}</span>
                  </Button>
                ))}
              </nav>
            )}

            <div className="order-2 ml-auto flex items-center gap-1 sm:order-none sm:ml-auto">
              <NotificationPopover hasUnread={hasUnread} notifications={notifications} onMarkRead={onMarkNotificationsRead} />
              {signedIn ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-9 w-9 rounded-full p-0" aria-label="Open account menu">
                      <Avatar className="h-9 w-9 bg-accent/20 text-accent"><AvatarImage src={profile?.avatar_url ?? undefined} alt="" /><AvatarFallback className="bg-accent/20 font-heading text-[11px] font-semibold text-accent">{initials(profile?.full_name)}</AvatarFallback></Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56 rounded-2xl">
                    <DropdownMenuLabel className="font-heading text-xs">{profile?.full_name}<span className="mt-1 block font-body text-[11px] font-normal text-muted-foreground">{mode === "seller" ? "Seller account" : "Buyer account"}</span></DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onSelect={() => onNavigate("shop")}><Store className="h-3.5 w-3.5 text-primary" /> Store profile</DropdownMenuItem>
                    <DropdownMenuItem onSelect={onOpenEditProfile}><UserRound className="h-3.5 w-3.5" /> Account settings</DropdownMenuItem>
                    {profile?.role === "admin" && <DropdownMenuItem onSelect={onOpenAdmin}><ShieldCheck className="h-3.5 w-3.5 text-accent" /> Admin dashboard</DropdownMenuItem>}
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onSelect={onLogout}>Sign out</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button variant="ghost" className="h-9 w-9 rounded-full p-0" aria-label="Sign in or create account" onClick={onOpenAuth}>
                  <Avatar className="h-9 w-9 bg-accent/20 text-accent"><AvatarFallback className="bg-accent/20 font-heading text-[11px] font-semibold text-accent">GM</AvatarFallback></Avatar>
                </Button>
              )}
            </div>

            <ModeToggle mode={mode} onChange={changeMode} />
          </div>
        </header>

        <main>{children}</main>
        <footer className="border-t border-border/70 px-5 py-6 text-center text-[11px] text-muted-foreground"><span className="font-heading font-semibold text-foreground">Soko</span> · Local commerce, made simple · Nairobi</footer>
      </div>
    </TooltipProvider>
  );
}
