"use client";

import { FormEvent, useState } from "react";

import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { DashboardGrid } from "@/components/ui/dashboard-grid";
import { FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
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
    <PageShell>
      <PageHero
        eyebrow="Reclamar ficha"
        title={`Administrar ${place.name}`}
        description="Si este negocio u organización te pertenece, envía esta solicitud y revisaremos la documentación antes de asignarte la propiedad."
      />

      <DashboardGrid
        main={
          <SurfaceCard className="grid gap-4">
            <p className="eyebrow">Solicitud pública</p>
            <h2 className="m-0 font-display-ui text-3xl leading-tight">Datos de validación</h2>
            <form className="grid gap-4" onSubmit={handleSubmit}>
              <FormGrid>
                <FormField label="Nombre" htmlFor="claimer_name">
                  <input id="claimer_name" name="claimer_name" required className="form-control" />
                </FormField>
                <FormField label="Organización" htmlFor="organization_name">
                  <input id="organization_name" name="organization_name" className="form-control" />
                </FormField>
                <FormField label="Email" htmlFor="email">
                  <input id="email" name="email" type="email" required className="form-control" />
                </FormField>
                <FormField label="Teléfono" htmlFor="phone">
                  <input id="phone" name="phone" className="form-control" />
                </FormField>
                <FormField label="Relación con la ficha" htmlFor="relationship_to_place" fullWidth>
                  <input
                    id="relationship_to_place"
                    name="relationship_to_place"
                    placeholder="Ej: propietaria, administrador, encargado de marketing"
                    required
                    className="form-control"
                  />
                </FormField>
                <FormField label="URL de evidencia" htmlFor="evidence_url" fullWidth>
                  <input
                    id="evidence_url"
                    name="evidence_url"
                    type="url"
                    placeholder="Sitio oficial, perfil de Instagram, documento o ficha comercial"
                    className="form-control"
                  />
                </FormField>
                <FormField label="Mensaje" htmlFor="message" fullWidth>
                  <textarea
                    id="message"
                    name="message"
                    placeholder="Cuéntanos por qué esta ficha debería quedar bajo tu administración."
                    className="form-control min-h-28 resize-y"
                  />
                </FormField>
              </FormGrid>

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
          </SurfaceCard>
        }
        aside={
          <>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Ficha a reclamar</h3>
              <p className="m-0 leading-7 text-app-text-soft">{place.formattedAddress}</p>
              <InfoBox>
                {canClaim
                  ? "Esta ficha todavía no está verificada y puede recibir reclamos de propiedad."
                  : `Esta ficha figura como ${getPlaceVerificationLabel(place).toLowerCase()} y no está disponible para nuevos reclamos.`}
              </InfoBox>
            </SurfaceCard>

            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Qué revisamos</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Coincidencia con sitio oficial, redes sociales, documento de respaldo y consistencia
                del contacto entregado.
              </p>
            </SurfaceCard>
          </>
        }
      />
    </PageShell>
  );
}
