import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { PlaceGoogleRating } from "@/components/places/place-google-rating";
import { EmptyState } from "@/components/shared/empty-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { SkeletonCard, SkeletonLine } from "@/components/ui/skeleton-card";
import { StatusPill } from "@/components/ui/status-pill";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Tag } from "@/components/ui/tag";
import { TextButton } from "@/components/ui/text-button";
import { cn } from "@/lib/utils/cn";
import { Place } from "@/lib/types";
import { getPlaceVerificationLabel, getPlaceVerificationTone } from "@/lib/utils/place-verification";
import { formatDistance, titleCase } from "@/lib/utils/formatters";

interface PlaceListProps {
  places: Place[];
  loading: boolean;
  selectedPlaceSlug?: string;
  onSelectPlace: (place: Place) => void;
}

const PAGE_SIZE = 4;

function getContactHref(kind: string, value: string) {
  if (kind === "website") {
    return value.startsWith("http") ? value : `https://${value}`;
  }
  if (kind === "email") {
    return `mailto:${value}`;
  }
  return `tel:${value}`;
}

function buildPagination(currentPage: number, totalPages: number) {
  if (totalPages <= 1) {
    return [1];
  }

  const items = new Set<number>();
  items.add(1);
  items.add(totalPages);

  for (let page = currentPage - 1; page <= currentPage + 1; page += 1) {
    if (page > 1 && page < totalPages) {
      items.add(page);
    }
  }

  return Array.from(items).sort((left, right) => left - right);
}

