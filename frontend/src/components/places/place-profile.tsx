import { PlaceGoogleRating } from "@/components/places/place-google-rating";
import { PlaceLoopActions } from "@/components/places/place-loop-actions";
import { LeafletMap } from "@/components/map/leaflet-map";
import { Button } from "@/components/ui/button";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { StatusPill } from "@/components/ui/status-pill";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Tag } from "@/components/ui/tag";
import { Place } from "@/lib/types";
import { getPlaceVerificationTone } from "@/lib/utils/place-verification";
import { titleCase } from "@/lib/utils/formatters";

export function PlaceProfile({ place }: { place: Place }) {
  const primaryContact =
    place.contactPoints.find((contact) => contact.isPrimary) ?? place.contactPoints[0];
  const hasMapPoint = place.latitude !== null && place.longitude !== null;
  const canClaim = place.canClaim ?? !place.isVerified;
  const verificationStatus =
    place.verificationStatus ??
    (place.isPremiumVerified ? "verified_premium" : place.isVerified ? "verified" : "unverified");
  const verificationHeaderLabel =
    verificationStatus === "verified_premium"
      ? "Ficha verificada premium"
      : verificationStatus === "verified"
        ? "Ficha verificada"
        : verificationStatus === "claim_requested"
          ? "Ficha reclamada"
          : "Ficha en revisión";

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
    <PageShell className="gap-5 pb-8 pt-5">
      <PageHero
        eyebrow={titleCase(place.category)}
        title={place.name}
        description={
          place.description || place.summary || "Ficha pública preparada para moderación y detalle operativo."
        }
        className="gap-5 border-[color-mix(in_srgb,var(--accent-blue)_18%,var(--border-strong))] bg-[radial-gradient(circle_at_top_right,color-mix(in_srgb,var(--accent-blue)_16%,transparent),transparent_28%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))] p-6"
        actions={
          <div className="flex w-full flex-col gap-4">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="inline-tags">
                {place.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
                {place.subcategory ? <Tag>{titleCase(place.subcategory)}</Tag> : null}
                {place.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
              </div>
              {place.isEmergencyService ? (
                <StatusPill label="Emergencia 24/7" tone="critical" />
              ) : (
                <StatusPill label={verificationHeaderLabel} tone={getPlaceVerificationTone(place)} />
              )}
            </div>
            <PlaceGoogleRating rating={place.googleRating} reviewsCount={place.googleReviewsCount} />
            <PlaceLoopActions place={place} />
          </div>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.1fr)_minmax(300px,0.9fr)]">
        <SurfaceCard className="grid gap-5 p-5">
          <SectionHeader eyebrow="Ficha pública" title="Información clave" />

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Ubicación</span>
              <span className="text-sm leading-6 text-app-text">{place.formattedAddress}</span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Cobertura</span>
              <span className="text-sm leading-6 text-app-text">
                {place.commune}, {place.region}
              </span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Estado</span>
              <span className="text-sm leading-6 text-app-text">
                {place.isEmergencyService ? "Servicio crítico" : "Servicio regular"}
              </span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Horario</span>
              <span className="text-sm leading-6 text-app-text">
                {place.isOpen247 ? "Continuo 24/7" : "Revisar ficha o contacto"}
              </span>
            </div>
          </div>

          <div className="grid gap-3">
            <SectionHeader title="Canales de contacto" compact />
            {place.contactPoints.length ? (
              place.contactPoints.map((contact) => (
                <div
                  key={`${contact.kind}-${contact.value}`}
                  className="flex flex-col gap-3 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="grid gap-1">
                    <strong className="text-sm font-semibold text-app-text">{contact.label}</strong>
                    <div className="text-sm leading-6 text-app-text-soft">{contact.value}</div>
                  </div>
                  <Button href={getContactHref(contact.kind, contact.value)} variant="secondary">
                    Acción principal
                  </Button>
                </div>
              ))
            ) : (
              <div className="feedback-panel">
                No hay contactos estructurados todavía para esta ficha.
              </div>
            )}
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
            <Button href="/" variant="ghost">
              Volver al mapa principal
            </Button>
          </div>
        </SurfaceCard>

        <SurfaceCard className="grid gap-5 p-5">
          <SectionHeader eyebrow="Mapa local" title="Ubicación exacta" />
          <div className="min-h-[360px] overflow-hidden rounded-[1.4rem] border border-app-border-strong">
            {hasMapPoint ? (
              <LeafletMap
                points={[
                  {
                    id: place.slug,
                    latitude: place.latitude as number,
                    longitude: place.longitude as number,
                    title: place.name,
                    subtitle: place.formattedAddress,
                    accent: "var(--accent-blue)",
                  },
                ]}
                focusedPointId={place.slug}
              />
            ) : (
              <div className="feedback-panel">
                Esta ficha todavía no tiene coordenadas listas para mostrar en el mapa.
              </div>
            )}
          </div>
        </SurfaceCard>
      </div>
    </PageShell>
  );
}
