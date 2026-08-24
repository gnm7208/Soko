import { Users } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

import type { ApiAdminUser } from "@/services/api";

function initials(name?: string) {
  return name?.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase() || "?";
}

interface AdminUsersTableProps {
  users: ApiAdminUser[];
}

export function AdminUsersTable({ users }: AdminUsersTableProps) {
  return (
    <Card className="overflow-hidden rounded-2xl border-border bg-card shadow-none">
      <div className="border-b border-border px-4 py-4"><h2 className="font-heading text-base font-semibold">Users</h2><p className="mt-0.5 font-body text-xs text-muted-foreground">{users.length} accounts</p></div>
      {users.length === 0 ? <div className="px-4 py-10 text-center"><Users className="mx-auto h-6 w-6 text-muted-foreground" aria-hidden="true" /><p className="mt-2 font-heading text-xs font-semibold">No users yet</p></div> : <div className="divide-y divide-border">{users.map((user) => <div key={user.id} className="flex items-center gap-3 px-4 py-3"><Avatar className="h-8 w-8 bg-accent/20 text-accent"><AvatarImage src={user.avatar_url ?? undefined} alt="" /><AvatarFallback className="bg-accent/20 font-heading text-[10px] font-semibold text-accent">{initials(user.full_name)}</AvatarFallback></Avatar><div className="min-w-0 flex-1"><p className="font-heading text-xs font-semibold">{user.full_name}</p><p className="mt-0.5 truncate font-body text-[11px] text-muted-foreground">{user.user_id}{user.phone ? ` · ${user.phone}` : ""}</p></div><Badge variant="secondary" className="shrink-0 rounded-full text-[10px] capitalize">{user.role}</Badge></div>)}</div>}
    </Card>
  );
}
