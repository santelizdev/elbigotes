import { LeafletMap } from "@/components/map/leaflet-map";
import { Button } from "@/components/ui/button";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Tag } from "@/components/ui/tag";
import { PublicPetOperation } from "@/lib/types";
import { formatTimestamp, titleCase } from "@/lib/utils/formatters";

export function PublicPetOperationProfile({ operation }: { operation: PublicPetOperation }) {
  const hasMapPoint =
    operation.latitude !== null &&
    operation.longitude !== null &&
    Number.isFinite(operation.latitude) &&
    Number.isFinite(operation.longitude);

  return (
    <PageShell className="gap-5 pb-8 pt-5">
      <PageHero
        eyebrow="Jornada confirmada"
        title={operation.title}
        description={
          operation.requirements ||
          `${operation.creatorName} organiza este operativo ${titleCase(operation.operationType)} en ${operation.commune}.`
        }
        className="border-[color-mix(in_srgb,var(--accent-coral)_18%,transparent)] bg-[radial-gradient(circle_at_top_right,color-mix(in_srgb,var(--accent-coral)_16%,transparent),transparent_28%),linear-gradient(180deg,color-mix(in_srgb,var(--background-soft)_96%,transparent),color-mix(in_srgb,var(--background)_98%,transparent))] p-6"
        actions={
          <div className="flex flex-wrap gap-2">
            <Tag tone="accent">{titleCase(operation.operationType)}</Tag>
            <Tag>{operation.creatorType === "public" ? "Organizador público" : "Organizador privado"}</Tag>
          </div>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
        <SurfaceCard className="grid gap-5 p-5">
          {operation.imageUrl ? (
            <div className="overflow-hidden rounded-[1.4rem] border border-app-border-strong">
              <img
                src={operation.imageUrl}
                alt={operation.title}
                className="block h-auto w-full object-cover"
              />
            </div>
          ) : null}

          <SectionHeader eyebrow="Información clave" title="Detalle del operativo" />

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Organiza</span>
              <span className="text-sm leading-6 text-app-text">{operation.creatorName}</span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Inicio</span>
              <span className="text-sm leading-6 text-app-text">{formatTimestamp(operation.startsAt)}</span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Ubicación</span>
              <span className="text-sm leading-6 text-app-text">{operation.address}</span>
            </div>
            <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_92%,transparent)] p-4">
              <span className="text-[0.78rem] uppercase tracking-[0.16em] text-app-text-muted">Cobertura</span>
              <span className="text-sm leading-6 text-app-text">
                {operation.commune}, {operation.region}
              </span>
            </div>
          </div>

          {operation.requirements ? (
            <div className="grid gap-2">
              <SectionHeader title="Requisitos" compact />
              <p className="m-0 text-sm leading-7 text-app-text-soft">{operation.requirements}</p>
            </div>
          ) : null}

          <div className="flex flex-wrap gap-3">
            <Button href="/jornadas-operativos" variant="ghost">
              Volver al listado
            </Button>
          </div>
        </SurfaceCard>

        <SurfaceCard className="grid gap-5 p-5">
          <SectionHeader eyebrow="Mapa local" title="Ubicación confirmada" />
          <div className="min-h-[360px] overflow-hidden rounded-[1.4rem] border border-app-border-strong">
            {hasMapPoint ? (
              <LeafletMap
                points={[
                  {
                    id: operation.slug,
                    latitude: operation.latitude as number,
                    longitude: operation.longitude as number,
                    title: operation.title,
                    subtitle: operation.address,
                    accent: "var(--accent-coral)",
                  },
                ]}
                focusedPointId={operation.slug}
              />
            ) : (
              <div className="feedback-panel">
                Este operativo todavía no tiene coordenadas confirmadas para mostrarse en el mapa.
              </div>
            )}
          </div>
        </SurfaceCard>
      </div>
    </PageShell>
  );
}
