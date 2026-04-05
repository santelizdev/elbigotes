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

export function MapLegend({ categories }: { categories: CategoryDefinition[] }) {
  return (
    <div className="map-legend">
      {categories.filter((category) => category.kind === "place").map((category) => (
        <span key={category.slug} className="map-legend__item">
          {(() => {
            const Icon = CATEGORY_ICONS[category.slug as keyof typeof CATEGORY_ICONS];

            return (
              <>
                <span
                  className="map-legend__icon"
                  style={{ color: category.accent }}
                  aria-hidden="true"
                >
                  {Icon ? <Icon /> : null}
                </span>
                <span className="map-legend__label">{category.shortLabel}</span>
              </>
            );
          })()}
        </span>
      ))}
    </div>
  );
}
