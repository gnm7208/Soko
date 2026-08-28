import { useState, type FormEvent } from "react";
import { Banknote, CheckCircle2, ChevronLeft, CreditCard, Loader2, MapPin, Smartphone, Store, Truck } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Separator } from "@/components/ui/separator";

import { api, ApiError, type ApiProfile } from "@/services/api";
import { money, shops as fallbackShops, type DeliveryMethod, type Listing, type PaymentMethod, type Shop } from "./data";

interface CheckoutProps {
  listing: Listing;
  profile: ApiProfile | null;
  shops?: Shop[];
  onBack: () => void;
  onDone: () => void;
  onRequireAuth: () => void;
}

const paymentOptions: Array<{ id: PaymentMethod; label: string; description: string; icon: typeof Smartphone }> = [
  { id: "M-Pesa", label: "M-Pesa", description: "Pay via mobile money", icon: Smartphone },
  { id: "Card", label: "Card", description: "Visa · Mastercard", icon: CreditCard },
  { id: "Cash on delivery", label: "Cash on delivery", description: "Pay the rider", icon: Banknote },
];

function providerFor(payment: PaymentMethod): "stripe" | "flutterwave" | "paystack" | "cash" {
  if (payment === "M-Pesa") return "flutterwave";
  if (payment === "Card") return "stripe";
  return "cash";
}

