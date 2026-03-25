import { StatusPill } from "@/components/ui/status-pill";
import { Tag } from "@/components/ui/tag";
import { LostPetReport } from "@/lib/types";
import { formatTimestamp, titleCase } from "@/lib/utils/formatters";

export function LostPetReportCard({ report }: { report: LostPetReport }) {
  return (
    <article className="report-card">
      <div className="report-card__header">
        <div>
          <p className="eyebrow">{titleCase(report.species)}</p>
          <h3>{report.petName}</h3>
        </div>
        <StatusPill
          label={report.status === "lost" ? "Perdida" : titleCase(report.status)}
          tone={report.status === "lost" ? "critical" : "warning"}
        />
      </div>

      <p className="report-card__summary">{report.colorDescription}</p>

      <div className="inline-tags">
        {report.breed ? <Tag>{report.breed}</Tag> : null}
        {report.isRewardOffered ? <Tag tone="warning">Recompensa</Tag> : null}
      </div>

      <dl className="report-card__meta">
        <div>
          <dt>Última ubicación</dt>
          <dd>{report.lastSeenAddress}</dd>
        </div>
        <div>
          <dt>Último avistamiento</dt>
          <dd>{formatTimestamp(report.lastSeenAt)}</dd>
        </div>
      </dl>
    </article>
  );
}

