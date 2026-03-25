"use client";

import { LeafletMap } from "@/components/map/leaflet-map";
import { Button } from "@/components/ui/button";
import { LostPetReportCard } from "@/components/lost-pets/lost-pet-report-card";
import styles from "@/components/explorer/map-explorer.module.css";
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroTop}>
          <div>
            <p className="eyebrow">Utilidad social</p>
            <h1 className={styles.heroTitle}>Mascotas perdidas sobre el mapa</h1>
            <p className={styles.heroLead}>
              Reunimos reportes activos con última ubicación conocida para que la búsqueda empiece
              desde el territorio y no desde un muro de avisos dispersos.
            </p>
          </div>

          <Button href="/publicar-mascota-perdida" variant="primary">
            Publicar reporte
          </Button>
        </div>
      </section>

      <div className={styles.workspace}>
        <aside className={styles.sidebar}>
          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <div>
                <p className="eyebrow">Reportes activos</p>
                <h2 className={styles.panelTitle}>Últimos avisos</h2>
              </div>
              <span className={styles.panelCaption}>{reports.length} reportes</span>
            </div>

            <div className="stack-lg">
              {reports.map((report) => (
                <LostPetReportCard key={report.id} report={report} />
              ))}
            </div>
          </section>
        </aside>

        <section className={styles.mapPanel}>
          <div className={styles.mapOverlay}>
            <div className={styles.mapChip}>
              <strong>Búsqueda territorial</strong>
              <span className={styles.mapHint}>Prioriza radio cercano y última referencia conocida</span>
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
    </div>
  );
}
