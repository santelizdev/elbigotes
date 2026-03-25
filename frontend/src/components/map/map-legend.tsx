import { CategoryDefinition } from "@/lib/constants/categories";

export function MapLegend({ categories }: { categories: CategoryDefinition[] }) {
  return (
    <div className="map-legend">
      {categories.filter((category) => category.kind === "place").map((category) => (
        <span key={category.slug} className="map-legend__item">
          <span className="map-legend__dot" style={{ background: category.accent }} />
          {category.shortLabel}
        </span>
      ))}
    </div>
  );
}
