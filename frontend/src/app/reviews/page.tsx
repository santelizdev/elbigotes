import { Metadata } from "next";

import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";
import { getPublishedReviews } from "@/lib/services/reviews-service";

export const metadata: Metadata = {
  title: "Reviews | Elbigotes",
  description: "Opiniones publicadas por usuarios sobre fichas activas del ecosistema pet.",
};

function renderStars(rating: number) {
  return "★".repeat(rating) + "☆".repeat(Math.max(0, 5 - rating));
}

export default async function ReviewsPage() {
  const reviews = await getPublishedReviews();

  return (
    <PageShell>
      <PageHero
        eyebrow="Opiniones del directorio"
        title="Reviews publicadas"
        description="Valoraciones moderadas de usuarios sobre veterinarias, guarderías, refugios, parques y otros servicios del ecosistema pet."
      />

      <SurfaceCard className="grid gap-5">
        <SectionHeader eyebrow="Últimas reseñas" title="Comunidad" />
        <div className="grid gap-3">
          {reviews.length ? (
            reviews.map((review) => (
              <article
                key={review.id}
                className="flex flex-col gap-4 rounded-2xl border border-app-border bg-[color-mix(in_srgb,var(--surface-raised)_88%,transparent)] p-4 sm:flex-row sm:items-start sm:justify-between"
              >
                <div className="grid gap-2">
                  <strong>{review.title || `${review.place_name} · ${review.reviewer_name}`}</strong>
                  <p className="m-0 text-sm leading-7 text-app-text-soft">{review.body}</p>
                  <p className="m-0 text-sm text-app-text-muted">
                    {review.place_name} · {review.reviewer_name}
                  </p>
                </div>
                <span className="inline-flex rounded-2xl border border-[color-mix(in_srgb,var(--accent-emerald)_18%,transparent)] bg-[color-mix(in_srgb,var(--accent-emerald)_12%,transparent)] px-4 py-3 text-app-text-soft">
                  {renderStars(review.rating)}
                </span>
              </article>
            ))
          ) : (
            <div className="feedback-panel">
              Todavía no hay reviews publicadas. Cuando se moderen las primeras aparecerán aquí.
            </div>
          )}
        </div>
      </SurfaceCard>
    </PageShell>
  );
}
