import { StatusPill } from "@/components/ui/status-pill";
import { SurfaceCard } from "@/components/ui/surface-card";
import { Tag } from "@/components/ui/tag";
import { LostPetReport } from "@/lib/types";
import { formatTimestamp, titleCase } from "@/lib/utils/formatters";

export function LostPetReportCard({ report }: { report: LostPetReport }) {
  return (
    <SurfaceCard className="grid gap-4 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="eyebrow">{titleCase(report.species)}</p>
          <h3 className="m-[0.2rem_0_0] text-[1.18rem] leading-[1.05]">{report.petName}</h3>
        </div>
        <StatusPill
          label={report.status === "lost" ? "Perdida" : titleCase(report.status)}
          tone={report.status === "lost" ? "critical" : "warning"}
        />
      </div>

      <p className="m-0 text-sm leading-7 text-app-text-soft">{report.colorDescription}</p>

      <div className="inline-tags">
        {report.breed ? <Tag>{report.breed}</Tag> : null}
        {report.isRewardOffered ? <Tag tone="warning">Recompensa</Tag> : null}
      </div>

      <dl className="grid gap-3 sm:grid-cols-2">
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <dt className="text-[0.78rem] font-semibold uppercase tracking-[0.16em] text-app-text-muted">
            Última ubicación
          </dt>
          <dd className="m-0 text-sm leading-6 text-app-text">{report.lastSeenAddress}</dd>
        </div>
        <div className="grid gap-1 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4">
          <dt className="text-[0.78rem] font-semibold uppercase tracking-[0.16em] text-app-text-muted">
            Último avistamiento
          </dt>
          <dd className="m-0 text-sm leading-6 text-app-text">{formatTimestamp(report.lastSeenAt)}</dd>
        </div>
      </dl>
    </SurfaceCard>
  );
}
