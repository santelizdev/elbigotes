"use client";

import { useEffect, useState } from "react";
import { FaSearch } from "react-icons/fa";

import { ExplorerToolbar } from "@/components/filters/explorer-toolbar";
import { CategoryFilterBar } from "@/components/filters/category-filter-bar";
import { LeafletMap } from "@/components/map/leaflet-map";
import { MapLegend } from "@/components/map/map-legend";
import { PlaceList } from "@/components/places/place-list";
import { ErrorState } from "@/components/shared/error-state";
import { Button } from "@/components/ui/button";
import { FeedbackPanel } from "@/components/ui/feedback-panel";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
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
    selectedRegion,
    selectedCommune,
    availableRegions,
    availableCommunes,
    totalPlacesCount,
    selectedRegionPlacesCount,
    radiusKm,
    hasUserLocation,
    locating,
    loading,
    error,
    locationMessage,
    showOnlyVerified,
    showOnly247,
    setSelectedCommune,
    setRadiusKm,
    setShowOnlyVerified,
    setShowOnly247,
    updateCategory,
    updateRegion,
    toggleUserLocation,
  } = usePlacesQuery({
    initialPlaces,
    initialCategory,
  });
  const places = queriedPlaces;
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

  return (
    <PageShell className="gap-5 pt-5">
      <SectionHeader title="Servicios operativos para tu mascota" />

      <CategoryFilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        onSelect={updateCategory}
      />

      <ExplorerToolbar
        region={selectedRegion}
        commune={selectedCommune}
        availableRegions={availableRegions}
        availableCommunes={availableCommunes}
        totalPlacesCount={totalPlacesCount}
        selectedRegionPlacesCount={selectedRegionPlacesCount}
        radiusKm={radiusKm}
        hasUserLocation={hasUserLocation}
        locating={locating}
        locationMessage={locationMessage}
        showOnlyVerified={showOnlyVerified}
        showOnly247={showOnly247}
        onRegionChange={updateRegion}
        onCommuneChange={setSelectedCommune}
        onRadiusChange={setRadiusKm}
        onLocationToggle={toggleUserLocation}
        onVerifiedChange={setShowOnlyVerified}
        onOpen247Change={setShowOnly247}
      />

      <div className="grid min-h-[40rem] gap-4 xl:grid-cols-[minmax(420px,0.96fr)_minmax(0,1.1fr)]">
        <aside className="grid content-start gap-4">
          <SurfaceCard className="grid gap-4 p-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="eyebrow">Servicios en el mapa</p>
                <h2 className="m-0 pt-1 font-display-ui text-[1.08rem]">Listado operativo</h2>
              </div>
              <span className="text-[0.92rem] text-app-text-muted">{places.length} resultados</span>
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
          </SurfaceCard>
        </aside>

        <section className="relative isolate overflow-hidden rounded-[1.6rem] border border-white/8 bg-app-bg min-h-[40rem] max-xl:order-[-1] max-xl:min-h-[32rem] max-md:min-h-[26rem]">
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
            <FeedbackPanel message="No hay puntos geolocalizados para mostrar en este mapa con los filtros actuales." className="m-5" />
          )}
        </section>
      </div>

      <SurfaceCard
        className="flex flex-wrap items-center justify-between gap-4 rounded-[1.35rem] px-4 py-4 max-xl:order-[-1]"
        aria-label="Contexto del mapa"
      >
        <div className="inline-flex items-center gap-2 rounded-full border border-app-border bg-[color-mix(in_srgb,var(--background-soft)_78%,var(--surface)_22%)] px-4 py-3 text-app-text">
          <strong className="text-[0.95rem]">Mapa activo</strong>
          <span className="text-[0.84rem] text-app-text-muted">
            Explora puntos verificados por categoría
          </span>
        </div>
        <MapLegend categories={categories} />
      </SurfaceCard>

      <PageHero
        eyebrow="Servicios pet activos en Chile"
        title={title}
        description={description}
        actions={
          <div className="flex flex-wrap items-center gap-3">
            <Button
              href="/emergencias-veterinarias-24-7"
              variant="secondary"
              className="border-white bg-white text-[#102127] shadow-[0_18px_34px_rgba(255,255,255,0.18)] hover:bg-white dark:border-transparent dark:bg-[linear-gradient(135deg,var(--accent-emerald),#106b78)] dark:text-white dark:shadow-[0_18px_34px_color-mix(in_srgb,var(--accent-emerald)_24%,transparent)]"
            >
              <span className="mr-2 inline-flex items-center justify-center align-middle" aria-hidden="true">
                <FaSearch />
              </span>
              Ver servicios 24 horas
            </Button>
            <Button
              href="/?category=tiendas-de-alimentos"
              variant="secondary"
              className="border-app-border-strong bg-transparent text-app-text hover:bg-[color-mix(in_srgb,var(--surface)_90%,transparent)]"
            >
              Explorar tiendas de alimentos
            </Button>
          </div>
        }
        className="gap-5 rounded-[1.6rem] border-[color-mix(in_srgb,var(--accent-emerald)_18%,transparent)] bg-[radial-gradient(circle_at_top_left,color-mix(in_srgb,var(--accent-emerald)_16%,transparent),transparent_28%),radial-gradient(circle_at_top_right,color-mix(in_srgb,var(--accent-emerald)_9%,transparent),transparent_26%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))]"
      />
    </PageShell>
  );
}
