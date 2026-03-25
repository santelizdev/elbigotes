"use client";

import { useEffect, useState } from "react";

import styles from "@/components/explorer/map-explorer.module.css";
import { ExplorerToolbar } from "@/components/filters/explorer-toolbar";
import { CategoryFilterBar } from "@/components/filters/category-filter-bar";
import { LeafletMap } from "@/components/map/leaflet-map";
import { MapLegend } from "@/components/map/map-legend";
import { PlaceDetailSheet } from "@/components/places/place-detail-sheet";
import { PlaceList } from "@/components/places/place-list";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { CATEGORY_DEFINITIONS } from "@/lib/constants/categories";
import { Place } from "@/lib/types";
import { usePlacesQuery } from "@/hooks/use-places-query";

interface MapExplorerPageProps {
  title: string;
  description: string;
  initialPlaces: Place[];
  initialCategory?: string;
  lostPetsCount?: number;
}

export function MapExplorerPage({
  title,
  description,
  initialPlaces,
  initialCategory,
  lostPetsCount = 0,
}: MapExplorerPageProps) {
  // La UX prioriza un patrón estable: filtros arriba, resultados a la izquierda y mapa dominante.
  const {
    places,
    selectedCategory,
    search,
    loading,
    error,
    showOnlyVerified,
    setSearch,
    setShowOnlyVerified,
    updateCategory,
  } = usePlacesQuery({
    initialPlaces,
    initialCategory,
  });
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(initialPlaces[0] ?? null);

  useEffect(() => {
    if (!places.length) {
      setSelectedPlace(null);
      return;
    }

    const stillVisible = places.find((place) => place.slug === selectedPlace?.slug);
    setSelectedPlace(stillVisible ?? places[0]);
  }, [places, selectedPlace?.slug]);

  const points = places
    .filter((place) => place.latitude !== null && place.longitude !== null)
    .map((place) => {
      const category = CATEGORY_DEFINITIONS.find((entry) => entry.apiCategory === place.category);
      return {
        id: place.slug,
        latitude: place.latitude as number,
        longitude: place.longitude as number,
        title: place.name,
        subtitle: place.formattedAddress,
        accent: category?.accent,
        active: selectedPlace?.slug === place.slug,
      };
    });

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroTop}>
          <div>
            <p className="eyebrow">Infraestructura pública pet en Chile</p>
            <h1 className={styles.heroTitle}>{title}</h1>
            <p className={styles.heroLead}>{description}</p>
          </div>

          <div className="stack-md">
            <Button href="/mascotas-perdidas" variant="secondary">
              Ver reportes activos
            </Button>
            <Button href="/publicar-mascota-perdida" variant="primary">
              Publicar una mascota perdida
            </Button>
          </div>
        </div>

        <div className={styles.stats}>
          <div className={styles.statCard}>
            <span className={styles.statValue}>{places.length}</span>
            <span className={styles.statLabel}>Puntos cargados en esta vista</span>
          </div>
          <div className={styles.statCard}>
            <span className={styles.statValue}>{places.filter((place) => place.isVerified).length}</span>
            <span className={styles.statLabel}>Fichas verificadas y listas para usar</span>
          </div>
          <div className={styles.statCard}>
            <span className={styles.statValue}>{lostPetsCount}</span>
            <span className={styles.statLabel}>Reportes activos de mascotas perdidas</span>
          </div>
        </div>
      </section>

      <CategoryFilterBar selectedCategory={selectedCategory} onSelect={updateCategory} />

      <ExplorerToolbar
        search={search}
        showOnlyVerified={showOnlyVerified}
        onSearchChange={setSearch}
        onVerifiedChange={setShowOnlyVerified}
      />

      <div className={styles.workspace}>
        <aside className={styles.sidebar}>
          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <p className="eyebrow">Resultados del mapa</p>
                <h2 className={styles.panelTitle}>Listado operativo</h2>
              </div>
              <span className={styles.panelCaption}>{places.length} resultados</span>
            </div>

            {error ? (
              <ErrorState message={error} />
            ) : (
              <PlaceList
                places={places}
                loading={loading}
                selectedPlaceSlug={selectedPlace?.slug}
                onSelectPlace={setSelectedPlace}
              />
            )}
          </section>

          {selectedPlace ? <PlaceDetailSheet place={selectedPlace} /> : null}
        </aside>

        <section className={styles.mapPanel}>
          <div className={styles.mapOverlay}>
            <div className={styles.mapChip}>
              <strong>Mapa activo</strong>
              <span className={styles.mapHint}>Explora puntos verificados por categoría</span>
            </div>
            <MapLegend />
          </div>
          {points.length ? (
            <LeafletMap
              points={points}
              focusedPointId={selectedPlace?.slug ?? null}
              onSelect={(id) => {
                const place = places.find((item) => item.slug === id);
                if (place) {
                  setSelectedPlace(place);
                }
              }}
            />
          ) : (
            <div className="feedback-panel">
              No hay puntos geolocalizados para mostrar en este mapa con los filtros actuales.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
