import { AlertTriangle, Package, ShieldCheck, Store, Users } from "lucide-react";
import { toast } from "sonner";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { ApiError, api } from "@/services/api";

import { AdminListingsTable } from "./AdminListingsTable";
import { AdminUsersTable } from "./AdminUsersTable";
import { DisputeQueue } from "./DisputeQueue";
import { PayoutQueue } from "./PayoutQueue";
import { Eyebrow } from "./Shared";
import { ShopApprovalQueue } from "./ShopApprovalQueue";
import { StatCard } from "./StatCard";
import { useAdminData } from "./useAdminData";

export function AdminDashboard() {
  const { metrics, shops, users, listings, payouts, disputes, refresh } = useAdminData(true);

  const fail = (fallback: string) => (error: unknown) => toast.error(error instanceof ApiError ? error.message : fallback);
  const approveShop = (id: string) => api.approveShop(id).then(() => { toast.success("Shop approved"); refresh(); }).catch(fail("Couldn’t approve that shop"));
  const suspendShop = (id: string) => api.suspendShop(id).then(() => { toast.success("Shop suspended"); refresh(); }).catch(fail("Couldn’t suspend that shop"));
  const setListingStatus = (id: string, status: "active" | "hidden") => api.adminUpdateListing(id, { status }).then(() => { toast.success(status === "hidden" ? "Listing hidden" : "Listing restored"); refresh(); }).catch(fail("Couldn’t update that listing"));
  const approvePayout = (id: string) => api.updateAdminPayout(id, "approved").then(() => { toast.success("Payout approved"); refresh(); }).catch(fail("Couldn’t approve that payout"));
  const rejectPayout = (id: string) => api.updateAdminPayout(id, "rejected").then(() => { toast.success("Payout rejected"); refresh(); }).catch(fail("Couldn’t reject that payout"));
  const resolveDispute = (id: string, status: "resolved" | "rejected", note: string) => api.resolveDispute(id, { status, resolution_note: note || undefined }).then(() => { toast.success("Dispute updated"); refresh(); }).catch(fail("Couldn’t update that dispute"));

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-7 sm:px-5 sm:py-8">
      <section><div className="mb-2 flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-accent" aria-hidden="true" /><Eyebrow>Admin workspace</Eyebrow></div><h1 className="font-heading text-3xl font-bold leading-tight tracking-[-.035em] sm:text-[34px]">Admin dashboard</h1><p className="mt-1 font-body text-sm text-muted-foreground">Approvals, moderation, and marketplace health</p></section>

      <section aria-label="Marketplace metrics" className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard icon={Store} label="Shops" value={String(metrics?.total_shops ?? 0)} note="Total" tone="bg-primary/15 text-primary" />
        <StatCard icon={Package} label="Listings" value={String(metrics?.total_listings ?? 0)} note="Total" tone="bg-accent/15 text-accent" />
        <StatCard icon={Users} label="Users" value={String(metrics?.total_users ?? 0)} note="Total" tone="bg-secondary text-foreground" />
        <StatCard icon={ShieldCheck} label="Orders" value={String(metrics?.total_orders ?? 0)} note="Total" tone="bg-success/15 text-success" />
      </section>

      <Tabs defaultValue="shops" className="w-full">
        <TabsList className="h-auto w-full justify-start gap-1 overflow-x-auto rounded-lg bg-background p-1"><TabsTrigger value="shops" className="shrink-0 gap-1.5 rounded-md px-3 py-1.5 font-heading text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm"><Store className="h-3.5 w-3.5" aria-hidden="true" /> Shops{shops.length > 0 ? ` (${shops.length})` : ""}</TabsTrigger><TabsTrigger value="listings" className="shrink-0 gap-1.5 rounded-md px-3 py-1.5 font-heading text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm"><Package className="h-3.5 w-3.5" aria-hidden="true" /> Listings</TabsTrigger><TabsTrigger value="users" className="shrink-0 gap-1.5 rounded-md px-3 py-1.5 font-heading text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm"><Users className="h-3.5 w-3.5" aria-hidden="true" /> Users</TabsTrigger><TabsTrigger value="payouts" className="shrink-0 gap-1.5 rounded-md px-3 py-1.5 font-heading text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm"><ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" /> Payouts{payouts.length > 0 ? ` (${payouts.length})` : ""}</TabsTrigger><TabsTrigger value="disputes" className="shrink-0 gap-1.5 rounded-md px-3 py-1.5 font-heading text-xs data-[state=active]:bg-card data-[state=active]:shadow-sm"><AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" /> Disputes{disputes.length > 0 ? ` (${disputes.length})` : ""}</TabsTrigger></TabsList>
        <TabsContent value="shops" className="mt-4"><ShopApprovalQueue shops={shops} onApprove={approveShop} onSuspend={suspendShop} /></TabsContent>
        <TabsContent value="listings" className="mt-4"><AdminListingsTable listings={listings} onSetStatus={setListingStatus} /></TabsContent>
        <TabsContent value="users" className="mt-4"><AdminUsersTable users={users} /></TabsContent>
        <TabsContent value="payouts" className="mt-4"><PayoutQueue payouts={payouts} onApprove={approvePayout} onReject={rejectPayout} /></TabsContent>
        <TabsContent value="disputes" className="mt-4"><DisputeQueue disputes={disputes} onResolve={resolveDispute} /></TabsContent>
      </Tabs>
    </div>
  );
}
