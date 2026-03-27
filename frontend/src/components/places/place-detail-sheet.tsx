import styles from "@/components/places/place-detail-sheet.module.css";
import { Button } from "@/components/ui/button";
import { StatusPill } from "@/components/ui/status-pill";
import { Place } from "@/lib/types";
import { titleCase } from "@/lib/utils/formatters";

export function PlaceDetailSheet({ place }: { place: Place }) {
  const primaryContact = place.contactPoints.find((contact) => contact.isPrimary) ?? place.contactPoints[0];

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
    <section className={styles.sheet}>
      <div className={styles.header}>
        <div>
          <p className="eyebrow">{titleCase(place.category)}</p>
          <h2 className={styles.title}>{place.name}</h2>
        </div>
        {place.isEmergencyService ? (
          <StatusPill label="Emergencia" tone="critical" />
        ) : place.isVerified ? (
          <StatusPill label="Verificado" tone="success" />
        ) : (
          <StatusPill label="Pendiente" />
        )}
      </div>

      <p className={styles.description}>
        {place.description || place.summary || "Ficha en construcción con datos básicos verificados."}
      </p>

      <div className={styles.grid}>
        <div className={styles.metaCard}>
          <span className={styles.metaLabel}>Ubicación</span>
          <span className={styles.metaValue}>{place.formattedAddress}</span>
        </div>
        <div className={styles.metaCard}>
          <span className={styles.metaLabel}>Estado operativo</span>
          <span className={styles.metaValue}>
            {place.isOpen247 ? "Abierto 24/7" : "Horario informado en ficha"}
          </span>
        </div>
        <div className={styles.metaCard}>
          <span className={styles.metaLabel}>Contacto</span>
          <span className={styles.metaValue}>{primaryContact?.value ?? "Sin contacto publicado"}</span>
        </div>
        <div className={styles.metaCard}>
          <span className={styles.metaLabel}>Cobertura</span>
          <span className={styles.metaValue}>
            {place.commune}, {place.region}
          </span>
        </div>
      </div>

      <div className={styles.actions}>
        {primaryContact ? (
          <Button href={getContactHref(primaryContact.kind, primaryContact.value)} variant="primary">
            Contactar ahora
          </Button>
        ) : null}
        {!place.isVerified ? (
          <Button href={`/lugares/${place.slug}/reclamar`} variant="secondary">
            Reclamar propiedad
          </Button>
        ) : null}
        <Button href={`/lugares/${place.slug}`} variant="secondary">
          Abrir ficha completa
        </Button>
      </div>
    </section>
  );
}
