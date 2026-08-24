import { useEffect, useState, type FormEvent } from "react";
import { Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import type { Listing } from "./data";

export interface NewListingValues {
  title: string;
  price: number;
  category: Listing["category"];
  condition: Listing["condition"];
}

interface NewListingDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (values: NewListingValues) => void;
}

export function NewListingDialog({ open, onOpenChange, onSubmit }: NewListingDialogProps) {
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState<Listing["category"]>("Electronics");
  const [condition, setCondition] = useState<Listing["condition"]>("New");
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) setError("");
  }, [open]);

  const close = (nextOpen: boolean) => {
    if (!nextOpen) {
      setTitle(""); setPrice(""); setCategory("Electronics"); setCondition("New"); setError("");
    }
    onOpenChange(nextOpen);
  };

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const numericPrice = Number(price);
    if (!title.trim()) { setError("Add a product name to save this draft."); return; }
    if (!Number.isFinite(numericPrice) || numericPrice <= 0) { setError("Enter a price greater than zero."); return; }
    onSubmit({ title: title.trim(), price: numericPrice, category, condition });
    close(false);
  };

  return (
    <Dialog open={open} onOpenChange={close}>
      <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-md">
        <DialogHeader className="text-left"><p className="font-heading text-[11px] font-semibold uppercase tracking-[.13em] text-primary">Seller workspace</p><DialogTitle className="mt-1 font-heading text-xl font-bold">Create new listing</DialogTitle><DialogDescription className="mt-1 font-body text-xs text-muted-foreground">Save a draft now and publish when it’s ready.</DialogDescription></DialogHeader>
        <form className="mt-2 space-y-4" onSubmit={submit} noValidate>
          <div className="space-y-1.5"><Label htmlFor="draft-title" className="font-heading text-xs">Product name</Label><Input id="draft-title" value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. USB-C Fast Charger" aria-describedby={error ? "draft-error" : undefined} autoFocus /></div>
          <div className="grid gap-3 sm:grid-cols-2"><div className="space-y-1.5"><Label htmlFor="draft-price" className="font-heading text-xs">Price (KSh)</Label><Input id="draft-price" type="number" min="1" inputMode="numeric" value={price} onChange={(event) => setPrice(event.target.value)} placeholder="2500" aria-describedby={error ? "draft-error" : undefined} /></div><div className="space-y-1.5"><Label htmlFor="draft-category" className="font-heading text-xs">Category</Label><Select value={category} onValueChange={(value) => setCategory(value as Listing["category"])}><SelectTrigger id="draft-category" className="h-9 bg-background text-sm"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="Electronics">Electronics</SelectItem><SelectItem value="Fashion">Fashion</SelectItem><SelectItem value="Home">Home</SelectItem><SelectItem value="Services">Services</SelectItem></SelectContent></Select></div></div>
          <div className="space-y-1.5"><Label htmlFor="draft-condition" className="font-heading text-xs">Condition</Label><Select value={condition} onValueChange={(value) => setCondition(value as Listing["condition"])}><SelectTrigger id="draft-condition" className="h-9 bg-background text-sm"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="New">New</SelectItem><SelectItem value="Used">Used</SelectItem></SelectContent></Select></div>
          {error && <p id="draft-error" role="alert" className="text-xs text-destructive">{error}</p>}
          <DialogFooter className="gap-2 border-t border-border pt-4 sm:justify-end"><Button type="button" variant="ghost" size="sm" className="font-heading text-xs text-muted-foreground" onClick={() => close(false)}>Cancel</Button><Button type="submit" size="sm" className="gap-2 rounded-lg font-heading text-xs"><Save className="h-3.5 w-3.5" aria-hidden="true" /> Save draft</Button></DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
