import { MoreHorizontal, Pencil, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

import type { SellerListing } from "./data";

export type ListingAction = "edit" | "promote";

interface ListingActionsMenuProps {
  listing: SellerListing;
  onAction: (action: ListingAction, listing: SellerListing) => void;
}

export function ListingActionsMenu({ listing, onAction }: ListingActionsMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild><Button type="button" variant="ghost" size="icon" className="h-8 w-8 rounded-full text-muted-foreground" aria-label={`More actions for ${listing.title}`}><MoreHorizontal className="h-4 w-4" aria-hidden="true" /></Button></DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-36 rounded-xl">
        <DropdownMenuItem onSelect={() => onAction("edit", listing)}><Pencil className="h-3.5 w-3.5" /> Edit listing</DropdownMenuItem>
        <DropdownMenuItem onSelect={() => onAction("promote", listing)}><Sparkles className="h-3.5 w-3.5 text-primary" /> Promote</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
