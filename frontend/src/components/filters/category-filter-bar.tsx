"use client";

import { FaBolt, FaCut, FaDog, FaHome, FaSearch, FaStethoscope, FaTree } from "react-icons/fa";

import { CategoryDefinition } from "@/lib/constants/categories";
import { cn } from "@/lib/utils/cn";

const CATEGORY_ICONS = {
  veterinarias: FaStethoscope,
  "refugios-albergues": FaHome,
  "parques-pet-friendly": FaTree,
  "emergencias-veterinarias": FaBolt,
  guarderias: FaDog,
  peluquerias: FaCut,
  "mascotas-perdidas": FaSearch,
} as const;

interface CategoryFilterBarProps {
  categories: CategoryDefinition[];
  selectedCategory: string;
  onSelect: (value: string) => void;
}

export function CategoryFilterBar({
  categories,
  selectedCategory,
  onSelect,
}: CategoryFilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3" aria-label="Filtros por categoría">
      {categories.filter((category) => category.kind === "place").map((category) => (
        (() => {
          const Icon = CATEGORY_ICONS[category.slug as keyof typeof CATEGORY_ICONS];
          const isActive = selectedCategory === category.apiCategory;

          return (
            <button
              key={category.slug}
              className={cn(
                "inline-flex items-center gap-2 rounded-full border px-4 py-2.5 text-sm font-bold transition duration-150",
                isActive
                  ? "border-brand-primary/25 bg-brand-primary/10 text-app-text"
                  : "border-transparent bg-transparent text-app-text-soft hover:bg-white/5 hover:text-app-text",
              )}
              onClick={() => onSelect(isActive ? "" : category.apiCategory ?? "")}
              type="button"
            >
              {Icon ? (
                <span
                  className={cn(
                    "inline-grid h-[1.15rem] w-[1.15rem] place-items-center text-brand-primary",
                    isActive && "text-brand-blue",
                  )}
                  aria-hidden="true"
                >
                  <Icon />
                </span>
              ) : null}
              <span className={cn(isActive && "underline underline-offset-4")}>
                {category.shortLabel}
              </span>
            </button>
          );
        })()
      ))}
    </div>
  );
}
