import { Metadata } from "next";

import styles from "@/components/accounts/registration.module.css";
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Opiniones del directorio</p>
        <h1 className="page-title">Reviews publicadas</h1>
        <p className="page-lead">
          Valoraciones moderadas de usuarios sobre veterinarias, guarderías, refugios, parques y
          otros servicios del ecosistema pet.
        </p>
      </section>

      <section className={styles.formCard}>
        <p className="eyebrow">Últimas reseñas</p>
        <h2>Comunidad</h2>
        <div className={styles.stackList}>
          {reviews.length ? (
            reviews.map((review) => (
              <article key={review.id} className={styles.listCard}>
                <div>
                  <strong>{review.title || `${review.place_name} · ${review.reviewer_name}`}</strong>
                  <p>{review.body}</p>
                  <p>
                    {review.place_name} · {review.reviewer_name}
                  </p>
                </div>
                <span className={styles.statusBox}>{renderStars(review.rating)}</span>
              </article>
            ))
          ) : (
            <div className="feedback-panel">
              Todavía no hay reviews publicadas. Cuando se moderen las primeras aparecerán aquí.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
