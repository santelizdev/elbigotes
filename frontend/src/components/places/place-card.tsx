import Link from "next/link";

import styles from "@/components/places/place-card.module.css";
import { StatusPill } from "@/components/ui/status-pill";
import { Tag } from "@/components/ui/tag";
import { Place } from "@/lib/types";
import { formatDistance, titleCase } from "@/lib/utils/formatters";

interface PlaceCardProps {
  place: Place;
  active?: boolean;
  onSelect?: () => void;
}

export function PlaceCard({ place, active = false, onSelect }: PlaceCardProps) {
  return (
    <article
      className={`${styles.card} ${active ? styles.active : ""}`}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect?.();
        }
      }}
      role="button"
      tabIndex={0}
    >
      <div className={styles.header}>
        <div>
          <p className="eyebrow">{titleCase(place.category)}</p>
          <h3 className={styles.title}>{place.name}</h3>
        </div>
        {place.isEmergencyService ? (
          <StatusPill label="24/7" tone="critical" />
        ) : place.isVerified ? (
          <StatusPill label="Verificado" tone="success" />
        ) : (
          <StatusPill label="Pendiente" />
        )}
      </div>

      <div className={styles.meta}>
        <span>{place.formattedAddress}</span>
        <span>{formatDistance(place.distanceKm)}</span>
      </div>

      <p className={styles.summary}>{place.summary}</p>

      <div className="inline-tags">
        {place.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
        {place.subcategory ? <Tag>{titleCase(place.subcategory)}</Tag> : null}
        {place.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
      </div>

      {place.contactPoints.length ? (
        <div className={styles.contacts}>
          {place.contactPoints.slice(0, 2).map((contact) => (
            <span key={`${contact.kind}-${contact.value}`} className={styles.contact}>
              {contact.label}: {contact.value}
            </span>
          ))}
        </div>
      ) : null}

      <div className={styles.footer}>
        <button
          className="text-button"
          onClick={(event) => {
            event.stopPropagation();
            onSelect?.();
          }}
          type="button"
        >
          Ver ficha rápida
        </button>
        <Link
          href={`/lugares/${place.slug}`}
          className={styles.link}
          onClick={(event) => event.stopPropagation()}
        >
          Abrir detalle
        </Link>
      </div>
    </article>
  );
}
