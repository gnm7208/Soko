import { useEffect, useState, type FormEvent } from "react";
import { Camera, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

import { ApiError, api, type ApiShop } from "@/services/api";
import type { Shop } from "./data";

interface ShopSettingsDialogProps {
  open: boolean;
  /** Omit to render in "create your shop" mode instead of editing an existing one. */
  shop?: Shop;
  onOpenChange: (open: boolean) => void;
  onUpdated: () => void;
  onCreated?: (shop: ApiShop) => void;
}

export function ShopSettingsDialog({ open, shop, onOpenChange, onUpdated, onCreated }: ShopSettingsDialogProps) {
  const isCreate = !shop;
  const [name, setName] = useState(shop?.name ?? "");
  const [category, setCategory] = useState(shop?.category ?? "");
  const [address, setAddress] = useState(shop?.address ?? "");
  const [description, setDescription] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) { setName(shop?.name ?? ""); setCategory(shop?.category ?? ""); setAddress(shop?.address ?? ""); setLogoFile(null); setCoverFile(null); setError(""); }
  }, [open, shop]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (isCreate) {
        const created = await api.createShop({ name, category, address: address || undefined, description: description || undefined });
        if (logoFile) await api.uploadShopImage(created.id, logoFile, "logo");
        if (coverFile) await api.uploadShopImage(created.id, coverFile, "cover");
        toast.success("Shop created — pending approval");
        onCreated?.(created);
      } else {
        await api.updateShop(shop.id, { name, category, address, description: description || undefined });
        if (logoFile) await api.uploadShopImage(shop.id, logoFile, "logo");
        if (coverFile) await api.uploadShopImage(shop.id, coverFile, "cover");
        toast.success("Shop settings saved");
        onUpdated();
      }
      onOpenChange(false);
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Couldn’t save your shop settings.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-md">
        <DialogHeader className="text-left"><p className="font-heading text-[11px] font-semibold uppercase tracking-[.14em] text-primary">Shop settings</p><DialogTitle className="font-heading text-xl font-bold">{isCreate ? "Create your shop" : "Edit your shop"}</DialogTitle><DialogDescription className="font-body text-xs text-muted-foreground">{isCreate ? "Set up your storefront — you can add photos now or later." : `Update how buyers see ${shop.name}.`}</DialogDescription></DialogHeader>
        <form className="mt-2 space-y-4" onSubmit={submit}>
          <div className="flex gap-3">
            <label className="flex flex-1 cursor-pointer flex-col items-center gap-1.5 rounded-xl border border-dashed border-border px-3 py-4 text-center font-heading text-[11px] text-muted-foreground hover:border-primary/40">
              <Camera className="h-4 w-4" aria-hidden="true" /> {logoFile ? logoFile.name : "Logo"}
              <input type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" onChange={(event) => setLogoFile(event.target.files?.[0] ?? null)} />
            </label>
            <label className="flex flex-1 cursor-pointer flex-col items-center gap-1.5 rounded-xl border border-dashed border-border px-3 py-4 text-center font-heading text-[11px] text-muted-foreground hover:border-primary/40">
              <Camera className="h-4 w-4" aria-hidden="true" /> {coverFile ? coverFile.name : "Cover photo"}
              <input type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" onChange={(event) => setCoverFile(event.target.files?.[0] ?? null)} />
            </label>
          </div>
          <div className="space-y-1.5"><Label htmlFor="shop-name" className="font-heading text-xs">Shop name</Label><Input id="shop-name" value={name} onChange={(event) => setName(event.target.value)} required /></div>
          <div className="space-y-1.5"><Label htmlFor="shop-category" className="font-heading text-xs">Category</Label><Input id="shop-category" value={category} onChange={(event) => setCategory(event.target.value)} required /></div>
          <div className="space-y-1.5"><Label htmlFor="shop-address" className="font-heading text-xs">Address</Label><Input id="shop-address" value={address} onChange={(event) => setAddress(event.target.value)} /></div>
          <div className="space-y-1.5"><Label htmlFor="shop-description" className="font-heading text-xs">Description</Label><Textarea id="shop-description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Tell buyers what you sell…" className="min-h-[72px] text-sm" /></div>
          {error && <p role="alert" className="text-xs text-destructive">{error}</p>}
          <Button type="submit" className="w-full gap-2 rounded-lg font-heading text-xs" disabled={submitting}>{submitting && <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />}{isCreate ? "Create shop" : "Save changes"}</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
