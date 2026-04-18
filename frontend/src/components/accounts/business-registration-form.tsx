"use client";

import { FormEvent, useState } from "react";

import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { DashboardGrid } from "@/components/ui/dashboard-grid";
import { FormCheckbox, FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import {
  BusinessRegistrationPayload,
  RegistrationCatalogItem,
  registerBusinessAccount,
} from "@/lib/services/accounts-service";
import { CHILE_REGIONS, DEFAULT_REGION, getCommunesForRegion } from "@/lib/constants/chile-locations";
import { getApiErrorMessage } from "@/lib/services/api-client";

export function BusinessRegistrationForm({
  businessKinds,
}: {
  businessKinds: RegistrationCatalogItem[];
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedKind, setSelectedKind] = useState<string>(businessKinds[0]?.value ?? "veterinary");
  const [selectedRegion, setSelectedRegion] = useState<string>(DEFAULT_REGION);
  const [selectedLatitude, setSelectedLatitude] = useState<number | undefined>(undefined);
  const [selectedLongitude, setSelectedLongitude] = useState<number | undefined>(undefined);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData(form);
    if (selectedLatitude === undefined || selectedLongitude === undefined) {
      setLoading(false);
      setError("Debes confirmar la ubicación haciendo clic en el mapa.");
      return;
    }

    const commune = String(formData.get("commune") ?? "");
    const region = String(formData.get("region") ?? "") || DEFAULT_REGION;
    const payload: BusinessRegistrationPayload = {
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? ""),
      first_name: String(formData.get("first_name") ?? ""),
      last_name: String(formData.get("last_name") ?? ""),
      business_name: String(formData.get("business_name") ?? ""),
      business_kind: String(formData.get("business_kind") ?? ""),
      phone: String(formData.get("phone") ?? ""),
      commune,
      region,
      website: String(formData.get("website") ?? ""),
      place_label: "Punto confirmado en mapa",
      latitude: selectedLatitude,
      longitude: selectedLongitude,
      marketing_opt_in: formData.get("marketing_opt_in") === "on",
      notes: String(formData.get("notes") ?? ""),
    };

    try {
      await registerBusinessAccount(payload);
      form.reset();
      setSelectedKind(businessKinds[0]?.value ?? "veterinary");
      setSelectedRegion(DEFAULT_REGION);
      setSelectedLatitude(undefined);
      setSelectedLongitude(undefined);
      setSuccessMessage(
        "Cuenta creada. La ficha quedó en revisión manual y la membresía se administrará desde asignaciones cuando corresponda.",
      );
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          "No pudimos crear la cuenta comercial. Revisa los datos e intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageShell>
      <PageHero
        eyebrow="Registro comercial"
        title="Alta de negocio u organización"
        description="Este flujo separa los negocios con membresía potencial de los actores comunitarios que quedarán siempre gratuitos, para que el modelo comercial nazca ordenado desde el inicio."
        actions={
          <Button href="/registro" variant="ghost">
            Volver a tipos de cuenta
          </Button>
        }
      />

      <DashboardGrid
        main={
          <SurfaceCard className="grid gap-4">
            <p className="eyebrow">Datos de alta</p>
            <h2 className="m-0 font-display-ui text-3xl leading-tight">Crear cuenta comercial</h2>
            <form className="grid gap-4" onSubmit={handleSubmit}>
              <FormGrid>
                <FormField label="Nombre responsable" htmlFor="first_name">
                  <input id="first_name" name="first_name" required className="form-control" />
                </FormField>
                <FormField label="Apellido" htmlFor="last_name">
                  <input id="last_name" name="last_name" className="form-control" />
                </FormField>
                <FormField label="Email" htmlFor="email">
                  <input id="email" name="email" type="email" required className="form-control" />
                </FormField>
                <FormField label="Password" htmlFor="password">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    minLength={8}
                    required
                    className="form-control"
                  />
                </FormField>
                <FormField label="Nombre comercial" htmlFor="business_name">
                  <input id="business_name" name="business_name" required className="form-control" />
                </FormField>
                <FormField label="Tipo de cuenta" htmlFor="business_kind">
                  <select
                    id="business_kind"
                    name="business_kind"
                    value={selectedKind}
                    onChange={(event) => setSelectedKind(event.target.value)}
                    className="form-control"
                  >
                    {businessKinds.map((kind) => (
                      <option key={kind.value} value={kind.value}>
                        {kind.label}
                      </option>
                    ))}
                  </select>
                </FormField>
                <FormField label="Teléfono" htmlFor="phone">
                  <input id="phone" name="phone" required className="form-control" />
                </FormField>
                <FormField label="Comuna" htmlFor="commune">
                  <select id="commune" name="commune" required className="form-control">
                    <option value="">Selecciona una comuna</option>
                    {getCommunesForRegion(selectedRegion).map((commune) => (
                      <option key={commune} value={commune}>
                        {commune}
                      </option>
                    ))}
                  </select>
                </FormField>
                <FormField label="Región" htmlFor="region">
                  <select
                    id="region"
                    name="region"
                    value={selectedRegion}
                    onChange={(event) => setSelectedRegion(event.target.value)}
                    className="form-control"
                  >
                    {CHILE_REGIONS.map((item) => (
                      <option key={item.region} value={item.region}>
                        {item.region}
                      </option>
                    ))}
                  </select>
                </FormField>
                <FormField
                  label="Sitio web"
                  htmlFor="website"
                  helper="Opcional. Si no tienes web, déjalo vacío."
                >
                  <input id="website" name="website" type="url" className="form-control" />
                </FormField>
                <FormField
                  label="Notas operativas"
                  htmlFor="notes"
                  fullWidth
                >
                  <textarea
                    id="notes"
                    name="notes"
                    placeholder="Ej: servicio 24/7, cobertura comunal, tipo de atención, etc."
                    className="form-control min-h-28 resize-y"
                  />
                </FormField>
                <FormField
                  label="Ubicación pública"
                  fullWidth
                  helper="Haz clic en el mapa para fijar la ubicación real. Sin geocodificación externa, la ficha pública se mostrará con comuna, región y punto confirmado en mapa."
                >
                  <div className="overflow-hidden rounded-[1.1rem] border border-app-border-strong min-h-[280px]">
                    <LocationPicker
                      latitude={selectedLatitude}
                      longitude={selectedLongitude}
                      onChange={(latitude, longitude) => {
                        setSelectedLatitude(latitude);
                        setSelectedLongitude(longitude);
                      }}
                    />
                  </div>
                  <InfoBox className="mt-2">
                    {selectedLatitude !== undefined && selectedLongitude !== undefined
                      ? `Punto seleccionado: ${selectedLatitude.toFixed(6)}, ${selectedLongitude.toFixed(6)}`
                      : "Aún no hay punto seleccionado."}
                  </InfoBox>
                </FormField>
              </FormGrid>

              <FormCheckbox htmlFor="marketing_opt_in">
                <input
                  id="marketing_opt_in"
                  name="marketing_opt_in"
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
                />
                <span>Recibir novedades del producto y futuras opciones comerciales</span>
              </FormCheckbox>

              <Button type="submit" disabled={loading}>
                {loading ? "Creando cuenta..." : "Crear cuenta comercial"}
              </Button>

              {loading ? <LoadingPanel message="Registrando negocio..." /> : null}
              {error ? <ErrorState message={error} /> : null}
              {successMessage ? <div className="success-banner">{successMessage}</div> : null}
            </form>
          </SurfaceCard>
        }
        aside={
          <>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Operación comercial</h3>
              <InfoBox>
                La cuenta queda creada y la asignación de planes se administra desde membresías, no
                desde el perfil comercial.
              </InfoBox>
            </SurfaceCard>

            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Qué deja listo este alta</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Se crea el usuario, el perfil comercial y la ficha base para que luego puedas sumar
                sucursales y asignaciones de membresía sin lógica duplicada.
              </p>
            </SurfaceCard>
          </>
        }
      />
    </PageShell>
  );
}
