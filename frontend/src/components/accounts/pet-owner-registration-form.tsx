"use client";

import { FormEvent, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import {
  CHILE_REGIONS,
  DEFAULT_REGION,
  getCommunesForRegion,
} from "@/lib/constants/chile-locations";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { PetOwnerRegistrationPayload, registerPetOwnerAccount } from "@/lib/services/accounts-service";

export function PetOwnerRegistrationForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<string>(DEFAULT_REGION);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData(form);
    const payload: PetOwnerRegistrationPayload = {
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? ""),
      first_name: String(formData.get("first_name") ?? ""),
      last_name: String(formData.get("last_name") ?? ""),
      phone: String(formData.get("phone") ?? ""),
      address_line: String(formData.get("address_line") ?? ""),
      commune: String(formData.get("commune") ?? ""),
      region: String(formData.get("region") ?? "") || DEFAULT_REGION,
      marketing_opt_in: formData.get("marketing_opt_in") === "on",
      pet: {
        name: String(formData.get("pet_name") ?? ""),
        species: String(formData.get("pet_species") ?? "dog"),
        breed: String(formData.get("pet_breed") ?? ""),
        sex: String(formData.get("pet_sex") ?? "unknown"),
        birth_date: String(formData.get("pet_birth_date") ?? "") || undefined,
      },
    };

    try {
      const response = await registerPetOwnerAccount(payload);
      form.reset();
      setSelectedRegion(DEFAULT_REGION);
      const petName =
        response && typeof response === "object" && "initial_pet" in response
          ? response.initial_pet.name
          : "La mascota";
      setSuccessMessage(
        `Cuenta creada. ${petName} ya quedó registrado como primera mascota del tutor.`,
      );
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          "No pudimos crear la cuenta del tutor. Revisa los datos e intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Registro de tutor</p>
        <h1 className="page-title">Alta de tutor y mascota</h1>
        <p className="page-lead">
          Este flujo crea dos fichas desde el principio: la del tutor y la de su mascota. Así
          dejamos la base lista para campañas, fechas relevantes y comunicación personalizada.
        </p>
        <div className={styles.heroActions}>
          <Button href="/registro" variant="ghost">
            Volver a tipos de cuenta
          </Button>
        </div>
      </section>

      <div className={styles.grid}>
        <section className={styles.formCard}>
          <p className="eyebrow">Cuenta personal</p>
          <h2>Crear tutor y primera mascota</h2>
          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.formGrid}>
              <div className={styles.field}>
                <label htmlFor="first_name">Nombre</label>
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
                <label htmlFor="phone">Teléfono</label>
                <input id="phone" name="phone" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="address_line">Dirección</label>
                <input
                  id="address_line"
                  name="address_line"
                  placeholder="Calle, número o referencia útil"
                />
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
            </div>

            <div className={styles.statusBox}>
              La ficha de mascota permite luego campañas por cumpleaños, especie, edad y momento de
              vida sin tener que rehacer el perfil del usuario.
            </div>

            <div className={styles.formGrid}>
              <div className={styles.field}>
                <label htmlFor="pet_name">Nombre mascota</label>
                <input id="pet_name" name="pet_name" required />
              </div>
              <div className={styles.field}>
                <label htmlFor="pet_species">Especie</label>
                <select id="pet_species" name="pet_species" defaultValue="dog">
                  <option value="dog">Perro</option>
                  <option value="cat">Gato</option>
                  <option value="other">Otra</option>
                </select>
              </div>
              <div className={styles.field}>
                <label htmlFor="pet_breed">Raza</label>
                <input id="pet_breed" name="pet_breed" />
              </div>
              <div className={styles.field}>
                <label htmlFor="pet_sex">Sexo</label>
                <select id="pet_sex" name="pet_sex" defaultValue="unknown">
                  <option value="unknown">No identificado</option>
                  <option value="male">Macho</option>
                  <option value="female">Hembra</option>
                </select>
              </div>
              <div className={styles.field}>
                <label htmlFor="pet_birth_date">Fecha de nacimiento</label>
                <input id="pet_birth_date" name="pet_birth_date" type="date" />
              </div>
            </div>

            <label className={styles.checkbox} htmlFor="marketing_opt_in">
              <input id="marketing_opt_in" name="marketing_opt_in" type="checkbox" defaultChecked />
              <span>Acepto recibir comunicaciones útiles y campañas personalizadas</span>
            </label>

            <Button type="submit" disabled={loading}>
              {loading ? "Creando cuenta..." : "Crear cuenta de tutor"}
            </Button>

            {loading ? <LoadingPanel message="Registrando tutor y mascota..." /> : null}
            {error ? <ErrorState message={error} /> : null}
            {successMessage ? <div className="success-banner">{successMessage}</div> : null}
          </form>
        </section>

        <aside className={styles.aside}>
          <section className={styles.asideCard}>
            <h3>Base para marketing responsable</h3>
            <p>
              Desde este alta ya quedan disponibles edad aproximada, especie, raza y consentimiento
              de contacto, que son la base mínima para automatizaciones futuras.
            </p>
          </section>

          <section className={styles.asideCard}>
            <h3>Qué viene después</h3>
            <p>
              Este módulo deja el terreno listo para login, múltiples mascotas por tutor,
              recordatorios de salud, promociones y mensajería segmentada.
            </p>
          </section>
        </aside>
      </div>
    </div>
  );
}
