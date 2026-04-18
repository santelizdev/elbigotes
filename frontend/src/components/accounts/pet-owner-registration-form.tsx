"use client";

import { FormEvent, useState } from "react";

import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { DashboardGrid } from "@/components/ui/dashboard-grid";
import { FormCheckbox, FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
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
    <PageShell>
      <PageHero
        eyebrow="Registro de tutor"
        title="Alta de tutor y mascota"
        description="Este flujo crea dos fichas desde el principio: la del tutor y la de su mascota. Así dejamos la base lista para campañas, fechas relevantes y comunicación personalizada."
        actions={
          <Button href="/registro" variant="ghost">
            Volver a tipos de cuenta
          </Button>
        }
      />

      <DashboardGrid
        main={
          <SurfaceCard className="grid gap-4">
            <p className="eyebrow">Cuenta personal</p>
            <h2 className="m-0 font-display-ui text-3xl leading-tight">
              Crear tutor y primera mascota
            </h2>
            <form className="grid gap-4" onSubmit={handleSubmit}>
              <FormGrid>
                <FormField label="Nombre" htmlFor="first_name">
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
                <FormField label="Teléfono" htmlFor="phone">
                  <input id="phone" name="phone" required className="form-control" />
                </FormField>
                <FormField label="Dirección" htmlFor="address_line">
                  <input
                    id="address_line"
                    name="address_line"
                    placeholder="Calle, número o referencia útil"
                    className="form-control"
                  />
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
              </FormGrid>

              <InfoBox>
                La ficha de mascota permite luego campañas por cumpleaños, especie, edad y momento
                de vida sin tener que rehacer el perfil del usuario.
              </InfoBox>

              <FormGrid>
                <FormField label="Nombre mascota" htmlFor="pet_name">
                  <input id="pet_name" name="pet_name" required className="form-control" />
                </FormField>
                <FormField label="Especie" htmlFor="pet_species">
                  <select id="pet_species" name="pet_species" defaultValue="dog" className="form-control">
                    <option value="dog">Perro</option>
                    <option value="cat">Gato</option>
                    <option value="other">Otra</option>
                  </select>
                </FormField>
                <FormField label="Raza" htmlFor="pet_breed">
                  <input id="pet_breed" name="pet_breed" className="form-control" />
                </FormField>
                <FormField label="Sexo" htmlFor="pet_sex">
                  <select id="pet_sex" name="pet_sex" defaultValue="unknown" className="form-control">
                    <option value="unknown">No identificado</option>
                    <option value="male">Macho</option>
                    <option value="female">Hembra</option>
                  </select>
                </FormField>
                <FormField label="Fecha de nacimiento" htmlFor="pet_birth_date">
                  <input id="pet_birth_date" name="pet_birth_date" type="date" className="form-control" />
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
                <span>Acepto recibir comunicaciones útiles y campañas personalizadas</span>
              </FormCheckbox>

              <Button type="submit" disabled={loading}>
                {loading ? "Creando cuenta..." : "Crear cuenta de tutor"}
              </Button>

              {loading ? <LoadingPanel message="Registrando tutor y mascota..." /> : null}
              {error ? <ErrorState message={error} /> : null}
              {successMessage ? <div className="success-banner">{successMessage}</div> : null}
            </form>
          </SurfaceCard>
        }
        aside={
          <>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">
                Base para marketing responsable
              </h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Desde este alta ya quedan disponibles edad aproximada, especie, raza y
                consentimiento de contacto, que son la base mínima para automatizaciones futuras.
              </p>
            </SurfaceCard>

            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Qué viene después</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Este módulo deja el terreno listo para login, múltiples mascotas por tutor,
                recordatorios de salud, promociones y mensajería segmentada.
              </p>
            </SurfaceCard>
          </>
        }
      />
    </PageShell>
  );
}
