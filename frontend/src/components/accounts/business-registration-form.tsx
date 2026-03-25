"use client";

import { FormEvent, useMemo, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
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

  const selectedDefinition = useMemo(
    () => businessKinds.find((item) => item.value === selectedKind),
    [businessKinds, selectedKind],
  );

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
      const response = await registerBusinessAccount(payload);
      form.reset();
      setSelectedKind(businessKinds[0]?.value ?? "veterinary");
      setSelectedRegion(DEFAULT_REGION);
      setSelectedLatitude(undefined);
      setSelectedLongitude(undefined);
      const membershipStatus =
        response && typeof response === "object" && "profile" in response
          ? response.profile.membership_status
          : null;
      setSuccessMessage(
        membershipStatus === "free_forever"
          ? "Cuenta creada. La ficha quedó en revisión manual y este tipo de organización seguirá siendo gratuita cuando se publique."
          : "Cuenta creada. La ficha quedó en revisión manual y el negocio sigue marcado con periodo de gracia para futura membresía.",
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Registro comercial</p>
        <h1 className="page-title">Alta de negocio u organización</h1>
        <p className="page-lead">
          Este flujo separa los negocios con membresía potencial de los actores comunitarios que
          quedarán siempre gratuitos, para que el modelo comercial nazca ordenado desde el inicio.
        </p>
        <div className={styles.heroActions}>
          <Button href="/registro" variant="ghost">
            Volver a tipos de cuenta
          </Button>
        </div>
      </section>

      <div className={styles.grid}>
        <section className={styles.formCard}>
          <p className="eyebrow">Datos de alta</p>
          <h2>Crear cuenta comercial</h2>
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.formGrid}>
              <div className={styles.field}>
                <label htmlFor="first_name">Nombre responsable</label>
                <input id="first_name" name="first_name" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="last_name">Apellido</label>
                <input id="last_name" name="last_name" />
              </div>
              <div className={styles.field}>
                <label htmlFor="email">Email</label>
                <input id="email" name="email" type="email" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="password">Password</label>
                <input id="password" name="password" type="password" minLength={8} required />
              </div>
              <div className={styles.field}>
                <label htmlFor="business_name">Nombre comercial</label>
                <input id="business_name" name="business_name" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="business_kind">Tipo de cuenta</label>
                <select
                  id="business_kind"
                  name="business_kind"
                  value={selectedKind}
                  onChange={(event) => setSelectedKind(event.target.value)}
                >
                  {businessKinds.map((kind) => (
                    <option key={kind.value} value={kind.value}>
                      {kind.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className={styles.field}>
                <label htmlFor="phone">Teléfono</label>
                <input id="phone" name="phone" required />
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
                <span className={styles.helper}>Opcional. Si no tienes web, déjalo vacío.</span>
              </div>
              <div className={styles.fieldFull}>
                <label htmlFor="notes">Notas operativas</label>
                <textarea
                  id="notes"
                  name="notes"
                  placeholder="Ej: servicio 24/7, cobertura comunal, tipo de atención, etc."
                />
              </div>
              <div className={styles.fieldFull}>
                <label>Ubicación pública</label>
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
                <span className={styles.helper}>
                  Haz clic en el mapa para fijar la ubicación real. Sin geocodificación externa, la
                  ficha pública se mostrará con comuna, región y punto confirmado en mapa.
                </span>
                <div className={styles.statusBox}>
                  {selectedLatitude !== undefined && selectedLongitude !== undefined
                    ? `Punto seleccionado: ${selectedLatitude.toFixed(6)}, ${selectedLongitude.toFixed(6)}`
                    : "Aún no hay punto seleccionado."}
                </div>
              </div>
            </div>

            <label className={styles.checkbox} htmlFor="marketing_opt_in">
              <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox" defaultChecked />
              <span>Recibir novedades del producto y futuras opciones comerciales</span>
            </label>

            <Button type="submit" disabled={loading}>
              {loading ? "Creando cuenta..." : "Crear cuenta comercial"}
            </Button>

            {loading ? <LoadingPanel message="Registrando negocio..." /> : null}
            {error ? <ErrorState message={error} /> : null}
            {successMessage ? <div className="success-banner">{successMessage}</div> : null}
          </form>
        </section>

        <aside className={styles.aside}>
          <section className={styles.asideCard}>
            <h3>Política comercial inicial</h3>
            <div className={styles.statusBox}>
              {selectedDefinition?.billing_mode === "free_forever"
                ? "Refugios y parques quedan marcados como gratuitos permanentes."
                : "Veterinarias, guarderías y emergencias quedan listas para periodo de gracia y futura membresía."}
            </div>
          </section>

          <section className={styles.asideCard}>
            <h3>Qué deja listo este alta</h3>
            <p>
              Se crea el usuario, el perfil comercial, la clasificación del negocio y el estado de
              membresía inicial para que luego podamos sumar reclamación de fichas y cobro.
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
