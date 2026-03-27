import Link from "next/link";

import styles from "@/components/places/place-list.module.css";
import { EmptyState } from "@/components/shared/empty-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { StatusPill } from "@/components/ui/status-pill";
import { Tag } from "@/components/ui/tag";
import { Place } from "@/lib/types";
import { formatDistance, titleCase } from "@/lib/utils/formatters";
import { useEffect, useMemo, useState } from "react";

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
          <article key={index} className="skeleton-card">
            <div className="skeleton-card__line skeleton-card__line--eyebrow" />
            <div className="skeleton-card__line skeleton-card__line--title" />
            <div className="skeleton-card__line skeleton-card__line--body" />
            <div className="skeleton-card__line skeleton-card__line--body" />
          </article>
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
  const compactPlaces = pagePlaces.filter((place) => place.slug !== featuredPlace?.slug);
  const paginationItems = buildPagination(currentPage, totalPages);

  return (
    <div className={styles.list}>
      {featuredPlace ? (
        <article className={styles.featured}>
          <div className={styles.featuredHeader}>
            <div>
              <p className="eyebrow">{titleCase(featuredPlace.category)}</p>
              <h3 className={styles.featuredTitle}>{featuredPlace.name}</h3>
            </div>
            {featuredPlace.isEmergencyService ? (
              <StatusPill label="24/7" tone="critical" />
            ) : featuredPlace.isVerified ? (
              <StatusPill label="Verificado" tone="success" />
            ) : (
              <StatusPill label="Pendiente" />
            )}
          </div>

          <div className={styles.featuredMeta}>
            <span>{featuredPlace.formattedAddress}</span>
            <span>{formatDistance(featuredPlace.distanceKm)}</span>
          </div>

          <p className={styles.featuredSummary}>
            {featuredPlace.description || featuredPlace.summary || "Ficha en construcción con datos básicos verificados."}
          </p>

          <div className="inline-tags">
            {featuredPlace.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
            {featuredPlace.subcategory ? <Tag>{titleCase(featuredPlace.subcategory)}</Tag> : null}
            {featuredPlace.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
          </div>

          {featuredPlace.contactPoints.length ? (
            <div className={styles.featuredContacts}>
              {featuredPlace.contactPoints.slice(0, 2).map((contact) => (
                <a
                  key={`${contact.kind}-${contact.value}`}
                  href={getContactHref(contact.kind, contact.value)}
                  className={styles.featuredContact}
                >
                  {contact.label}: {contact.value}
                </a>
              ))}
            </div>
          ) : null}

          <div className={styles.featuredFooter}>
            <button className="text-button" onClick={() => onSelectPlace(featuredPlace)} type="button">
              Ver ficha rápida
            </button>
            {!featuredPlace.isVerified ? (
              <Link href={`/lugares/${featuredPlace.slug}/reclamar`} className={styles.featuredLink}>
                Reclamar propiedad
              </Link>
            ) : null}
            <Link href={`/lugares/${featuredPlace.slug}`} className={styles.featuredLink}>
              Abrir detalle
            </Link>
          </div>
        </article>
      ) : null}

      {compactPlaces.length ? (
        <div className={styles.compactList}>
          {compactPlaces.map((place) => (
            <button
              key={place.slug}
              type="button"
              onClick={() => onSelectPlace(place)}
              className={[
                styles.compactCard,
                compactPlaces[0]?.slug === place.slug ? styles.compactCardStrong : "",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              <div className={styles.compactOrder}>
                Ficha #{places.findIndex((item) => item.slug === place.slug) + 1}
              </div>
              <div className={styles.compactBody}>
                <strong className={styles.compactTitle}>{place.name}</strong>
                <span className={styles.compactAddress}>{place.formattedAddress}</span>
              </div>
            </button>
          ))}
        </div>
      ) : null}

      {totalPages > 1 ? (
        <nav className={styles.pagination} aria-label="Paginas de resultados">
          <button
            type="button"
            className={styles.paginationArrow}
            onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
            disabled={currentPage === 1}
          >
            Atras
          </button>

          <div className={styles.paginationPages}>
            {paginationItems.map((page, index) => {
              const previous = paginationItems[index - 1];
              const showEllipsis = previous !== undefined && page - previous > 1;

              return (
                <div key={page} className={styles.paginationChunk}>
                  {showEllipsis ? <span className={styles.paginationEllipsis}>...</span> : null}
                  <button
                    type="button"
                    onClick={() => setCurrentPage(page)}
                    className={[
                      styles.paginationPage,
                      page === currentPage ? styles.paginationPageActive : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
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
            className={styles.paginationArrow}
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
