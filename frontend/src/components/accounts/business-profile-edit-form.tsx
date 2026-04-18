"use client";

import { FormEvent, useEffect, useState } from "react";

import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormCheckbox, FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import {
  BusinessWorkspaceResponse,
  getBusinessWorkspace,
  getStoredAccessToken,
  updateBusinessWorkspace,
} from "@/lib/services/accounts-service";
import { CHILE_REGIONS, DEFAULT_REGION, getCommunesForRegion } from "@/lib/constants/chile-locations";
import { getApiErrorMessage } from "@/lib/services/api-client";

export function BusinessProfileEditForm() {
  const [workspace, setWorkspace] = useState<BusinessWorkspaceResponse | null>(null);
  const [selectedRegion, setSelectedRegion] = useState(DEFAULT_REGION);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [missingToken, setMissingToken] = useState(false);

  useEffect(() => {
    async function loadWorkspace() {
      const token = getStoredAccessToken();
      if (!token) {
        setMissingToken(true);
        setLoading(false);
        return;
      }

      try {
        const response = await getBusinessWorkspace(token);
        setWorkspace(response);
        setSelectedRegion(response.profile.region || DEFAULT_REGION);
      } catch (error) {
        setError(
          getApiErrorMessage(error, "No pudimos cargar tus datos comerciales para edición."),
        );
      } finally {
        setLoading(false);
      }
    }

    loadWorkspace();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const token = getStoredAccessToken();
    if (!token) {
      setMissingToken(true);
      return;
    }

    setSaving(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData(event.currentTarget);

    try {
      const response = await updateBusinessWorkspace(token, {
        first_name: String(formData.get("first_name") ?? ""),
        last_name: String(formData.get("last_name") ?? ""),
        business_name: String(formData.get("business_name") ?? ""),
        phone: String(formData.get("phone") ?? ""),
        commune: String(formData.get("commune") ?? ""),
        region: String(formData.get("region") ?? "") || DEFAULT_REGION,
        website: String(formData.get("website") ?? ""),
        marketing_opt_in: formData.get("marketing_opt_in") === "on",
        notes: String(formData.get("notes") ?? ""),
      });
      setWorkspace(response);
      setSelectedRegion(response.profile.region || DEFAULT_REGION);
      setSuccessMessage("Datos actualizados. La ficha principal sigue su flujo de revisión habitual.");
    } catch (error) {
      setError(getApiErrorMessage(error, "No pudimos guardar los cambios del perfil comercial."));
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <LoadingPanel message="Cargando perfil comercial..." />;
  }

  if (missingToken) {
    return <AccountAccessNotice />;
  }

  if (!workspace) {
    return (
      <div className="py-8">
        <ErrorState message={error ?? "No pudimos cargar el perfil comercial."} />
      </div>
    );
  }

  return (
    <PageShell>
      <PageHero
        eyebrow="Área cliente"
        title="Editar datos de registro"
        description="Ajusta la información principal de tu cuenta comercial sin tocar el estado editorial de publicación."
      />

      <SurfaceCard className="grid gap-6">
        <InfoBox tone="muted">
          Estos cambios actualizan tu perfil comercial y mantienen el mismo flujo de revisión para la ficha pública.
        </InfoBox>

        <form className="grid gap-5" onSubmit={handleSubmit}>
          <FormGrid>
            <FormField label="Nombre responsable" htmlFor="first_name">
              <input className="form-control" id="first_name" name="first_name" defaultValue={workspace.user.first_name} required />
            </FormField>
            <FormField label="Apellido" htmlFor="last_name">
              <input className="form-control" id="last_name" name="last_name" defaultValue={workspace.user.last_name} />
            </FormField>
            <FormField label="Nombre comercial" htmlFor="business_name">
              <input
                className="form-control"
                id="business_name"
                name="business_name"
                defaultValue={workspace.profile.business_name}
                required
              />
            </FormField>
            <FormField label="Teléfono" htmlFor="phone">
              <input className="form-control" id="phone" name="phone" defaultValue={workspace.profile.phone} required />
            </FormField>
            <FormField label="Comuna" htmlFor="commune">
              <select className="form-control" id="commune" name="commune" defaultValue={workspace.profile.commune} required>
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
              <input className="form-control" id="website" name="website" type="url" defaultValue={workspace.profile.website} />
            </FormField>
            <FormField label="Notas comerciales" htmlFor="notes" fullWidth>
              <textarea className="form-control min-h-[110px] resize-y" id="notes" name="notes" defaultValue={workspace.profile.notes} />
            </FormField>
          </FormGrid>

          <FormCheckbox htmlFor="marketing_opt_in">
            <input
              id="marketing_opt_in"
              name="marketing_opt_in"
              type="checkbox"
              defaultChecked={workspace.profile.marketing_opt_in}
            />
            <span>Recibir novedades de producto y comercialización</span>
          </FormCheckbox>

          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={saving}>
              {saving ? "Guardando..." : "Guardar cambios"}
            </Button>
            <Button href="/mi-negocio" variant="ghost">
              Volver al resumen
            </Button>
          </div>

          {saving ? <LoadingPanel message="Guardando perfil..." /> : null}
          {error ? <ErrorState message={error} /> : null}
          {successMessage ? <div className="success-banner">{successMessage}</div> : null}
        </form>
      </SurfaceCard>
    </PageShell>
  );
}
