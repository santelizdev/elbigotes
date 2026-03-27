"use client";

import { useEffect, useState } from "react";
import { FaSearch } from "react-icons/fa";

import styles from "@/components/explorer/map-explorer.module.css";
import { ExplorerToolbar } from "@/components/filters/explorer-toolbar";
import { CategoryFilterBar } from "@/components/filters/category-filter-bar";
import { LeafletMap } from "@/components/map/leaflet-map";
import { MapLegend } from "@/components/map/map-legend";
import { PlaceList } from "@/components/places/place-list";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { CATEGORY_DEFINITIONS, CategoryDefinition } from "@/lib/constants/categories";
import { Place } from "@/lib/types";
import { usePlacesQuery } from "@/hooks/use-places-query";

interface MapExplorerPageProps {
  title: string;
  description: string;
  initialPlaces: Place[];
  initialCategory?: string;
  categories?: CategoryDefinition[];
}

export function MapExplorerPage({
  title,
  description,
  initialPlaces,
  initialCategory,
  categories = CATEGORY_DEFINITIONS,
}: MapExplorerPageProps) {
  // La UX prioriza un patrón estable: filtros arriba, resultados a la izquierda y mapa dominante.
  const {
    places: queriedPlaces,
    selectedCategory,
    selectedCommune,
    radiusKm,
    hasUserLocation,
    locating,
    loading,
    error,
    locationMessage,
    showOnlyVerified,
    setSelectedCommune,
    setRadiusKm,
    setShowOnlyVerified,
    updateCategory,
    toggleUserLocation,
  } = usePlacesQuery({
    initialPlaces,
    initialCategory,
  });
  const [selectedRegion, setSelectedRegion] = useState("");
  const places = selectedRegion
    ? queriedPlaces.filter((place) => place.region === selectedRegion)
    : queriedPlaces;
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
      const category = categories.find((entry) => entry.apiCategory === place.category);
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

  const handleRegionChange = (value: string) => {
    setSelectedRegion(value);
    setSelectedCommune("");
  };

  return (
    <div className={styles.page}>
      <div className={styles.sectionIntro}>
        <h2 className={styles.sectionTitle}>Que buscas para tu Mascota?</h2>
      </div>

      <CategoryFilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        onSelect={updateCategory}
      />

      <ExplorerToolbar
        region={selectedRegion}
        commune={selectedCommune}
        radiusKm={radiusKm}
        hasUserLocation={hasUserLocation}
        locating={locating}
        locationMessage={locationMessage}
        showOnlyVerified={showOnlyVerified}
        onRegionChange={handleRegionChange}
        onCommuneChange={setSelectedCommune}
        onRadiusChange={setRadiusKm}
        onLocationToggle={toggleUserLocation}
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
        </aside>

        <section className={styles.mapPanel}>
          <div className={styles.mapOverlay}>
            <div className={styles.mapChip}>
              <strong>Mapa activo</strong>
              <span className={styles.mapHint}>Explora puntos verificados por categoría</span>
            </div>
            <MapLegend categories={categories} />
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

      <section className={styles.hero}>
        <div className={styles.heroTop}>
          <div>
            <p className="eyebrow">Infraestructura pública pet en Chile</p>
            <h1 className={styles.heroTitle}>{title}</h1>
            <p className={styles.heroLead}>{description}</p>
          </div>

          <div className={styles.heroActions}>
            <Button
              href="/mascotas-perdidas"
              variant="secondary"
              className={styles.heroPrimaryAction}
            >
              <span className={styles.actionIcon} aria-hidden="true">
                <FaSearch />
              </span>
              Ver publicaciones activas
            </Button>
            <Button
              href="/publicar-mascota-perdida"
              variant="secondary"
              className={styles.heroSecondaryAction}
            >
              Publicar una mascota perdida
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
