import { useEffect, useState, type FormEvent } from "react";
import { Camera, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { ApiError, api, type ApiProfile } from "@/services/api";

interface EditProfileDialogProps {
  open: boolean;
  profile: ApiProfile | null;
  onOpenChange: (open: boolean) => void;
  onUpdated: (profile: ApiProfile) => void;
}

function initials(name?: string) {
  return name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "?";
}

export function EditProfileDialog({ open, profile, onOpenChange, onUpdated }: EditProfileDialogProps) {
  const [fullName, setFullName] = useState(profile?.full_name ?? "");
  const [phone, setPhone] = useState(profile?.phone ?? "");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) { setFullName(profile?.full_name ?? ""); setPhone(profile?.phone ?? ""); setAvatarFile(null); setError(""); }
  }, [open, profile]);

  useEffect(() => {
    if (!avatarFile) { setAvatarPreview(null); return; }
    const url = URL.createObjectURL(avatarFile);
    setAvatarPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [avatarFile]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!profile) return;
    setError("");
    setSubmitting(true);
    try {
      let updated = profile;
      if (avatarFile) updated = await api.uploadAvatar(avatarFile);
      if (fullName !== profile.full_name || phone !== (profile.phone ?? "")) {
        updated = await api.updateProfile({ full_name: fullName, phone: phone || undefined });
      }
      onUpdated(updated);
      toast.success("Profile updated");
      onOpenChange(false);
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Couldn’t update your profile.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-sm">
        <DialogHeader className="text-left"><p className="font-heading text-[11px] font-semibold uppercase tracking-[.14em] text-primary">Account settings</p><DialogTitle className="font-heading text-xl font-bold">Edit profile</DialogTitle><DialogDescription className="font-body text-xs text-muted-foreground">Update your photo and contact details.</DialogDescription></DialogHeader>
        <form className="mt-2 space-y-4" onSubmit={submit}>
          <div className="flex items-center gap-3">
            <Avatar className="h-16 w-16 bg-accent/20 text-accent"><AvatarImage src={avatarPreview ?? profile?.avatar_url ?? undefined} alt="" /><AvatarFallback className="bg-accent/20 font-heading text-lg font-semibold text-accent">{initials(profile?.full_name)}</AvatarFallback></Avatar>
            <label className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 font-heading text-xs text-muted-foreground hover:border-primary/40">
              <Camera className="h-3.5 w-3.5" aria-hidden="true" /> Change photo
              <input type="file" accept="image/png,image/jpeg,image/webp" className="sr-only" onChange={(event) => setAvatarFile(event.target.files?.[0] ?? null)} />
            </label>
          </div>
          <div className="space-y-1.5"><Label htmlFor="edit-name" className="font-heading text-xs">Full name</Label><Input id="edit-name" value={fullName} onChange={(event) => setFullName(event.target.value)} required /></div>
          <div className="space-y-1.5"><Label htmlFor="edit-phone" className="font-heading text-xs">Phone</Label><Input id="edit-phone" value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="+254 7xx xxx xxx" /></div>
          {error && <p role="alert" className="text-xs text-destructive">{error}</p>}
          <Button type="submit" className="w-full gap-2 rounded-lg font-heading text-xs" disabled={submitting}>{submitting && <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />}Save changes</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
