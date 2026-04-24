import { Button } from "@/components/ui/button";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Tag } from "@/components/ui/tag";
import { PublicPetOperation } from "@/lib/types";
import { formatTimestamp, titleCase } from "@/lib/utils/formatters";

export function PublicPetOperationCard({ operation }: { operation: PublicPetOperation }) {
  return (
    <SurfaceCard className="grid gap-4 p-5">
      <div className="flex flex-col gap-3">
        <div className="inline-tags">
          <Tag tone="accent">{titleCase(operation.operationType)}</Tag>
          <Tag>{operation.creatorType === "public" ? "Organizador público" : "Organizador privado"}</Tag>
        </div>
        <div className="grid gap-1">
          <h3 className="m-0 text-[1.18rem] leading-[1.1] text-app-text">{operation.title}</h3>
          <p className="m-0 text-sm leading-6 text-app-text-soft">
            {operation.creatorName} · {operation.commune}, {operation.region}
          </p>
        </div>
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <dt className="text-[0.78rem] font-semibold uppercase tracking-[0.16em] text-app-text-muted">
            Dirección
          </dt>
          <dd className="m-0 text-sm leading-6 text-app-text">{operation.address}</dd>
        </div>
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <dt className="text-[0.78rem] font-semibold uppercase tracking-[0.16em] text-app-text-muted">
            Inicio
          </dt>
          <dd className="m-0 text-sm leading-6 text-app-text">{formatTimestamp(operation.startsAt)}</dd>
        </div>
      </dl>

      {operation.requirements ? (
        <p className="m-0 text-sm leading-7 text-app-text-soft">{operation.requirements}</p>
      ) : null}

      <div className="flex flex-wrap gap-3">
        <Button href={`/jornadas-operativos/${operation.slug}`} variant="secondary">
          Ver ficha
        </Button>
      </div>
    </SurfaceCard>
  );
}
