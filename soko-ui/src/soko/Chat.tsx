import { useEffect, useState, type FormEvent } from "react";
import { ChevronLeft, Phone, Send, ShieldCheck } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { api, type ApiProfile } from "@/services/api";
import { messages as fallbackMessages, shops as fallbackShops, type Listing, type Message, type Shop } from "./data";
import { normalizeMessage } from "./normalizers";

interface ChatProps {
  shop?: Shop;
  listing?: Listing;
  profile: ApiProfile | null;
  onBack: () => void;
  onRequireAuth: () => void;
}

const uiEase = [0.22, 1, 0.36, 1] as const;

export function Chat({ shop = fallbackShops[0], listing, profile, onBack, onRequireAuth }: ChatProps) {
  const shouldReduceMotion = useReducedMotion();
  const [messages, setMessages] = useState<Message[]>(() => fallbackMessages.map((message) => ({ ...message })));
  const [conversationId, setConversationId] = useState<string>();
  const [text, setText] = useState("");

  useEffect(() => {
    if (!profile) return;
    let active = true;
    api.getConversations().then(async (conversations) => {
      const existing = conversations.find((conversation) => conversation.shop_id === shop.id && (!listing || conversation.listing_id === listing.id));
      if (!existing) return;
      const conversation = await api.getConversation(existing.id);
      if (!active) return;
      setConversationId(conversation.id);
      if (conversation.messages) setMessages(conversation.messages.map((message) => normalizeMessage(message, profile.id)));
    }).catch(() => undefined);
    return () => { active = false; };
  }, [listing, profile, shop.id]);

  const send = async (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    const body = text.trim();
    if (!body) return;
    if (!profile) { onRequireAuth(); return; }
    setText("");
    try {
      if (!conversationId) {
        const conversation = await api.startConversation({ shop_id: shop.id, listing_id: listing?.id, body });
        setConversationId(conversation.id);
        setMessages((current) => [...current, { id: `local-${current.length + 1}`, from: "me", text: body, time: "now" }]);
      } else {
        const message = await api.sendMessage(conversationId, body);
        setMessages((current) => [...current, normalizeMessage(message, profile.id)]);
      }
    } catch {
      toast.error("Message could not be sent. Please try again.");
      setText(body);
    }
  };

  return <div className="mx-auto flex h-[70vh] max-w-2xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow"><div className="flex items-center gap-3 border-b border-border bg-card px-4 py-3"><Button type="button" variant="ghost" size="icon" onClick={onBack} className="h-8 w-8" aria-label="Back"><ChevronLeft className="h-[18px] w-[18px]" aria-hidden="true" /></Button><img src={shop.logo} alt={shop.name} loading="lazy" decoding="async" className="h-9 w-9 rounded-lg object-cover" /><div className="flex-1"><p className="flex items-center gap-1.5 font-heading text-sm font-medium">{shop.name}<ShieldCheck className="h-3.5 w-3.5 text-accent" aria-label="Verified retailer" /></p><p className="font-heading text-xs text-success">● Online now</p></div><Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={() => toast.info("Calling the retailer is available after account verification.")} aria-label="Call seller"><Phone className="h-4 w-4" aria-hidden="true" /></Button></div><div className="flex-1 space-y-3 overflow-y-auto bg-secondary/30 p-4" role="log" aria-live="polite" aria-label="Messages with seller">{messages.map((message) => <motion.div key={message.id} initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.22, ease: uiEase }} className={`flex ${message.from === "me" ? "justify-end" : "justify-start"}`}><div className={`max-w-[75%] rounded-2xl px-3.5 py-2 text-sm ${message.from === "me" ? "rounded-br-sm bg-primary text-primary-foreground" : "rounded-bl-sm border border-border bg-card"}`}><p className="font-body leading-relaxed">{message.text}</p><p className={`mt-1 font-heading text-[10px] ${message.from === "me" ? "text-primary-foreground/70" : "text-muted-foreground"}`}>{message.time}</p></div></motion.div>)}</div><form className="flex items-center gap-2 border-t border-border bg-card p-3" onSubmit={send}><Input value={text} onChange={(event) => setText(event.target.value)} placeholder="Message the seller…" className="rounded-full" aria-label="Message the seller" /><Button type="submit" size="icon" className="rounded-full" aria-label="Send message"><Send className="h-4 w-4" aria-hidden="true" /></Button></form></div>;
}
