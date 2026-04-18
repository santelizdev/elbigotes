import Link from "next/link";

import { PlaceGoogleRating } from "@/components/places/place-google-rating";
import { StatusPill } from "@/components/ui/status-pill";
import { Tag } from "@/components/ui/tag";
import { TextButton } from "@/components/ui/text-button";
import { Place } from "@/lib/types";
import { cn } from "@/lib/utils/cn";
import { getPlaceVerificationLabel, getPlaceVerificationTone } from "@/lib/utils/place-verification";
import { formatDistance, titleCase } from "@/lib/utils/formatters";

interface PlaceCardProps {
  place: Place;
  active?: boolean;
  onSelect?: () => void;
}

export function PlaceCard({ place, active = false, onSelect }: PlaceCardProps) {
  return (
    <article
      className={cn(
        "grid cursor-pointer gap-4 rounded-[1.2rem] border border-app-border bg-app-surface-raised p-4 transition duration-150",
        "hover:-translate-y-0.5 hover:border-brand-primary/35 hover:shadow-[0_18px_30px_rgba(7,17,24,0.18)]",
        "focus-visible:-translate-y-0.5 focus-visible:border-brand-primary/35 focus-visible:shadow-[0_18px_30px_rgba(7,17,24,0.18)]",
        active && "-translate-y-0.5 border-brand-primary/35 shadow-[0_18px_30px_rgba(7,17,24,0.18)]",
      )}
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
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="eyebrow">{titleCase(place.category)}</p>
          <h3 className="m-0 text-base font-bold">{place.name}</h3>
        </div>
        {place.isEmergencyService ? (
          <StatusPill label="24/7" tone="critical" />
        ) : (
          <StatusPill
            label={getPlaceVerificationLabel(place)}
            tone={getPlaceVerificationTone(place)}
          />
        )}
      </div>

      <div className="flex flex-wrap gap-2 text-[0.92rem] text-app-text-muted">
        <span>{place.formattedAddress}</span>
        <span>{formatDistance(place.distanceKm)}</span>
      </div>

      <p className="m-0 text-[0.95rem] leading-6 text-app-text-soft">{place.summary}</p>

      <PlaceGoogleRating
        rating={place.googleRating}
        reviewsCount={place.googleReviewsCount}
        compact
      />

      <div className="inline-tags">
        {place.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
        {place.subcategory ? <Tag>{titleCase(place.subcategory)}</Tag> : null}
        {place.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
      </div>

      {place.contactPoints.length ? (
        <div className="flex flex-wrap gap-2">
          {place.contactPoints.slice(0, 2).map((contact) => (
            <span
              key={`${contact.kind}-${contact.value}`}
              className="rounded-full bg-white/5 px-3 py-2 text-[0.88rem] text-app-text-soft"
            >
              {contact.label}: {contact.value}
            </span>
          ))}
        </div>
      ) : null}

      <div className="flex flex-col items-start justify-between gap-3 md:flex-row md:items-center">
        <TextButton
          onClick={(event) => {
            event.stopPropagation();
            onSelect?.();
          }}
        >
          Ver ficha rápida
        </TextButton>
        <Link
          href={`/lugares/${place.slug}`}
          className="font-semibold text-brand-bright no-underline"
          onClick={(event) => event.stopPropagation()}
        >
          Abrir detalle
        </Link>
      </div>
    </article>
  );
}
