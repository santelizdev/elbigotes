"use client";

import { FormEvent, useEffect, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
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
      <div className={styles.page}>
        <ErrorState message={error ?? "No pudimos cargar el perfil comercial."} />
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Área cliente</p>
        <h1 className="page-title">Editar datos de registro</h1>
        <p className="page-lead">
          Ajusta la información principal de tu cuenta comercial sin tocar el estado editorial de
          publicación.
        </p>
      </section>

      <section className={styles.formCard}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGrid}>
            <div className={styles.field}>
              <label htmlFor="first_name">Nombre responsable</label>
              <input id="first_name" name="first_name" defaultValue={workspace.user.first_name} required />
            </div>
            <div className={styles.field}>
              <label htmlFor="last_name">Apellido</label>
              <input id="last_name" name="last_name" defaultValue={workspace.user.last_name} />
            </div>
            <div className={styles.field}>
              <label htmlFor="business_name">Nombre comercial</label>
              <input
                id="business_name"
                name="business_name"
                defaultValue={workspace.profile.business_name}
                required
              />
            </div>
            <div className={styles.field}>
              <label htmlFor="phone">Teléfono</label>
              <input id="phone" name="phone" defaultValue={workspace.profile.phone} required />
            </div>
            <div className={styles.field}>
              <label htmlFor="commune">Comuna</label>
              <select id="commune" name="commune" defaultValue={workspace.profile.commune} required>
                <option value="">Selecciona una comuna</option>
                {getCommunesForRegion(selectedRegion).map((commune) => (
                  <option key={commune} value={commune}>
                    {commune}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label htmlFor="region">Región</label>
              <select
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
            </div>
            <div className={styles.field}>
              <label htmlFor="website">Sitio web</label>
              <input id="website" name="website" type="url" defaultValue={workspace.profile.website} />
            </div>
            <div className={styles.fieldFull}>
              <label htmlFor="notes">Notas comerciales</label>
              <textarea id="notes" name="notes" defaultValue={workspace.profile.notes} />
            </div>
          </div>

          <label className={styles.checkbox} htmlFor="marketing_opt_in">
            <input
              id="marketing_opt_in"
              name="marketing_opt_in"
              type="checkbox"
              defaultChecked={workspace.profile.marketing_opt_in}
            />
            <span>Recibir novedades de producto y comercialización</span>
          </label>

          <div className={styles.heroActions}>
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
      </section>
    </div>
  );
}
