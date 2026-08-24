import { useState, type FormEvent } from "react";
import { Loader2, LockKeyhole, Mail, UserRound } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { ApiError, api, type ApiProfile } from "@/services/api";

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAuthenticated: (profile: ApiProfile) => void;
}

type AuthMode = "login" | "register";

const uiEase = [0.22, 1, 0.36, 1] as const;

export function AuthDialog({ open, onOpenChange, onAuthenticated }: AuthDialogProps) {
  const shouldReduceMotion = useReducedMotion();
  const fieldTransition = shouldReduceMotion ? { duration: 0 } : { duration: 0.2, ease: uiEase };
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"buyer" | "retailer">("buyer");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const reset = () => {
    setEmail(""); setPassword(""); setFullName(""); setRole("buyer"); setError(""); setSubmitting(false);
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = mode === "login"
        ? await api.login(email.trim(), password)
        : await api.register({ email: email.trim(), password, full_name: fullName.trim(), role });
      const profile: ApiProfile = { ...result.profile, user_id: result.profile.user_id ?? email.trim() };
      onAuthenticated(profile);
      toast.success(mode === "login" ? "Welcome back to Soko" : "Your Soko account is ready");
      reset();
      onOpenChange(false);
    } catch (requestError) {
      const message = requestError instanceof ApiError ? requestError.message : "We couldn’t reach Soko right now.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const switchMode = () => {
    setMode((current) => current === "login" ? "register" : "login");
    setError("");
  };

  return (
    <Dialog open={open} onOpenChange={(nextOpen) => { if (!nextOpen) reset(); onOpenChange(nextOpen); }}>
      <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-md">
        <DialogHeader className="text-left"><p className="font-heading text-[11px] font-semibold uppercase tracking-[.14em] text-primary">Soko account</p><DialogTitle className="font-heading text-xl font-bold">{mode === "login" ? "Welcome back" : "Join your local marketplace"}</DialogTitle><DialogDescription className="font-body text-xs text-muted-foreground">{mode === "login" ? "Sign in to sync orders, favorites, chat, and seller tools." : "Create an account to shop local or open a retailer workspace."}</DialogDescription></DialogHeader>
        <form className="mt-2 space-y-4" onSubmit={submit} noValidate>
          <AnimatePresence initial={false}>
            {mode === "register" && (
              <motion.div key="full-name" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={fieldTransition} className="overflow-hidden">
                <div className="space-y-1.5"><Label htmlFor="auth-name" className="font-heading text-xs">Full name</Label><div className="relative"><UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input id="auth-name" value={fullName} onChange={(event) => setFullName(event.target.value)} className="pl-9" placeholder="Grace Mwangi" required /></div></div>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="space-y-1.5"><Label htmlFor="auth-email" className="font-heading text-xs">Email</Label><div className="relative"><Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input id="auth-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="pl-9" placeholder="you@example.com" required /></div></div>
          <div className="space-y-1.5"><Label htmlFor="auth-password" className="font-heading text-xs">Password</Label><div className="relative"><LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input id="auth-password" type="password" minLength={mode === "register" ? 8 : undefined} value={password} onChange={(event) => setPassword(event.target.value)} className="pl-9" placeholder={mode === "register" ? "At least 8 characters" : "Your password"} required /></div></div>
          <AnimatePresence initial={false}>
            {mode === "register" && (
              <motion.div key="role" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={fieldTransition} className="overflow-hidden">
                <div className="space-y-1.5"><Label htmlFor="auth-role" className="font-heading text-xs">I’m joining as</Label><Select value={role} onValueChange={(value) => setRole(value as "buyer" | "retailer")}><SelectTrigger id="auth-role" className="bg-background text-sm"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="buyer">Buyer</SelectItem><SelectItem value="retailer">Retailer</SelectItem></SelectContent></Select></div>
              </motion.div>
            )}
          </AnimatePresence>
          {error && <p role="alert" className="text-xs text-destructive">{error}</p>}
          <Button type="submit" className="w-full gap-2 rounded-lg font-heading text-xs" disabled={submitting}>{submitting && <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />}{mode === "login" ? "Sign in" : "Create account"}</Button>
          <p className="text-center font-body text-xs text-muted-foreground">{mode === "login" ? "New to Soko?" : "Already have an account?"} <Button type="button" variant="link" size="sm" className="h-auto p-0 font-heading text-xs text-primary" onClick={switchMode}>{mode === "login" ? "Create an account" : "Sign in"}</Button></p>
        </form>
      </DialogContent>
    </Dialog>
  );
}
