"use client";

import { FaBolt, FaCut, FaDog, FaHome, FaSearch, FaStethoscope, FaTree } from "react-icons/fa";

import { CategoryDefinition } from "@/lib/constants/categories";

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
    <div className="category-filter-bar" aria-label="Filtros por categoría">
      {categories.filter((category) => category.kind === "place").map((category) => (
        (() => {
          const Icon = CATEGORY_ICONS[category.slug as keyof typeof CATEGORY_ICONS];
          const isActive = selectedCategory === category.apiCategory;

          return (
            <button
              key={category.slug}
              className={`category-chip ${isActive ? "category-chip--active" : ""}`}
              onClick={() => onSelect(isActive ? "" : category.apiCategory ?? "")}
              type="button"
            >
              {Icon ? (
                <span className="category-chip__icon" aria-hidden="true">
                  <Icon />
                </span>
              ) : null}
              <span>{category.shortLabel}</span>
            </button>
          );
        })()
      ))}
    </div>
  );
}
