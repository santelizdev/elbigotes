import { CATEGORY_DEFINITIONS } from "@/lib/constants/categories";

export function MapLegend() {
  return (
    <div className="map-legend">
      {CATEGORY_DEFINITIONS.filter((category) => category.kind === "place").map((category) => (
        <span key={category.slug} className="map-legend__item">
          <span className="map-legend__dot" style={{ background: category.accent }} />
          {category.shortLabel}
        </span>
      ))}
    </div>
  );
}

