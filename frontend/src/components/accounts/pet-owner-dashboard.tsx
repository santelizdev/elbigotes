"use client";

import { useEffect, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import {
  clearStoredAccessToken,
  getPetOwnerWorkspace,
  getStoredAccessToken,
  PetOwnerWorkspaceResponse,
} from "@/lib/services/accounts-service";
import { getApiErrorMessage } from "@/lib/services/api-client";

function formatModerationStatus(status: string) {
  const labels: Record<string, string> = {
    pending: "Pendiente de moderación",
    approved: "Publicado",
    rejected: "Rechazado",
  };
  return labels[status] ?? status;
}

function formatReportStatus(status: string) {
  const labels: Record<string, string> = {
    lost: "Extraviada",
    sighted: "Vista",
    reunited: "Reencontrada",
  };
  return labels[status] ?? status;
}

export function PetOwnerDashboard() {
  const [workspace, setWorkspace] = useState<PetOwnerWorkspaceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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
        const response = await getPetOwnerWorkspace(token);
        setWorkspace(response);
      } catch (error) {
        clearStoredAccessToken();
        setError(
          getApiErrorMessage(
            error,
            "No pudimos cargar tu área personal. Inicia sesión nuevamente.",
          ),
        );
      } finally {
        setLoading(false);
      }
    }

    loadWorkspace();
  }, []);

  if (loading) {
    return <LoadingPanel message="Cargando área personal..." />;
  }

  if (missingToken) {
    return (
      <AccountAccessNotice message="Ingresa con tu cuenta de tutor o crea una nueva para gestionar mascotas y reportes." />
    );
  }

  if (error || !workspace) {
    return (
      <div className={styles.page}>
        <ErrorState message={error ?? "No pudimos cargar el panel de tutor."} />
      </div>
    );
  }

  const approvedReports = workspace.reports.filter(
    (report) => report.moderation_status === "approved",
  ).length;

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Área de tutor</p>
        <h1 className="page-title">{workspace.user.first_name || workspace.user.email}</h1>
        <p className="page-lead">
          Este panel reúne tu perfil, tus mascotas registradas y el seguimiento de reportes de
          mascotas extraviadas desde una sola vista.
        </p>
        <div className={styles.heroActions}>
          <Button href="/publicar-mascota-perdida" variant="primary">
            Publicar nuevo reporte
          </Button>
          <Button href="/mascotas-perdidas" variant="secondary">
            Ver mapa público
          </Button>
        </div>
      </section>

      <section className={styles.cards}>
        <article className={styles.card}>
          <p className="eyebrow">Mascotas registradas</p>
          <h3>{workspace.profile.pets.length}</h3>
          <p>Tu ficha ya puede centralizar historial de mascotas y campañas futuras.</p>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Reportes creados</p>
          <h3>{workspace.reports.length}</h3>
          <p>{approvedReports} reportes ya están publicados y visibles en el mapa público.</p>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Contacto principal</p>
          <h3>{workspace.profile.phone}</h3>
          <p>
            {workspace.profile.address_line
              ? `${workspace.profile.address_line}, ${workspace.profile.commune || "sin comuna"}`
              : "Aún no hay una dirección consolidada en tu perfil."}
          </p>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Fichas guardadas</p>
          <h3>{workspace.saved_places.length}</h3>
          <p>
            Guarda negocios para volver rápido a las fichas que más te interesan y compartirlas
            cuando las necesites.
          </p>
        </article>
      </section>

      <section className={styles.grid}>
        <section className={styles.formCard}>
          <p className="eyebrow">Tus mascotas</p>
          <h2>Perfiles activos</h2>
          <div className={styles.stackList}>
            {workspace.profile.pets.map((pet) => (
              <article key={pet.id} className={styles.listCard}>
                <div>
                  <strong>{pet.name}</strong>
                  <p>
                    {pet.species}
                    {pet.breed ? ` · ${pet.breed}` : ""}
                    {pet.birth_date ? ` · Nació el ${pet.birth_date}` : ""}
                  </p>
                </div>
                <span className={styles.statusBox}>{pet.is_active ? "Activa" : "Inactiva"}</span>
              </article>
            ))}
          </div>
        </section>

        <aside className={styles.aside}>
          <section className={styles.asideCard}>
            <h3>Membresías</h3>
            <p>
              {workspace.profile.memberships.length
                ? `${workspace.profile.memberships.length} asignación(es) de membresía disponible(s) para esta cuenta.`
                : "Todavía no hay una membresía asignada a este perfil."}
            </p>
          </section>
          <section className={styles.asideCard}>
            <h3>Comunicaciones</h3>
            <p>
              {workspace.profile.marketing_opt_in
                ? "Aceptaste recibir avisos y campañas útiles para tus mascotas."
                : "Tu cuenta está marcada sin comunicaciones promocionales."}
            </p>
          </section>
        </aside>
      </section>

      <section className={styles.formCard}>
        <p className="eyebrow">Tus fichas</p>
        <h2>Negocios guardados</h2>
        <div className={styles.stackList}>
          {workspace.saved_places.length ? (
            workspace.saved_places.map((place) => (
              <article key={place.slug} className={styles.listCard}>
                <div>
                  <strong>{place.name}</strong>
                  <p>
                    {place.commune}, {place.region}
                    {place.google_rating ? ` · ${place.google_rating.toFixed(1)} estrellas` : ""}
                    {place.google_reviews_count ? ` · ${place.google_reviews_count} reseñas` : ""}
                  </p>
                </div>
                <Button href={`/lugares/${place.slug}`} variant="secondary">
                  Abrir ficha
                </Button>
              </article>
            ))
          ) : (
            <div className={styles.statusBox}>
              Todavía no has guardado fichas. Cuando encuentres un negocio interesante, podrás
              dejarlo en tu perfil con un clic.
            </div>
          )}
        </div>
      </section>

      <section className={styles.formCard}>
        <p className="eyebrow">Mascotas extraviadas</p>
        <h2>Seguimiento de reportes</h2>
        <div className={styles.stackList}>
          {workspace.reports.length ? (
            workspace.reports.map((report) => (
              <article key={report.id} className={styles.listCard}>
                <div>
                  <strong>{report.pet_name}</strong>
                  <p>
                    {formatReportStatus(report.status)} · {report.last_seen_address}
                  </p>
                </div>
                <span className={styles.statusBox}>
                  {formatModerationStatus(report.moderation_status)}
                </span>
              </article>
            ))
          ) : (
            <div className={styles.statusBox}>
              Todavía no has generado reportes desde esta cuenta.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
