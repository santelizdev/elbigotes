"use client";

import { FormEvent, useState } from "react";

import styles from "@/components/lost-pets/lost-pet-report-form.module.css";
import { LocationPicker } from "@/components/map/location-picker";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
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
    <div className={styles.shell}>
      <section className={styles.intro}>
        <p className="eyebrow">Publicación guiada</p>
        <h1 className="page-title">Publicar una mascota perdida</h1>
        <p className="page-lead">
          Este flujo prioriza la última ubicación conocida, una foto liviana y un contacto claro
          para activar la búsqueda sin pedir datos técnicos al usuario.
        </p>
      </section>

      <div className={styles.grid}>
        <form className={styles.form} onSubmit={handleSubmit}>
          {/* El formulario agrupa primero identidad y último punto conocido porque eso es lo que activa la búsqueda real. */}
          <div className={styles.field}>
            <label htmlFor="pet_name">Nombre de la mascota</label>
            <input id="pet_name" name="pet_name" required />
          </div>
          <div className={styles.field}>
            <label htmlFor="species">Especie</label>
            <select id="species" name="species" defaultValue="dog">
              <option value="dog">Perro</option>
              <option value="cat">Gato</option>
              <option value="other">Otra</option>
            </select>
          </div>
          <div className={styles.field}>
            <label htmlFor="breed">Raza o descripción breve</label>
            <input id="breed" name="breed" />
          </div>
          <div className={styles.field}>
            <label htmlFor="sex">Sexo</label>
            <select id="sex" name="sex" defaultValue="unknown">
              <option value="unknown">No identificado</option>
              <option value="male">Macho</option>
              <option value="female">Hembra</option>
            </select>
          </div>
          <div className={`${styles.field} ${styles.full}`}>
            <label htmlFor="color_description">Color y aspecto visible</label>
            <input id="color_description" name="color_description" required />
          </div>
          <div className={styles.field}>
            <label htmlFor="last_seen_at">Fecha y hora del último avistamiento</label>
            <input id="last_seen_at" name="last_seen_at" type="datetime-local" required />
          </div>
          <div className={`${styles.field} ${styles.full}`}>
            <label htmlFor="last_seen_address">Dirección o referencia principal</label>
            <input id="last_seen_address" name="last_seen_address" required />
          </div>
          <div className={`${styles.field} ${styles.full}`}>
            <label htmlFor="last_seen_reference">Referencia adicional</label>
            <input id="last_seen_reference" name="last_seen_reference" />
          </div>
          <div className={`${styles.field} ${styles.full}`}>
            <label>Último punto visto en el mapa</label>
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
            <span className={styles.helpText}>
              Haz clic en el mapa para dejar la ubicación territorial del aviso y que el reporte se
              vea realmente en la vista pública.
            </span>
          </div>
          <div className={styles.field}>
            <label htmlFor="reporter_name">Nombre de contacto</label>
            <input id="reporter_name" name="reporter_name" required />
          </div>
          <div className={styles.field}>
            <label htmlFor="reporter_phone">Teléfono</label>
            <input id="reporter_phone" name="reporter_phone" required />
          </div>
          <div className={styles.field}>
            <label htmlFor="reporter_email">Email</label>
            <input id="reporter_email" name="reporter_email" type="email" />
          </div>
          <div className={`${styles.field} ${styles.full}`}>
            <label htmlFor="photo">Foto de la mascota</label>
            <input
              id="photo"
              name="photo"
              type="file"
              accept="image/jpeg,image/png,image/webp"
            />
            <span className={styles.helpText}>
              Sube una imagen JPG, PNG o WebP. El backend la comprimirá para no saturar el
              servidor.
            </span>
          </div>
          <div className={styles.field}>
            <label className={styles.checkboxRow} htmlFor="is_reward_offered">
              <input id="is_reward_offered" name="is_reward_offered" type="checkbox" />
              <span>Se ofrece recompensa</span>
            </label>
          </div>
          <div className={styles.field}>
            <label htmlFor="reward_amount">Monto recompensa</label>
            <input id="reward_amount" name="reward_amount" type="number" min="0" step="1000" />
          </div>

          <Button type="submit" disabled={loading}>
            {loading ? "Publicando..." : "Publicar reporte"}
          </Button>

          {loading ? <LoadingPanel message="Enviando reporte al backend..." /> : null}
          {error ? <ErrorState message={error} /> : null}
          {successMessage ? <div className="success-banner">{successMessage}</div> : null}
        </form>

        <aside className={styles.aside}>
          <div className={styles.tipCard}>
            <h3>Cómo está pensada la UX</h3>
            <p>
              El formulario pide primero la ubicación y los rasgos útiles porque son los datos más
              relevantes para activar una búsqueda territorial rápida en mapa.
            </p>
          </div>
          <div className={styles.tipCard}>
            <h3>Consejos para publicar mejor</h3>
            <p>
              Usa una referencia concreta, agrega un número siempre disponible y describe collar,
              color general, tamaño y la calle o punto donde fue visto por última vez.
            </p>
          </div>
          <div className={styles.tipCard}>
            <h3>Preparado para crecer</h3>
            <p>
              Este flujo ya deja espacio para validación, moderación, perfiles reclamados,
              destacadas y futuras notificaciones geolocalizadas.
            </p>
            <Button href="/mascotas-perdidas" variant="secondary" fullWidth>
              Ver reportes activos
            </Button>
          </div>
        </aside>
      </div>
    </div>
  );
}
