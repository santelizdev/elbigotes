"use client";

import { LeafletMap } from "@/components/map/leaflet-map";
import { EmptyState } from "@/components/shared/empty-state";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
import { PublicPetOperation } from "@/lib/types";
import { PublicPetOperationCard } from "@/components/operations/public-pet-operation-card";

export function PublicPetOperationsExplorer({ operations }: { operations: PublicPetOperation[] }) {
  const points = operations
    .filter(
      (operation) =>
        operation.latitude !== null &&
        operation.longitude !== null &&
        Number.isFinite(operation.latitude) &&
        Number.isFinite(operation.longitude),
    )
    .map((operation) => ({
      id: operation.slug,
      latitude: operation.latitude as number,
      longitude: operation.longitude as number,
      title: operation.title,
      subtitle: operation.address,
      accent: "var(--accent-coral)",
    }));

  return (
    <PageShell className="gap-5 pb-8 pt-5">
      <PageHero
        eyebrow="Agenda territorial"
        title="Jornadas y operativos para mascotas"
        description="Concentramos operativos públicos y privados vigentes con dirección confirmada para que se puedan descubrir rápido desde una sola capa territorial."
        className="border-[color-mix(in_srgb,var(--accent-coral)_18%,transparent)] bg-[radial-gradient(circle_at_top_left,color-mix(in_srgb,var(--accent-coral)_16%,transparent),transparent_28%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))]"
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(420px,0.96fr)_minmax(0,1.1fr)]">
        <aside className="grid content-start gap-4">
          <SurfaceCard className="grid gap-4 p-4">
            <SectionHeader
              eyebrow="Operativos vigentes"
              title="Agenda publicada"
              compact
              action={<span className="text-sm text-app-text-muted">{operations.length} operativos</span>}
            />

            {operations.length ? (
              <div className="stack-lg">
                {operations.map((operation) => (
                  <PublicPetOperationCard key={operation.slug} operation={operation} />
                ))}
              </div>
            ) : (
              <EmptyState
                title="Todavía no hay operativos vigentes"
                message="Cuando el equipo editorial publique nuevas jornadas con dirección confirmada, aparecerán aquí."
              />
            )}
          </SurfaceCard>
        </aside>

        <section className="relative isolate min-h-[26rem] overflow-hidden rounded-[1.6rem] border border-app-border bg-app-background xl:min-h-[40rem]">
          <div className="pointer-events-none absolute left-4 top-4 z-[500]">
            <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-app-border bg-[color-mix(in_srgb,var(--background-soft)_78%,var(--surface)_22%)] px-4 py-3 shadow-soft">
              <strong className="text-[0.95rem] text-app-text">Cobertura territorial</strong>
              <span className="text-[0.84rem] text-app-text-muted">
                Solo operativos vigentes con dirección confirmada
              </span>
            </div>
          </div>
          {points.length ? (
            <LeafletMap points={points} />
          ) : (
            <div className="feedback-panel">
              Aún no hay operativos con coordenadas confirmadas para mostrarlos sobre el mapa.
            </div>
          )}
        </section>
      </div>
    </PageShell>
  );
}
