"use client";

import { CategoryDefinition } from "@/lib/constants/categories";

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
      <button
        className={`category-chip ${selectedCategory === "" ? "category-chip--active" : ""}`}
        onClick={() => onSelect("")}
        type="button"
      >
        Todo Chile
      </button>
      {categories.filter((category) => category.kind === "place").map((category) => (
        <button
          key={category.slug}
          className={`category-chip ${
            selectedCategory === category.apiCategory ? "category-chip--active" : ""
          }`}
          onClick={() => onSelect(category.apiCategory ?? "")}
          type="button"
        >
          {category.shortLabel}
        </button>
      ))}
    </div>
  );
}
