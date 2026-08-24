import { useState } from "react";
import { Check, ChevronDown, Flag, MessageCircle, Radio, Receipt } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

import { ApiError, api } from "@/services/api";
import type { Order } from "./data";
import { money } from "./data";
import { DeliveryMap } from "./DeliveryMap";
import { OrderTracker } from "./OrderTracker";
import { StatusBadge } from "./Shared";

interface OrderCardProps {
  order: Order;
  expanded: boolean;
  featured?: boolean;
  onToggle: (id: string) => void;
  onDeliver?: (id: string) => void;
}

const uiEase = [0.22, 1, 0.36, 1] as const;

export function OrderCard({ order, expanded, featured = false, onToggle, onDeliver }: OrderCardProps) {
  const shouldReduceMotion = useReducedMotion();
  const [reportOpen, setReportOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const markDelivered = () => {
    onDeliver?.(order.id);
    toast.success("Order marked as delivered");
  };

  const submitReport = async () => {
    if (reason.trim().length < 5) { toast.error("Tell us a bit more about the issue."); return; }
    setSubmitting(true);
    try {
      await api.createDispute({ order_id: order.id, reason: reason.trim() });
      toast.success("Report sent — our team will follow up.");
      setReportOpen(false);
      setReason("");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Couldn’t send that report. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card className={`overflow-hidden rounded-2xl border-border bg-card shadow ${featured ? "border-primary/25 shadow-lg" : ""}`}>
      {featured && <div className="flex items-center justify-between border-b border-border bg-background px-5 py-3"><div className="flex items-center gap-2"><span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/15 text-primary"><Radio className="h-3 w-3" aria-hidden="true" /></span><span className="font-heading text-[10px] font-bold uppercase tracking-[.14em] text-primary">Tracking now</span></div><span className="font-heading text-[10px] text-muted-foreground">Updated a moment ago</span></div>}
      <Button type="button" variant="ghost" className="h-auto w-full items-start justify-start gap-4 rounded-none p-4 text-left hover:bg-background/70 sm:p-5" onClick={() => onToggle(order.id)} aria-expanded={expanded} aria-controls={`order-details-${order.id}`}>
        <img src={order.image} alt={order.listingTitle} loading="lazy" decoding="async" className={`${featured ? "h-[76px] w-[76px]" : "h-16 w-16"} shrink-0 rounded-xl object-cover`} />
        <span className="min-w-0 flex-1">
          <span className="flex flex-wrap items-center gap-2"><span className={`font-heading font-semibold leading-tight ${featured ? "text-[15px]" : "text-[13px]"}`}>{order.listingTitle}</span><StatusBadge status={order.status} /></span>
          <span className="mt-1 block font-body text-[11px] text-muted-foreground">{order.shopName} · {order.id}</span>
          <span className="mt-2 block font-body text-[11px] text-muted-foreground sm:hidden">{order.date} · {order.payment}</span>
          {featured && <span className="mt-3 block font-heading text-[13px] font-semibold text-primary">{money(order.total)} <span className="font-body text-[11px] font-normal text-muted-foreground">· {order.payment}</span></span>}
        </span>
        <span className="hidden shrink-0 text-right sm:block"><span className="block font-heading text-sm font-semibold text-primary">{money(order.total)}</span><span className="mt-1 block font-body text-[10px] text-muted-foreground">{order.status === "Delivered" ? "Completed" : order.eta}</span></span>
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-background text-muted-foreground"><ChevronDown className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`} aria-hidden="true" /></span>
      </Button>
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            key="details"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.25, ease: uiEase }}
            className="overflow-hidden"
          >
            <div id={`order-details-${order.id}`} className="border-t border-border px-5 pb-5 pt-5"><div className={featured ? "grid gap-5 lg:grid-cols-[1fr_350px]" : ""}><div><div className="flex items-start justify-between gap-4"><div><p className="font-heading text-[12px] font-semibold">{order.status === "Delivered" ? "Delivery complete" : order.eta ?? "Order is being prepared"}</p><p className="mt-1 font-body text-[11px] text-muted-foreground">{order.status === "Delivered" ? "Thanks for shopping local." : "Your rider is on the way to Kilimani."}</p></div>{featured && order.status !== "Delivered" && <Button type="button" variant="outline" size="sm" className="h-8 shrink-0 gap-1.5 border-success/35 bg-success/10 px-3 font-heading text-[10px] text-success" onClick={markDelivered}><Check className="h-3.5 w-3.5" aria-hidden="true" /> Mark as delivered</Button>}</div><OrderTracker order={order} compact={!featured} /><div className="mt-5 flex flex-wrap gap-2"><Button type="button" variant="outline" size="sm" className="h-8 gap-1.5 font-heading text-[10px] text-muted-foreground" onClick={() => toast.info(`Opening chat with ${order.shopName}`)}><MessageCircle className="h-3.5 w-3.5 text-accent" aria-hidden="true" /> Message seller</Button><Button type="button" variant="outline" size="sm" className="h-8 gap-1.5 font-heading text-[10px] text-muted-foreground" onClick={() => toast.info(`Receipt for ${order.id} is ready`)}><Receipt className="h-3.5 w-3.5 text-accent" aria-hidden="true" /> View receipt</Button><Button type="button" variant="outline" size="sm" className="h-8 gap-1.5 font-heading text-[10px] text-muted-foreground" onClick={() => setReportOpen(true)}><Flag className="h-3.5 w-3.5 text-destructive" aria-hidden="true" /> Report a problem</Button></div></div>{featured && <DeliveryMap order={order} />}</div></div>
          </motion.div>
        )}
      </AnimatePresence>

      <Dialog open={reportOpen} onOpenChange={(open) => { setReportOpen(open); if (!open) setReason(""); }}>
        <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-sm">
          <DialogHeader className="text-left"><DialogTitle className="font-heading text-lg font-bold">Report a problem</DialogTitle><DialogDescription className="font-body text-xs text-muted-foreground">Tell us what went wrong with {order.listingTitle}. Our team will review it.</DialogDescription></DialogHeader>
          <div className="mt-2 space-y-4">
            <Textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Item arrived damaged, wrong item, missing parts…" className="min-h-[88px] text-sm" />
            <Button type="button" className="w-full rounded-lg font-heading text-xs" onClick={submitReport} disabled={submitting}>Send report</Button>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
