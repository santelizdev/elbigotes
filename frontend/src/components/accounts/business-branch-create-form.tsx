"use client";

import { FormEvent, useState } from "react";

import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import {
  createBusinessBranch,
  getStoredAccessToken,
} from "@/lib/services/accounts-service";
import { CHILE_REGIONS, DEFAULT_REGION, getCommunesForRegion } from "@/lib/constants/chile-locations";
import { getApiErrorMessage } from "@/lib/services/api-client";

export function BusinessBranchCreateForm() {
  const [selectedRegion, setSelectedRegion] = useState(DEFAULT_REGION);
  const [selectedLatitude, setSelectedLatitude] = useState<number | undefined>(undefined);
  const [selectedLongitude, setSelectedLongitude] = useState<number | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [missingToken, setMissingToken] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const token = getStoredAccessToken();
    if (!token) {
      setMissingToken(true);
      return;
    }

    if (selectedLatitude === undefined || selectedLongitude === undefined) {
      setError("Debes confirmar la ubicación de la sucursal haciendo clic en el mapa.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData(event.currentTarget);

    try {
      await createBusinessBranch(token, {
        branch_name: String(formData.get("branch_name") ?? ""),
        phone: String(formData.get("phone") ?? ""),
        commune: String(formData.get("commune") ?? ""),
        region: String(formData.get("region") ?? "") || DEFAULT_REGION,
        website: String(formData.get("website") ?? ""),
        place_label: String(formData.get("place_label") ?? ""),
        latitude: selectedLatitude,
        longitude: selectedLongitude,
        notes: String(formData.get("notes") ?? ""),
      });

      event.currentTarget.reset();
      setSelectedRegion(DEFAULT_REGION);
      setSelectedLatitude(undefined);
      setSelectedLongitude(undefined);
      setSuccessMessage(
        "Sucursal creada. Quedó en revisión manual antes de mostrarse públicamente.",
      );
    } catch (error) {
      setError(
        getApiErrorMessage(error, "No pudimos crear la sucursal. Revisa los datos e intenta nuevamente."),
      );
    } finally {
      setLoading(false);
    }
  }

  if (missingToken) {
    return <AccountAccessNotice />;
  }

  return (
    <PageShell>
      <PageHero
        eyebrow="Área cliente"
        title="Añadir sucursal"
        description="Cada nueva sucursal nace como ficha pública independiente, pero queda asociada al mismo perfil comercial y entra a revisión manual antes de publicarse."
      />

      <SurfaceCard className="grid gap-6">
        <InfoBox tone="muted">
          Para publicar bien esta sucursal necesitamos una referencia visible y una ubicación precisa confirmada en el mapa.
        </InfoBox>

        <form className="grid gap-5" onSubmit={handleSubmit}>
          <FormGrid>
            <FormField label="Nombre de la sucursal" htmlFor="branch_name">
              <input className="form-control" id="branch_name" name="branch_name" required />
            </FormField>
            <FormField label="Teléfono de la sucursal" htmlFor="phone">
              <input className="form-control" id="phone" name="phone" />
            </FormField>
            <FormField label="Comuna" htmlFor="commune">
              <select className="form-control" id="commune" name="commune" required>
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
                className="form-control"
                id="region"
                name="region"
                value={selectedRegion}
                onChange={(event) => setSelectedRegion(event.target.value)}
              >
                {CHILE_REGIONS.map((item) => (
                  <option key={item.region} value={item.region}>
                    {item.region}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField label="Sitio web" htmlFor="website">
              <input className="form-control" id="website" name="website" type="url" />
            </FormField>
            <FormField
              label="Dirección visible o referencia operativa"
              htmlFor="place_label"
              fullWidth
            >
              <input
                className="form-control"
                id="place_label"
                name="place_label"
                placeholder="Calle, número o punto claramente identificable"
                required
              />
            </FormField>
            <FormField
              label="Ubicación de la sucursal"
              fullWidth
              helper="Haz clic en el mapa para dejar fijada la ubicación exacta."
            >
              <div className="min-h-[280px] overflow-hidden rounded-[1.1rem] border border-app-border-strong">
                <LocationPicker
                  latitude={selectedLatitude}
                  longitude={selectedLongitude}
                  onChange={(latitude, longitude) => {
                    setSelectedLatitude(latitude);
                    setSelectedLongitude(longitude);
                  }}
                />
              </div>
            </FormField>
            <FormField label="Notas internas" htmlFor="notes" fullWidth>
              <textarea className="form-control min-h-[110px] resize-y" id="notes" name="notes" />
            </FormField>
          </FormGrid>

          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={loading}>
              {loading ? "Creando..." : "Crear sucursal"}
            </Button>
            <Button href="/mi-negocio" variant="ghost">
              Volver al resumen
            </Button>
          </div>

          {loading ? <LoadingPanel message="Creando sucursal..." /> : null}
          {error ? <ErrorState message={error} /> : null}
          {successMessage ? <div className="success-banner">{successMessage}</div> : null}
        </form>
      </SurfaceCard>
    </PageShell>
  );
}
