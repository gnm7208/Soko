import type { LucideIcon } from "lucide-react";
import { Apple, Baby, Car, Grid2X2, Shirt, Smartphone, Sofa, Sparkles, Wrench } from "lucide-react";

import { Button } from "@/components/ui/button";

import { type Category } from "./data";

const iconMap: Record<string, LucideIcon> = {
  Smartphone,
  Shirt,
  Sofa,
  Apple,
  Sparkles,
  Car,
  Wrench,
  Baby,
};

interface CategoryChipsProps {
  categories: Category[];
  activeCategory: string;
  onChange: (category: string) => void;
}

export function CategoryChips({ categories, activeCategory, onChange }: CategoryChipsProps) {
  return (
    <div className="flex flex-wrap gap-2" aria-label="Browse categories">
      <Button type="button" variant={activeCategory === "All" ? "default" : "outline"} className={`h-10 rounded-full px-3.5 text-[11px] font-medium ${activeCategory === "All" ? "border-primary bg-primary text-primary-foreground hover:bg-primary/90" : "bg-card hover:border-primary/50 hover:bg-secondary"}`} onClick={() => onChange("All")} aria-pressed={activeCategory === "All"}>
        <Grid2X2 className="h-3.5 w-3.5" aria-hidden="true" /> All
      </Button>
      {categories.map((category) => {
        const Icon = iconMap[category.icon] ?? Sparkles;
        const isActive = activeCategory === category.name;
        return <Button key={category.id} type="button" variant={isActive ? "default" : "outline"} className={`h-10 rounded-full px-3.5 text-[11px] font-medium ${isActive ? "border-primary bg-primary text-primary-foreground hover:bg-primary/90" : "bg-card hover:border-primary/50 hover:bg-secondary"}`} onClick={() => onChange(category.name)} aria-pressed={isActive}><Icon className={`h-3.5 w-3.5 ${isActive ? "text-primary-foreground" : "text-accent"}`} aria-hidden="true" />{category.name}</Button>;
      })}
    </div>
  );
}
