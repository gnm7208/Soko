import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  delta?: string;
  tone: string;
  note?: string;
}

export function StatCard({ icon: Icon, label, value, delta, tone, note }: StatCardProps) {
  return (
    <Card className="rounded-2xl border-border bg-card p-4 shadow-none">
      <div className="flex items-center justify-between"><span className={`flex h-9 w-9 items-center justify-center rounded-lg ${tone}`}><Icon className="h-[17px] w-[17px]" aria-hidden="true" /></span>{delta ? <span className="inline-flex items-center gap-0.5 font-heading text-[11px] font-semibold text-success"><ArrowUpRight className="h-3 w-3" aria-hidden="true" />{delta}</span> : <span className="font-heading text-[11px] font-medium text-muted-foreground">{note}</span>}</div>
      <p className="mt-3 font-heading text-[23px] font-bold tracking-[-.03em]">{value}</p>
      <p className="mt-0.5 font-body text-xs text-muted-foreground">{label}</p>
    </Card>
  );
}
