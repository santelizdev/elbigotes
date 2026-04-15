import { PlaceGoogleRating } from "@/components/places/place-google-rating";
import { PlaceLoopActions } from "@/components/places/place-loop-actions";
import styles from "@/components/places/place-profile.module.css";
import { LeafletMap } from "@/components/map/leaflet-map";
import { Button } from "@/components/ui/button";
import { StatusPill } from "@/components/ui/status-pill";
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroHeader}>
          <div>
            <p className="eyebrow">{titleCase(place.category)}</p>
            <h1 className={styles.heroTitle}>{place.name}</h1>
            <p className={styles.heroLead}>
              {place.description || place.summary || "Ficha pública preparada para moderación y detalle operativo."}
            </p>
          </div>
          {place.isEmergencyService ? (
            <StatusPill label="Emergencia 24/7" tone="critical" />
          ) : (
            <StatusPill
              label={verificationHeaderLabel}
              tone={getPlaceVerificationTone(place)}
            />
          )}
        </div>

        <div className="inline-tags">
          {place.isOpen247 ? <Tag tone="warning">Abierto 24/7</Tag> : null}
          {place.subcategory ? <Tag>{titleCase(place.subcategory)}</Tag> : null}
          {place.isFeatured ? <Tag tone="accent">Destacado</Tag> : null}
        </div>

        <PlaceGoogleRating rating={place.googleRating} reviewsCount={place.googleReviewsCount} />

        <PlaceLoopActions place={place} />
      </section>

      <div className={styles.grid}>
        <section className={styles.panel}>
          <div>
            <p className="eyebrow">Ficha pública</p>
            <h2>Información clave</h2>
          </div>

          <div className={styles.metaGrid}>
            <div className={styles.metaCard}>
              <span className={styles.metaLabel}>Ubicación</span>
              <span className={styles.metaValue}>{place.formattedAddress}</span>
            </div>
            <div className={styles.metaCard}>
              <span className={styles.metaLabel}>Cobertura</span>
              <span className={styles.metaValue}>
                {place.commune}, {place.region}
              </span>
            </div>
            <div className={styles.metaCard}>
              <span className={styles.metaLabel}>Estado</span>
              <span className={styles.metaValue}>
                {place.isEmergencyService ? "Servicio crítico" : "Servicio regular"}
              </span>
            </div>
            <div className={styles.metaCard}>
              <span className={styles.metaLabel}>Horario</span>
              <span className={styles.metaValue}>
                {place.isOpen247 ? "Continuo 24/7" : "Revisar ficha o contacto"}
              </span>
            </div>
          </div>

          <div className={styles.contacts}>
            <h3>Canales de contacto</h3>
            {place.contactPoints.length ? (
              place.contactPoints.map((contact) => (
                <div key={`${contact.kind}-${contact.value}`} className={styles.contactRow}>
                  <div>
                    <strong>{contact.label}</strong>
                    <div>{contact.value}</div>
                  </div>
                  <Button
                    href={getContactHref(contact.kind, contact.value)}
                    variant="secondary"
                  >
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

          <div className="stack-md">
            {primaryContact ? (
              <Button
                href={getContactHref(primaryContact.kind, primaryContact.value)}
                variant="primary"
              >
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
        </section>

        <section className={styles.panel}>
          <div>
            <p className="eyebrow">Mapa local</p>
            <h2>Ubicación exacta</h2>
          </div>
          <div className={styles.mapFrame}>
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
        </section>
      </div>
    </div>
  );
}
