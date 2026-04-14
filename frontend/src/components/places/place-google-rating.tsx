import Image from "next/image";

import styles from "@/components/places/place-google-rating.module.css";

interface PlaceGoogleRatingProps {
  rating?: number | null;
  reviewsCount?: number | null;
  compact?: boolean;
}

function StarIcon({ filled, compact = false }: { filled: boolean; compact?: boolean }) {
  return (
    <svg
      viewBox="0 0 20 20"
      aria-hidden="true"
      className={[styles.star, compact ? styles.starCompact : ""].filter(Boolean).join(" ")}
    >
      <path
        d="M10 2.2l2.38 4.82 5.32.77-3.85 3.75.91 5.29L10 14.34l-4.76 2.49.91-5.29L2.3 7.79l5.32-.77L10 2.2Z"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function PlaceGoogleRating({
  rating = null,
  reviewsCount = 0,
  compact = false,
}: PlaceGoogleRatingProps) {
  if (rating === null || rating === undefined || Number.isNaN(rating)) {
    return null;
  }

  const normalizedReviewsCount = Math.max(0, Number(reviewsCount) || 0);
  const filledStars = Math.max(0, Math.min(5, Math.round(rating)));

  return (
    <div
      className={[styles.rating, compact ? styles.ratingCompact : ""].filter(Boolean).join(" ")}
      aria-label={`Rating Google ${rating.toFixed(1)} de 5 con ${normalizedReviewsCount} reseñas`}
    >
      <span className={styles.logoWrap} aria-hidden="true">
        <Image
          src="/googlereviews.svg"
          alt=""
          width={90}
          height={32}
          className={[styles.logo, compact ? styles.logoCompact : ""].filter(Boolean).join(" ")}
        />
      </span>
      <span className={[styles.score, compact ? styles.scoreCompact : ""].filter(Boolean).join(" ")}>
        {rating.toFixed(1)}
      </span>
      <span className={styles.stars}>
        {Array.from({ length: 5 }, (_, index) => (
          <StarIcon key={index} filled={index < filledStars} compact={compact} />
        ))}
      </span>
      <span
        className={[styles.reviews, compact ? styles.reviewsCompact : ""].filter(Boolean).join(" ")}
      >
        ({normalizedReviewsCount.toLocaleString("es-CL")})
      </span>
    </div>
  );
}
