import Image from "next/image";

import { cn } from "@/lib/utils/cn";

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
      className={cn(
        "h-[0.95rem] w-[0.95rem]",
        compact && "h-[0.82rem] w-[0.82rem]",
      )}
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
      className={cn(
        "inline-flex flex-wrap items-center gap-[0.55rem] text-app-text-soft",
        compact && "gap-[0.35rem]",
      )}
      aria-label={`Rating Google ${rating.toFixed(1)} de 5 con ${normalizedReviewsCount} reseñas`}
    >
      <span className="inline-flex items-center justify-center pr-[0.15rem]" aria-hidden="true">
        <Image
          src="/googlereviews.svg"
          alt=""
          width={90}
          height={32}
          className={cn(
            "h-[1.1rem] w-auto object-contain",
            compact && "h-[0.95rem]",
          )}
        />
      </span>
      <span className={cn("text-base font-bold text-app-text", compact && "text-[0.95rem]")}>
        {rating.toFixed(1)}
      </span>
      <span className="inline-flex items-center gap-[0.12rem] text-[#f5b942]">
        {Array.from({ length: 5 }, (_, index) => (
          <StarIcon key={index} filled={index < filledStars} compact={compact} />
        ))}
      </span>
      <span className={cn("text-[0.94rem] text-app-text-muted", compact && "text-[0.84rem]")}>
        ({normalizedReviewsCount.toLocaleString("es-CL")})
      </span>
    </div>
  );
}
