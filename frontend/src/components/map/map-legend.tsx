import { FaBolt, FaCut, FaDog, FaHome, FaShoppingBasket, FaStethoscope, FaTree } from "react-icons/fa";

import { CategoryDefinition } from "@/lib/constants/categories";

const CATEGORY_ICONS = {
  veterinarias: FaStethoscope,
  "refugios-albergues": FaHome,
  "parques-pet-friendly": FaTree,
  "emergencias-veterinarias": FaBolt,
  "tiendas-de-alimentos": FaShoppingBasket,
  guarderias: FaDog,
  peluquerias: FaCut,
} as const;

export function MapLegend({ categories }: { categories: CategoryDefinition[] }) {
  return (
    <div className="flex flex-wrap items-center justify-end gap-3">
      {categories.filter((category) => category.kind === "place").map((category) => (
        <span
          key={category.slug}
          className="inline-flex items-center gap-2 rounded-full border border-app-border bg-[color-mix(in_srgb,var(--background-soft)_70%,var(--surface)_30%)] px-3 py-2 text-[0.84rem] font-bold text-app-text"
        >
          {(() => {
            const Icon = CATEGORY_ICONS[category.slug as keyof typeof CATEGORY_ICONS];

            return (
              <>
                <span
                  className="inline-grid h-4 w-4 shrink-0 place-items-center"
                  style={{ color: category.accent }}
                  aria-hidden="true"
                >
                  {Icon ? <Icon /> : null}
                </span>
                <span className="text-app-text-soft">{category.shortLabel}</span>
              </>
            );
          })()}
        </span>
      ))}
    </div>
  );
}
