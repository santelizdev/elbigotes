import { PlaceGoogleRating } from "@/components/places/place-google-rating";
import { PlaceLoopActions } from "@/components/places/place-loop-actions";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { StatusPill } from "@/components/ui/status-pill";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Place } from "@/lib/types";
import { getPlaceVerificationLabel, getPlaceVerificationTone } from "@/lib/utils/place-verification";
import { titleCase } from "@/lib/utils/formatters";

export function PlaceDetailSheet({ place }: { place: Place }) {
  const primaryContact = place.contactPoints.find((contact) => contact.isPrimary) ?? place.contactPoints[0];
  const canClaim = place.canClaim ?? !place.isVerified;

  function getContactHref(kind: string, value: string) {
    if (kind === "website") {
      return value.startsWith("http") ? value : `https://${value}`;
    }
    if (kind === "email") {
      return `mailto:${value}`;
    }
    return `tel:${value}`;
  }

  return (
    <SurfaceCard className="grid gap-4 border-[color-mix(in_srgb,var(--accent-emerald)_18%,transparent)] bg-[linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_98%,transparent),color-mix(in_srgb,var(--surface-elevated)_96%,transparent))] p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <SectionHeader eyebrow={titleCase(place.category)} title={place.name} compact />
        {place.isEmergencyService ? (
          <StatusPill label="Emergencia" tone="critical" />
        ) : (
          <StatusPill
            label={getPlaceVerificationLabel(place)}
            tone={getPlaceVerificationTone(place)}
          />
        )}
      </div>

      <p className="m-0 text-sm leading-7 text-app-text-soft">
        {place.description || place.summary || "Ficha en construcción con datos básicos verificados."}
      </p>

      <PlaceGoogleRating rating={place.googleRating} reviewsCount={place.googleReviewsCount} />

      <PlaceLoopActions place={place} />

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Ubicación</span>
          <span className="text-sm leading-6 text-app-text">{place.formattedAddress}</span>
        </div>
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Estado operativo</span>
          <span className="text-sm leading-6 text-app-text">
            {place.isOpen247 ? "Abierto 24/7" : "Horario informado en ficha"}
          </span>
        </div>
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Contacto</span>
          <span className="text-sm leading-6 text-app-text">
            {primaryContact?.value ?? "Sin contacto publicado"}
          </span>
        </div>
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Cobertura</span>
          <span className="text-sm leading-6 text-app-text">
            {place.commune}, {place.region}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        {primaryContact ? (
          <Button href={getContactHref(primaryContact.kind, primaryContact.value)} variant="primary">
            Contactar ahora
          </Button>
        ) : null}
        {canClaim ? (
          <Button href={`/lugares/${place.slug}/reclamar`} variant="secondary">
            Reclamar propiedad
          </Button>
        ) : null}
        <Button href={`/lugares/${place.slug}`} variant="secondary">
          Abrir ficha completa
        </Button>
      </div>
    </SurfaceCard>
  );
}
