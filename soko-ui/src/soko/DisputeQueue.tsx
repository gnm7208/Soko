import { useState } from "react";
import { ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

import type { ApiDispute } from "@/services/api";

interface DisputeQueueProps {
  disputes: ApiDispute[];
  onResolve: (id: string, status: "resolved" | "rejected", note: string) => void;
}

export function DisputeQueue({ disputes, onResolve }: DisputeQueueProps) {
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [status, setStatus] = useState<"resolved" | "rejected">("resolved");
  const [note, setNote] = useState("");

  const openResolve = (id: string) => { setResolvingId(id); setStatus("resolved"); setNote(""); };
  const submit = () => { if (resolvingId) onResolve(resolvingId, status, note); setResolvingId(null); };

  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><h2 className="font-heading text-base font-semibold">Disputes</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">Open issues raised by buyers and sellers</p></div>
      {disputes.length === 0 ? <div className="px-4 py-10 text-center"><ShieldAlert className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No open disputes</p></div> : <div className="divide-y divide-border">{disputes.map((dispute) => <div key={dispute.id} className="flex items-start gap-3 px-4 py-3.5"><div className="min-w-0 flex-1"><p className="font-heading text-xs font-semibold">Order {dispute.order_id}</p><p className="mt-1 font-body text-[11px] leading-relaxed text-muted-foreground">{dispute.reason}</p></div><Button type="button" size="sm" variant="outline" className="h-8 shrink-0 px-2.5 text-[10px]" onClick={() => openResolve(dispute.id)}>Resolve</Button></div>)}</div>}

      <Dialog open={resolvingId !== null} onOpenChange={(open) => !open && setResolvingId(null)}>
        <DialogContent className="rounded-2xl border-border bg-card p-5 sm:max-w-sm">
          <DialogHeader className="text-left"><DialogTitle className="font-heading text-lg font-bold">Resolve dispute</DialogTitle><DialogDescription className="font-body text-xs text-muted-foreground">Record the outcome and an optional note for the record.</DialogDescription></DialogHeader>
          <div className="mt-2 space-y-4">
            <div className="space-y-1.5"><Label className="font-heading text-xs">Outcome</Label><Select value={status} onValueChange={(value) => setStatus(value as "resolved" | "rejected")}><SelectTrigger className="bg-background text-sm"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="resolved">Resolved</SelectItem><SelectItem value="rejected">Rejected</SelectItem></SelectContent></Select></div>
            <div className="space-y-1.5"><Label className="font-heading text-xs">Resolution note</Label><Textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="What happened and how it was resolved…" className="min-h-[88px] text-sm" /></div>
            <Button type="button" className="w-full rounded-lg font-heading text-xs" onClick={submit}>Save resolution</Button>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
