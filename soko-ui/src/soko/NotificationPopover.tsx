import { Bell, CheckCircle2, Inbox, PackageCheck, Truck } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

import type { NotificationItem } from "./data";

interface NotificationPopoverProps {
  hasUnread: boolean;
  notifications?: NotificationItem[];
  onMarkRead: () => void | Promise<void>;
}

function NotificationIcon({ type }: { type: string }) {
  if (type === "message") return <PackageCheck className="h-3.5 w-3.5" aria-hidden="true" />;
  if (type === "promotion") return <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />;
  return <Truck className="h-3.5 w-3.5" aria-hidden="true" />;
}

const fallbackNotifications: NotificationItem[] = [
  { id: "demo-delivery", type: "order", title: "Your order is on the way", body: "SOKO-2481 is arriving in about 12 minutes.", read: false },
  { id: "demo-delivered", type: "order", title: "Order delivered", body: "Your produce basket was delivered yesterday.", read: true },
  { id: "demo-message", type: "message", title: "Seller reply received", body: "Mama Njeri Electronics replied to your chat.", read: true },
];

export function NotificationPopover({ hasUnread, notifications, onMarkRead }: NotificationPopoverProps) {
  const items = notifications ?? fallbackNotifications;
  const markRead = async () => {
    try {
      await onMarkRead();
      toast.success("Notifications marked as read");
    } catch {
      toast.info("Sign in to sync notification status");
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild><Button variant="ghost" size="icon" className="relative rounded-full" aria-label="Open notifications"><Bell className="h-[17px] w-[17px]" aria-hidden="true" />{hasUnread && <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary ring-2 ring-background" aria-hidden="true" />}</Button></PopoverTrigger>
      <PopoverContent align="end" className="w-[310px] overflow-hidden rounded-2xl p-0"><div className="flex items-center justify-between border-b border-border px-4 py-3"><p className="font-heading text-sm font-semibold">Notifications</p>{hasUnread && <span className="rounded-full bg-primary/10 px-2.5 py-1 font-heading text-[10px] font-semibold text-primary">{items.filter((item) => !item.read).length || 1} new</span>}</div><div className="space-y-1 p-2">{items.length === 0 ? <div className="px-3 py-8 text-center"><Inbox className="mx-auto h-5 w-5 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">You’re all caught up</p><p className="mt-1 font-body text-[11px] text-muted-foreground">New order and chat updates will appear here.</p></div> : items.slice(0, 4).map((item) => <Button key={item.id} variant="ghost" className={`h-auto w-full justify-start gap-3 rounded-xl p-3 text-left hover:bg-background ${!item.read ? "bg-primary/[.07] hover:bg-primary/[.12]" : ""}`}><span className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${item.type === "message" ? "bg-accent/15 text-accent" : item.read ? "bg-success/15 text-success" : "bg-primary/15 text-primary"}`}><NotificationIcon type={item.type} /></span><span className="min-w-0"><span className="block font-heading text-[12px] font-semibold">{item.title}</span><span className="mt-0.5 block text-[11px] leading-snug text-muted-foreground">{item.body}</span></span></Button>)}</div><Button variant="link" size="sm" className="m-2 px-1.5 font-heading text-[11px] text-accent" onClick={markRead} disabled={!hasUnread}>Mark all as read</Button></PopoverContent>
    </Popover>
  );
}
