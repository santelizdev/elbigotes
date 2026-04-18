"use client";

import { useEffect, useState } from "react";

import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { DashboardGrid } from "@/components/ui/dashboard-grid";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
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
    return <ErrorState message={error ?? "No pudimos cargar el panel de tutor."} />;
  }

  const approvedReports = workspace.reports.filter(
    (report) => report.moderation_status === "approved",
  ).length;

  return (
    <PageShell>
      <PageHero
        eyebrow="Área de tutor"
        title={workspace.user.first_name || workspace.user.email}
        description="Este panel reúne tu perfil, tus mascotas registradas y el seguimiento de reportes de mascotas extraviadas desde una sola vista."
        actions={
          <>
            <Button href="/publicar-mascota-perdida" variant="primary">
              Publicar nuevo reporte
            </Button>
            <Button href="/mascotas-perdidas" variant="secondary">
              Ver mapa público
            </Button>
          </>
        }
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SurfaceCard className="grid gap-3">
          <p className="eyebrow">Mascotas registradas</p>
          <h3 className="m-0 font-display-ui text-3xl leading-tight">
            {workspace.profile.pets.length}
          </h3>
          <p className="m-0 leading-7 text-app-text-soft">
            Tu ficha ya puede centralizar historial de mascotas y campañas futuras.
          </p>
        </SurfaceCard>

        <SurfaceCard className="grid gap-3">
          <p className="eyebrow">Reportes creados</p>
          <h3 className="m-0 font-display-ui text-3xl leading-tight">{workspace.reports.length}</h3>
          <p className="m-0 leading-7 text-app-text-soft">
            {approvedReports} reportes ya están publicados y visibles en el mapa público.
          </p>
        </SurfaceCard>

        <SurfaceCard className="grid gap-3">
          <p className="eyebrow">Contacto principal</p>
          <h3 className="m-0 font-display-ui text-2xl leading-tight">{workspace.profile.phone}</h3>
          <p className="m-0 leading-7 text-app-text-soft">
            {workspace.profile.address_line
              ? `${workspace.profile.address_line}, ${workspace.profile.commune || "sin comuna"}`
              : "Aún no hay una dirección consolidada en tu perfil."}
          </p>
        </SurfaceCard>

        <SurfaceCard className="grid gap-3">
          <p className="eyebrow">Fichas guardadas</p>
          <h3 className="m-0 font-display-ui text-3xl leading-tight">
            {workspace.saved_places.length}
          </h3>
          <p className="m-0 leading-7 text-app-text-soft">
            Guarda negocios para volver rápido a las fichas que más te interesan y compartirlas
            cuando las necesites.
          </p>
        </SurfaceCard>
      </section>

      <DashboardGrid
        main={
          <>
            <SurfaceCard className="grid gap-4">
              <SectionHeader eyebrow="Tus mascotas" title="Perfiles activos" />
              <div className="grid gap-3">
                {workspace.profile.pets.map((pet) => (
                  <article
                    key={pet.id}
                    className="flex flex-col gap-3 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4 md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <strong>{pet.name}</strong>
                      <p className="m-0 text-app-text-soft">
                        {pet.species}
                        {pet.breed ? ` · ${pet.breed}` : ""}
                        {pet.birth_date ? ` · Nació el ${pet.birth_date}` : ""}
                      </p>
                    </div>
                    <span className="rounded-2xl border border-brand-primary/20 bg-brand-primary/10 px-4 py-2 text-sm text-app-text-soft">
                      {pet.is_active ? "Activa" : "Inactiva"}
                    </span>
                  </article>
                ))}
              </div>
            </SurfaceCard>

            <SurfaceCard className="grid gap-4">
              <SectionHeader eyebrow="Tus fichas" title="Negocios guardados" />
              <div className="grid gap-3">
                {workspace.saved_places.length ? (
                  workspace.saved_places.map((place) => (
                    <article
                      key={place.slug}
                      className="flex flex-col gap-3 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4 md:flex-row md:items-center md:justify-between"
                    >
                      <div>
                        <strong>{place.name}</strong>
                        <p className="m-0 text-app-text-soft">
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
                  <div className="rounded-2xl border border-brand-primary/20 bg-brand-primary/10 px-4 py-4 text-app-text-soft">
                    Todavía no has guardado fichas. Cuando encuentres un negocio interesante, podrás
                    dejarlo en tu perfil con un clic.
                  </div>
                )}
              </div>
            </SurfaceCard>

            <SurfaceCard className="grid gap-4">
              <SectionHeader eyebrow="Mascotas extraviadas" title="Seguimiento de reportes" />
              <div className="grid gap-3">
                {workspace.reports.length ? (
                  workspace.reports.map((report) => (
                    <article
                      key={report.id}
                      className="flex flex-col gap-3 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4 md:flex-row md:items-center md:justify-between"
                    >
                      <div>
                        <strong>{report.pet_name}</strong>
                        <p className="m-0 text-app-text-soft">
                          {formatReportStatus(report.status)} · {report.last_seen_address}
                        </p>
                      </div>
                      <span className="rounded-2xl border border-brand-primary/20 bg-brand-primary/10 px-4 py-2 text-sm text-app-text-soft">
                        {formatModerationStatus(report.moderation_status)}
                      </span>
                    </article>
                  ))
                ) : (
                  <div className="rounded-2xl border border-brand-primary/20 bg-brand-primary/10 px-4 py-4 text-app-text-soft">
                    Todavía no has generado reportes desde esta cuenta.
                  </div>
                )}
              </div>
            </SurfaceCard>
          </>
        }
        aside={
          <>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Membresías</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                {workspace.profile.memberships.length
                  ? `${workspace.profile.memberships.length} asignación(es) de membresía disponible(s) para esta cuenta.`
                  : "Todavía no hay una membresía asignada a este perfil."}
              </p>
            </SurfaceCard>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Comunicaciones</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                {workspace.profile.marketing_opt_in
                  ? "Aceptaste recibir avisos y campañas útiles para tus mascotas."
                  : "Tu cuenta está marcada sin comunicaciones promocionales."}
              </p>
            </SurfaceCard>
          </>
        }
      />
    </PageShell>
  );
}