export function Checkout({ listing, profile, shops = fallbackShops, onBack, onDone, onRequireAuth }: CheckoutProps) {
  const shop = shops.find((item) => item.id === listing.shopId) ?? fallbackShops[0];
  const [payment, setPayment] = useState<PaymentMethod>("M-Pesa");
  const [delivery, setDelivery] = useState<DeliveryMethod>("delivery");
  const [submitting, setSubmitting] = useState(false);
  const fee = delivery === "delivery" ? shop.deliveryFee : 0;
  const total = listing.price + fee;

  const submit = async (event: FormEvent<HTMLButtonElement>) => {
    event.preventDefault();
    if (!profile) { onRequireAuth(); return; }
    setSubmitting(true);
    try {
      const provider = providerFor(payment);
      const order = await api.createOrder({ shop_id: listing.shopId, items: [{ listing_id: listing.id, qty: 1 }], delivery_method: delivery, delivery_address: delivery === "delivery" ? "Kilimani, Nairobi" : undefined, payment_method: provider });
      if (provider !== "cash") {
        await api.createPaymentIntent({ order_id: order.id, provider });
        toast.info("Payment request created. We’ll update the order after provider confirmation.");
      } else {
        toast.info("Cash-on-delivery order created. Pay the rider when it arrives.");
      }
      onDone();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "We couldn’t place that order. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return <div className="mx-auto max-w-3xl space-y-6 px-4 py-6 sm:px-6 sm:py-8"><Button type="button" variant="ghost" size="sm" onClick={onBack} className="gap-1 text-muted-foreground"><ChevronLeft className="h-4 w-4" aria-hidden="true" /> Back</Button><h1 className="font-heading text-2xl font-bold">Checkout</h1><div className="grid gap-6 md:grid-cols-[minmax(0,1fr)_320px]"><div className="space-y-6"><Card className="rounded-2xl border-border p-5 shadow-none"><p className="mb-3 font-heading font-semibold">Delivery method</p><RadioGroup value={delivery} onValueChange={(value) => setDelivery(value as DeliveryMethod)} className="grid grid-cols-2 gap-3"><Label htmlFor="delivery-option" className={`flex cursor-pointer items-center gap-3 rounded-xl border p-3 text-left transition duration-150 active:scale-[0.97] ${delivery === "delivery" ? "border-primary bg-primary/5" : "hover:border-primary/40"}`}><RadioGroupItem value="delivery" id="delivery-option" className="sr-only" /><Truck className={`h-5 w-5 ${delivery === "delivery" ? "text-primary" : "text-muted-foreground"}`} aria-hidden="true" /><span><span className="block font-heading text-sm font-medium">Delivery</span><span className="block font-body text-xs text-muted-foreground">{money(shop.deliveryFee)}</span></span></Label><Label htmlFor="pickup-option" className={`flex cursor-pointer items-center gap-3 rounded-xl border p-3 text-left transition duration-150 active:scale-[0.97] ${delivery === "pickup" ? "border-primary bg-primary/5" : "hover:border-primary/40"}`}><RadioGroupItem value="pickup" id="pickup-option" className="sr-only" /><Store className={`h-5 w-5 ${delivery === "pickup" ? "text-primary" : "text-muted-foreground"}`} aria-hidden="true" /><span><span className="block font-heading text-sm font-medium">Pickup</span><span className="block font-body text-xs text-muted-foreground">Free</span></span></Label></RadioGroup>{delivery === "delivery" && <div className="mt-3 flex items-center gap-2 rounded-lg bg-secondary/50 p-3 font-body text-sm text-muted-foreground"><MapPin className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" /> Kilimani, Nairobi · <Button type="button" variant="link" size="sm" className="h-auto p-0 font-heading text-xs text-accent" onClick={() => toast.info("Address editing will be connected to your profile.")}>Change</Button></div>}</Card><Card className="rounded-2xl border-border p-5 shadow-none"><p className="mb-3 font-heading font-semibold">Payment</p><RadioGroup value={payment} onValueChange={(value) => setPayment(value as PaymentMethod)} className="space-y-2">{paymentOptions.map(({ id, label, description, icon: Icon }) => <Label key={id} htmlFor={`payment-${id}`} className={`flex cursor-pointer items-center gap-3 rounded-xl border p-3 text-left transition duration-150 active:scale-[0.97] ${payment === id ? "border-primary bg-primary/5" : "hover:border-primary/40"}`}><RadioGroupItem value={id} id={`payment-${id}`} className="sr-only" /><Icon className={`h-5 w-5 ${payment === id ? "text-primary" : "text-muted-foreground"}`} aria-hidden="true" /><span className="flex-1"><span className="block font-heading text-sm font-medium">{label}</span><span className="block font-body text-xs text-muted-foreground">{description}</span></span><span className={`flex h-4 w-4 items-center justify-center rounded-full border-2 ${payment === id ? "border-primary" : "border-border"}`} aria-hidden="true"><span className={`h-2 w-2 rounded-full bg-primary transition-transform duration-150 ${payment === id ? "scale-100" : "scale-0"}`} /></span></Label>)}</RadioGroup></Card></div><Card className="h-fit rounded-2xl border-border p-5 shadow-none"><p className="mb-3 font-heading font-semibold">Order summary</p><div className="flex gap-3"><img src={listing.image} alt={listing.title} loading="lazy" decoding="async" className="h-16 w-16 rounded-lg object-cover" /><div className="min-w-0 font-body text-sm"><p className="line-clamp-2">{listing.title}</p><p className="mt-1 text-xs text-muted-foreground">{shop.name}</p></div></div><Separator className="my-4" /><div className="space-y-2 font-body text-sm"><div className="flex justify-between"><span className="text-muted-foreground">Subtotal</span><span>{money(listing.price)}</span></div><div className="flex justify-between"><span className="text-muted-foreground">Delivery</span><span>{fee ? money(fee) : "Free"}</span></div></div><Separator className="my-4" /><div className="flex justify-between font-heading text-lg font-semibold"><span>Total</span><span className="text-primary">{money(total)}</span></div><Button type="button" size="lg" className="mt-4 w-full gap-2 rounded-lg font-heading text-xs" onClick={submit} disabled={submitting}>{submitting && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} {profile ? "Place order" : "Sign in to place order"}</Button><p className="mt-2 flex items-center justify-center gap-1 font-body text-xs text-muted-foreground"><CheckCircle2 className="h-3.5 w-3.5 text-success" aria-hidden="true" /> Protected by Soko buyer guarantee</p></Card></div></div>;
}
