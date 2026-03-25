import { PlaceCard } from "@/components/places/place-card";
import { EmptyState } from "@/components/shared/empty-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Place } from "@/lib/types";

interface PlaceListProps {
  places: Place[];
  loading: boolean;
  selectedPlaceSlug?: string;
  onSelectPlace: (place: Place) => void;
}

export function PlaceList({
  places,
  loading,
  selectedPlaceSlug,
  onSelectPlace,
}: PlaceListProps) {
  if (loading) {
    return (
      <div className="stack-lg" aria-hidden="true">
        <LoadingPanel message="Actualizando resultados sobre el mapa..." />
        {Array.from({ length: 3 }, (_, index) => (
          <article key={index} className="skeleton-card">
            <div className="skeleton-card__line skeleton-card__line--eyebrow" />
            <div className="skeleton-card__line skeleton-card__line--title" />
            <div className="skeleton-card__line skeleton-card__line--body" />
            <div className="skeleton-card__line skeleton-card__line--body" />
            <div className="skeleton-card__chips">
              <span className="skeleton-card__chip" />
              <span className="skeleton-card__chip" />
            </div>
          </article>
        ))}
      </div>
    );
  }

  if (!places.length) {
    return (
      <EmptyState
        title="No encontramos resultados con esos filtros"
        message="Prueba quitando la búsqueda o cambiando de categoría para ampliar el mapa."
      />
    );
  }

  return (
    <div className="stack-lg">
      {places.map((place) => (
        <PlaceCard
          key={place.slug}
          place={place}
          active={selectedPlaceSlug === place.slug}
          onSelect={() => onSelectPlace(place)}
        />
      ))}
    </div>
  );
}
