"use client";

import { FormEvent, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Área cliente</p>
        <h1 className="page-title">Añadir sucursal</h1>
        <p className="page-lead">
          Cada nueva sucursal nace como ficha pública independiente, pero queda asociada al mismo
          perfil comercial y entra a revisión manual antes de publicarse.
        </p>
      </section>

      <section className={styles.formCard}>
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGrid}>
            <div className={styles.field}>
              <label htmlFor="branch_name">Nombre de la sucursal</label>
              <input id="branch_name" name="branch_name" required />
            </div>
            <div className={styles.field}>
              <label htmlFor="phone">Teléfono de la sucursal</label>
              <input id="phone" name="phone" />
            </div>
            <div className={styles.field}>
              <label htmlFor="commune">Comuna</label>
              <select id="commune" name="commune" required>
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
              <input id="website" name="website" type="url" />
            </div>
            <div className={styles.fieldFull}>
              <label htmlFor="place_label">Dirección visible o referencia operativa</label>
              <input
                id="place_label"
                name="place_label"
                placeholder="Calle, número o punto claramente identificable"
                required
              />
            </div>
            <div className={styles.fieldFull}>
              <label>Ubicación de la sucursal</label>
              <div className={styles.mapPicker}>
                <LocationPicker
                  latitude={selectedLatitude}
                  longitude={selectedLongitude}
                  onChange={(latitude, longitude) => {
                    setSelectedLatitude(latitude);
                    setSelectedLongitude(longitude);
                  }}
                />
              </div>
            </div>
            <div className={styles.fieldFull}>
              <label htmlFor="notes">Notas internas</label>
              <textarea id="notes" name="notes" />
            </div>
          </div>

          <div className={styles.heroActions}>
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
      </section>
    </div>
  );
}
