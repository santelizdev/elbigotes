"use client";

import { LeafletMap } from "@/components/map/leaflet-map";
import { Button } from "@/components/ui/button";
import { LostPetReportCard } from "@/components/lost-pets/lost-pet-report-card";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
import { LostPetReport } from "@/lib/types";

export function LostPetsExplorer({ reports }: { reports: LostPetReport[] }) {
  const points = reports
    .filter(
      (report) =>
        report.latitude !== null &&
        report.longitude !== null &&
        Number.isFinite(report.latitude) &&
        Number.isFinite(report.longitude),
    )
    .map((report) => ({
      id: report.id,
      latitude: report.latitude as number,
      longitude: report.longitude as number,
      title: report.petName,
      subtitle: report.lastSeenAddress,
      accent: "var(--accent-gold)",
    }));

  return (
    <PageShell className="gap-5 pb-8 pt-5">
      <PageHero
        eyebrow="Utilidad social"
        title="Mascotas perdidas sobre el mapa"
        description="Reunimos reportes activos con última ubicación conocida para que la búsqueda empiece desde el territorio y no desde un muro de avisos dispersos."
        className="border-[color-mix(in_srgb,var(--accent-emerald)_18%,transparent)] bg-[radial-gradient(circle_at_top_left,color-mix(in_srgb,var(--accent-emerald)_16%,transparent),transparent_28%),radial-gradient(circle_at_top_right,color-mix(in_srgb,var(--accent-emerald)_9%,transparent),transparent_26%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))]"
        actions={
          <Button href="/publicar-mascota-perdida" variant="primary">
            Publicar 📢
          </Button>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(420px,0.96fr)_minmax(0,1.1fr)]">
        <aside className="grid content-start gap-4">
          <SurfaceCard className="grid gap-4 p-4">
            <SectionHeader
              eyebrow="Reportes activos"
              title="Últimos avisos"
              compact
              action={<span className="text-sm text-app-text-muted">{reports.length} reportes</span>}
            />

            <div className="stack-lg">
              {reports.map((report) => (
                <LostPetReportCard key={report.id} report={report} />
              ))}
            </div>
          </SurfaceCard>
        </aside>

        <section className="relative isolate min-h-[26rem] overflow-hidden rounded-[1.6rem] border border-app-border bg-app-background xl:min-h-[40rem]">
          <div className="pointer-events-none absolute left-4 top-4 z-[500]">
            <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-app-border bg-[color-mix(in_srgb,var(--background-soft)_78%,var(--surface)_22%)] px-4 py-3 shadow-soft">
              <strong className="text-[0.95rem] text-app-text">Búsqueda territorial</strong>
              <span className="text-[0.84rem] text-app-text-muted">
                Prioriza radio cercano y última referencia conocida
              </span>
            </div>
          </div>
          {points.length ? (
            <LeafletMap points={points} />
          ) : (
            <div className="feedback-panel">
              Aún no hay reportes con coordenadas confirmadas para mostrar en el mapa.
            </div>
          )}
        </section>
      </div>
    </PageShell>
  );
}