export function PlaceList({
  places,
  loading,
  selectedPlaceSlug,
  onSelectPlace,
}: PlaceListProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(places.length / PAGE_SIZE));
  const selectedIndex = places.findIndex((place) => place.slug === selectedPlaceSlug);

  useEffect(() => {
    if (!places.length) {
      setCurrentPage(1);
      return;
    }

    if (selectedIndex >= 0) {
      const pageForSelected = Math.floor(selectedIndex / PAGE_SIZE) + 1;
      setCurrentPage(pageForSelected);
      return;
    }

    setCurrentPage((page) => Math.min(page, totalPages));
  }, [places.length, selectedIndex, totalPages]);

  const pagePlaces = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return places.slice(start, start + PAGE_SIZE);
  }, [currentPage, places]);

  useEffect(() => {
    if (!pagePlaces.length) {
      return;
    }

    const selectedOnPage = pagePlaces.some((place) => place.slug === selectedPlaceSlug);
    if (!selectedOnPage) {
      onSelectPlace(pagePlaces[0]);
    }
  }, [onSelectPlace, pagePlaces, selectedPlaceSlug]);

  if (loading) {
    return (
      <div className="stack-lg" aria-hidden="true">
        <LoadingPanel message="Actualizando resultados sobre el mapa..." />
        {Array.from({ length: 4 }, (_, index) => (
          <SkeletonCard key={index}>
            <SkeletonLine width="eyebrow" />
            <SkeletonLine width="title" size="title" />
            <SkeletonLine />
            <SkeletonLine />
          </SkeletonCard>
        ))}
      </div>
    );
  }

  if (!places.length) {
    return (
      <EmptyState
        title="No encontramos resultados con esos filtros"
        message="Prueba cambiando de region, comuna, radio o categoria para ampliar el mapa."
      />
    );
  }

  const featuredPlace =
    pagePlaces.find((place) => place.slug === selectedPlaceSlug) ?? pagePlaces[0] ?? null;
  const featuredPlaceCanClaim = featuredPlace ? (featuredPlace.canClaim ?? !featuredPlace.isVerified) : false;
  const compactPlaces = pagePlaces.filter((place) => place.slug !== featuredPlace?.slug);
  const paginationItems = buildPagination(currentPage, totalPages);

  return (
    <div className="grid gap-4">
      {featuredPlace ? (
        <SurfaceCard className="grid gap-4 border-[color-mix(in_srgb,var(--accent-emerald)_20%,var(--border))] bg-app-surface-raised p-5 shadow-[0_16px_28px_color-mix(in_srgb,var(--accent-emerald)_12%,transparent)]">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="eyebrow">{titleCase(featuredPlace.category)}</p>
              <h3 className="m-[0.2rem_0_0] text-[1.25rem] leading-[1.1]">{featuredPlace.name}</h3>
            </div>
            {featuredPlace.isEmergencyService ? (
              <StatusPill label="24/7" tone="critical" />
            ) : (
              <StatusPill
                label={getPlaceVerificationLabel(featuredPlace)}
                tone={getPlaceVerificationTone(featuredPlace)}
              />
            )}
          </div>

          <div className="flex flex-wrap gap-x-4 gap-y-2 text-[0.94rem] text-app-text-muted">
            <span>{featuredPlace.formattedAddress}</span>
            <span>{formatDistance(featuredPlace.distanceKm)}</span>
          </div>

          <p className="m-0 text-[0.98rem] leading-7 text-app-text-soft">
            {featuredPlace.description || featuredPlace.summary || "Ficha en construcción con datos básicos verificados."}
          </p>

          <PlaceGoogleRating
            rating={featuredPlace.googleRating}
            reviewsCount={featuredPlace.googleReviewsCount}
          />

          <div className="inline-tags">
            {featuredPlace.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
            {featuredPlace.subcategory ? <Tag>{titleCase(featuredPlace.subcategory)}</Tag> : null}
            {featuredPlace.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
          </div>

          {featuredPlace.contactPoints.length ? (
            <div className="flex flex-wrap gap-2">
              {featuredPlace.contactPoints.slice(0, 2).map((contact) => (
                <a
                  key={`${contact.kind}-${contact.value}`}
                  href={getContactHref(contact.kind, contact.value)}
                  className="inline-flex items-center rounded-full border border-app-border bg-[color-mix(in_srgb,var(--background-soft)_72%,#ffffff)] px-3 py-2 text-[0.9rem] text-app-text-soft no-underline"
                >
                  {contact.label}: {contact.value}
                </a>
              ))}
            </div>
          ) : null}

          <div className="flex flex-wrap items-center justify-between gap-3">
            <TextButton onClick={() => onSelectPlace(featuredPlace)}>
              Ver ficha rápida
            </TextButton>
            {featuredPlaceCanClaim ? (
              <Link
                href={`/lugares/${featuredPlace.slug}/reclamar`}
                className="font-bold text-brand-secondary no-underline"
              >
                Reclamar propiedad
              </Link>
            ) : null}
            <Link href={`/lugares/${featuredPlace.slug}`} className="font-bold text-brand-secondary no-underline">
              Abrir detalle
            </Link>
          </div>
        </SurfaceCard>
      ) : null}

      {compactPlaces.length ? (
        <div className="grid gap-3">
          {compactPlaces.map((place) => (
            <button
              key={place.slug}
              type="button"
              onClick={() => onSelectPlace(place)}
              className={cn(
                "grid w-full cursor-pointer gap-3 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface)_90%,transparent)] p-4 text-left text-app-text transition duration-150 hover:-translate-y-px hover:border-[color-mix(in_srgb,var(--accent-emerald)_28%,var(--border-strong))] sm:grid-cols-[auto_minmax(0,1fr)] sm:items-center",
                compactPlaces[0]?.slug === place.slug &&
                  "min-h-[4.8rem] shadow-[0_14px_28px_color-mix(in_srgb,var(--accent-emerald)_10%,transparent)]",
              )}
            >
              <div className="inline-flex min-w-[4.7rem] items-center justify-center rounded-full bg-[color-mix(in_srgb,var(--accent-emerald)_12%,transparent)] px-3 py-2 text-[0.8rem] font-extrabold text-[var(--accent-emerald)]">
                Ficha #{places.findIndex((item) => item.slug === place.slug) + 1}
              </div>
              <div className="grid min-w-0 gap-1">
                <strong className="text-[0.98rem] leading-5">{place.name}</strong>
                <span className="text-[0.88rem] leading-6 text-app-text-muted">{place.formattedAddress}</span>
                <PlaceGoogleRating
                  rating={place.googleRating}
                  reviewsCount={place.googleReviewsCount}
                  compact
                />
              </div>
            </button>
          ))}
        </div>
      ) : null}

      {totalPages > 1 ? (
        <nav className="grid items-center gap-3 pt-1 md:grid-cols-[auto_minmax(0,1fr)_auto]" aria-label="Paginas de resultados">
          <button
            type="button"
            className="min-h-[2.4rem] rounded-full border border-app-border bg-[color-mix(in_srgb,var(--surface)_92%,transparent)] px-4 py-2 text-app-text disabled:cursor-not-allowed disabled:opacity-45"
            onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
            disabled={currentPage === 1}
          >
            Atras
          </button>

          <div className="flex flex-wrap justify-center gap-2">
            {paginationItems.map((page, index) => {
              const previous = paginationItems[index - 1];
              const showEllipsis = previous !== undefined && page - previous > 1;

              return (
                <div key={page} className="inline-flex items-center gap-2">
                  {showEllipsis ? <span className="font-bold text-app-text-muted">...</span> : null}
                  <button
                    type="button"
                    onClick={() => setCurrentPage(page)}
                    className={cn(
                      "min-h-[2.4rem] min-w-[2.4rem] rounded-full border border-app-border bg-[color-mix(in_srgb,var(--surface)_92%,transparent)] px-3 py-2 text-app-text",
                      page === currentPage && "border-transparent bg-[var(--accent-emerald)] text-white",
                    )}
                    aria-current={page === currentPage ? "page" : undefined}
                  >
                    {page}
                  </button>
                </div>
              );
            })}
          </div>

          <button
            type="button"
            className="min-h-[2.4rem] rounded-full border border-app-border bg-[color-mix(in_srgb,var(--surface)_92%,transparent)] px-4 py-2 text-app-text disabled:cursor-not-allowed disabled:opacity-45"
            onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
            disabled={currentPage === totalPages}
          >
            Siguiente
          </button>
        </nav>
      ) : null}
    </div>
  );
}
