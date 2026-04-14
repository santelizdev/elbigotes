"use client";

import { FormEvent, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { createClaimRequest } from "@/lib/services/claims-service";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { Place } from "@/lib/types";
import { getPlaceVerificationLabel } from "@/lib/utils/place-verification";

export function ClaimRequestForm({ place }: { place: Place }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const canClaim = place.canClaim ?? !place.isVerified;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canClaim) {
      return;
    }
    const form = event.currentTarget;
    const formData = new FormData(form);

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await createClaimRequest(place.slug, {
        claimer_name: String(formData.get("claimer_name") ?? ""),
        organization_name: String(formData.get("organization_name") ?? ""),
        email: String(formData.get("email") ?? ""),
        phone: String(formData.get("phone") ?? ""),
        relationship_to_place: String(formData.get("relationship_to_place") ?? ""),
        message: String(formData.get("message") ?? ""),
        evidence_url: String(formData.get("evidence_url") ?? ""),
      });
      form.reset();
      setSuccessMessage(
        "Recibimos tu solicitud. La revisaremos antes de transferir la administración de la ficha.",
      );
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          "No pudimos registrar el reclamo en este momento. Intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Reclamar ficha</p>
        <h1 className="page-title">Administrar {place.name}</h1>
        <p className="page-lead">
          Si este negocio u organización te pertenece, envía esta solicitud y revisaremos la
          documentación antes de asignarte la propiedad.
        </p>
      </section>

      <div className={styles.grid}>
        <section className={styles.formCard}>
          <p className="eyebrow">Solicitud pública</p>
          <h2>Datos de validación</h2>
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.formGrid}>
              <div className={styles.field}>
                <label htmlFor="claimer_name">Nombre</label>
                <input id="claimer_name" name="claimer_name" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="organization_name">Organización</label>
                <input id="organization_name" name="organization_name" />
              </div>
              <div className={styles.field}>
                <label htmlFor="email">Email</label>
                <input id="email" name="email" type="email" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="phone">Teléfono</label>
                <input id="phone" name="phone" />
              </div>
              <div className={styles.fieldFull}>
                <label htmlFor="relationship_to_place">Relación con la ficha</label>
                <input
                  id="relationship_to_place"
                  name="relationship_to_place"
                  placeholder="Ej: propietaria, administrador, encargado de marketing"
                  required
                />
              </div>
              <div className={styles.fieldFull}>
                <label htmlFor="evidence_url">URL de evidencia</label>
                <input
                  id="evidence_url"
                  name="evidence_url"
                  type="url"
                  placeholder="Sitio oficial, perfil de Instagram, documento o ficha comercial"
                />
              </div>
              <div className={styles.fieldFull}>
                <label htmlFor="message">Mensaje</label>
                <textarea
                  id="message"
                  name="message"
                  placeholder="Cuéntanos por qué esta ficha debería quedar bajo tu administración."
                />
              </div>
            </div>

            <Button type="submit" disabled={loading || !canClaim}>
              {loading
                ? "Enviando solicitud..."
                : !canClaim
                  ? "Reclamo no disponible"
                  : "Enviar reclamo"}
            </Button>

            {loading ? <LoadingPanel message="Registrando reclamo..." /> : null}
            {error ? <ErrorState message={error} /> : null}
            {successMessage ? <div className="success-banner">{successMessage}</div> : null}
          </form>
        </section>

        <aside className={styles.aside}>
          <section className={styles.asideCard}>
            <h3>Ficha a reclamar</h3>
            <p>{place.formattedAddress}</p>
            <div className={styles.statusBox}>
              {canClaim
                ? "Esta ficha todavía no está verificada y puede recibir reclamos de propiedad."
                : `Esta ficha figura como ${getPlaceVerificationLabel(place).toLowerCase()} y no está disponible para nuevos reclamos.`}
            </div>
          </section>

          <section className={styles.asideCard}>
            <h3>Qué revisamos</h3>
            <p>
              Coincidencia con sitio oficial, redes sociales, documento de respaldo y consistencia
              del contacto entregado.
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
