"use client";

import { FormEvent, useState } from "react";

import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormCheckbox, FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { createLostPetReport } from "@/lib/services/lost-pets-service";

export function LostPetReportForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [selectedLatitude, setSelectedLatitude] = useState<number | undefined>(undefined);
  const [selectedLongitude, setSelectedLongitude] = useState<number | undefined>(undefined);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    const rawFormData = new FormData(form);
    const submitData = new FormData();

    if (selectedLatitude === undefined || selectedLongitude === undefined) {
      setLoading(false);
      setError("Debes confirmar el último punto visto haciendo clic en el mapa.");
      return;
    }

    const lastSeenAtValue = String(rawFormData.get("last_seen_at") ?? "");
    const lastSeenAtIso = lastSeenAtValue ? new Date(lastSeenAtValue).toISOString() : "";

    submitData.set("pet_name", String(rawFormData.get("pet_name") ?? ""));
    submitData.set("species", String(rawFormData.get("species") ?? "dog"));
    submitData.set("breed", String(rawFormData.get("breed") ?? ""));
    submitData.set("sex", String(rawFormData.get("sex") ?? "unknown"));
    submitData.set("color_description", String(rawFormData.get("color_description") ?? ""));
    submitData.set("status", "lost");
    submitData.set("last_seen_at", lastSeenAtIso);
    submitData.set("last_seen_address", String(rawFormData.get("last_seen_address") ?? ""));
    submitData.set("last_seen_reference", String(rawFormData.get("last_seen_reference") ?? ""));
    submitData.set("last_seen_latitude", String(selectedLatitude));
    submitData.set("last_seen_longitude", String(selectedLongitude));
    submitData.set("reporter_name", String(rawFormData.get("reporter_name") ?? ""));
    submitData.set("reporter_phone", String(rawFormData.get("reporter_phone") ?? ""));
    submitData.set("reporter_email", String(rawFormData.get("reporter_email") ?? ""));
    submitData.set(
      "is_reward_offered",
      String(rawFormData.get("is_reward_offered") === "on"),
    );

    const rewardAmount = String(rawFormData.get("reward_amount") ?? "");
    if (rewardAmount) {
      submitData.set("reward_amount", rewardAmount);
    }

    const photo = rawFormData.get("photo");
    if (photo instanceof File && photo.size > 0) {
      submitData.set("photo", photo);
    }

    try {
      await createLostPetReport(submitData);

      form.reset();
      setSelectedLatitude(undefined);
      setSelectedLongitude(undefined);
      setSuccessMessage(
        "Reporte recibido. Quedó en revisión manual antes de mostrarse en la sección pública.",
      );
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          "No fue posible publicar el reporte. Revisa la imagen subida, la conexión con el backend o vuelve a intentarlo.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageShell>
      <PageHero
        eyebrow="Publicación guiada"
        title="Publicar una mascota perdida"
        description="Este flujo prioriza la última ubicación conocida, una foto liviana y un contacto claro para activar la búsqueda sin pedir datos técnicos al usuario."
        className="border-[rgba(251,191,36,0.18)] bg-[radial-gradient(circle_at_top_left,rgba(251,191,36,0.18),transparent_32%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))]"
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <SurfaceCard className="grid gap-5">
          <form className="grid gap-5" onSubmit={handleSubmit}>
          {/* El formulario agrupa primero identidad y último punto conocido porque eso es lo que activa la búsqueda real. */}
          <FormGrid>
            <FormField label="Nombre de la mascota" htmlFor="pet_name">
              <input className="form-control" id="pet_name" name="pet_name" required />
            </FormField>
            <FormField label="Especie" htmlFor="species">
              <select className="form-control" id="species" name="species" defaultValue="dog">
                <option value="dog">Perro</option>
                <option value="cat">Gato</option>
                <option value="other">Otra</option>
              </select>
            </FormField>
            <FormField label="Raza o descripción breve" htmlFor="breed">
              <input className="form-control" id="breed" name="breed" />
            </FormField>
            <FormField label="Sexo" htmlFor="sex">
              <select className="form-control" id="sex" name="sex" defaultValue="unknown">
                <option value="unknown">No identificado</option>
                <option value="male">Macho</option>
                <option value="female">Hembra</option>
              </select>
            </FormField>
            <FormField label="Color y aspecto visible" htmlFor="color_description" fullWidth>
              <input className="form-control" id="color_description" name="color_description" required />
            </FormField>
            <FormField label="Fecha y hora del último avistamiento" htmlFor="last_seen_at">
              <input className="form-control" id="last_seen_at" name="last_seen_at" type="datetime-local" required />
            </FormField>
            <FormField label="Dirección o referencia principal" htmlFor="last_seen_address" fullWidth>
              <input className="form-control" id="last_seen_address" name="last_seen_address" required />
            </FormField>
            <FormField label="Referencia adicional" htmlFor="last_seen_reference" fullWidth>
              <input className="form-control" id="last_seen_reference" name="last_seen_reference" />
            </FormField>
            <FormField
              label="Último punto visto en el mapa"
              fullWidth
              helper="Haz clic en el mapa para dejar la ubicación territorial del aviso y que el reporte se vea realmente en la vista pública."
            >
              <div className="min-h-[280px] overflow-hidden rounded-[1rem] border border-app-border-strong">
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
            <FormField label="Nombre de contacto" htmlFor="reporter_name">
              <input className="form-control" id="reporter_name" name="reporter_name" required />
            </FormField>
            <FormField label="Teléfono" htmlFor="reporter_phone">
              <input className="form-control" id="reporter_phone" name="reporter_phone" required />
            </FormField>
            <FormField label="Email" htmlFor="reporter_email">
              <input className="form-control" id="reporter_email" name="reporter_email" type="email" />
            </FormField>
            <FormField
              label="Foto de la mascota"
              htmlFor="photo"
              fullWidth
              helper="Sube una imagen JPG, PNG o WebP. El backend la comprimirá para no saturar el servidor."
            >
              <input
                className="form-control"
                id="photo"
                name="photo"
                type="file"
                accept="image/jpeg,image/png,image/webp"
              />
            </FormField>
            <FormField label="Recompensa" fullWidth className="gap-3">
              <div className="grid gap-3 md:grid-cols-[minmax(0,220px)_minmax(0,1fr)] md:items-end">
                <FormCheckbox htmlFor="is_reward_offered">
                  <input id="is_reward_offered" name="is_reward_offered" type="checkbox" />
                  <span>Se ofrece recompensa</span>
                </FormCheckbox>
                <div className="grid gap-2">
                  <label htmlFor="reward_amount" className="text-[0.92rem] font-semibold">
                    Monto recompensa
                  </label>
                  <input
                    className="form-control"
                    id="reward_amount"
                    name="reward_amount"
                    type="number"
                    min="0"
                    step="1000"
                  />
                </div>
              </div>
            </FormField>
          </FormGrid>

          <Button type="submit" disabled={loading} className="w-full sm:w-auto">
            {loading ? "Publicando..." : "Publicar reporte"}
          </Button>

          {loading ? <LoadingPanel message="Enviando reporte al backend..." /> : null}
          {error ? <ErrorState message={error} /> : null}
          {successMessage ? <div className="success-banner">{successMessage}</div> : null}
        </form>
        </SurfaceCard>

        <aside className="grid content-start gap-4">
          <SurfaceCard className="grid gap-3 bg-app-surface-raised">
            <h3>Cómo está pensada la UX</h3>
            <p>
              El formulario pide primero la ubicación y los rasgos útiles porque son los datos más
              relevantes para activar una búsqueda territorial rápida en mapa.
            </p>
          </SurfaceCard>
          <SurfaceCard className="grid gap-3 bg-app-surface-raised">
            <h3>Consejos para publicar mejor</h3>
            <p>
              Usa una referencia concreta, agrega un número siempre disponible y describe collar,
              color general, tamaño y la calle o punto donde fue visto por última vez.
            </p>
          </SurfaceCard>
          <SurfaceCard className="grid gap-4 bg-app-surface-raised">
            <h3>Preparado para crecer</h3>
            <p>
              Este flujo ya deja espacio para validación, moderación, perfiles reclamados,
              destacadas y futuras notificaciones geolocalizadas.
            </p>
            <InfoBox tone="muted">
              Esta capa ya queda lista para sumar alertas geolocalizadas, guardado de búsquedas y difusión social sin rediseñar la base.
            </InfoBox>
            <Button href="/mascotas-perdidas" variant="secondary" fullWidth>
              Ver reportes activos
            </Button>
          </SurfaceCard>
        </aside>
      </div>
    </PageShell>
  );
}
