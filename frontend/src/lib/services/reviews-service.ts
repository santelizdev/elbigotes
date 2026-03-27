import { apiRequest } from "@/lib/services/api-client";

interface ApiListResponse<T> {
  count?: number;
  results?: T[];
}

export interface PlaceReview {
  id: number;
  place_name: string;
  place_slug: string;
  reviewer_name: string;
  rating: number;
  title?: string;
  body: string;
  is_verified_visit: boolean;
  published_at?: string | null;
  created_at: string;
}

export interface CreatePlaceReviewPayload {
  place_slug: string;
  reviewer_name: string;
  reviewer_email: string;
  rating: number;
  title?: string;
  body: string;
  is_verified_visit?: boolean;
}

export async function getPublishedReviews(placeSlug?: string): Promise<PlaceReview[]> {
  const response = await apiRequest<ApiListResponse<PlaceReview>>("/reviews/", {
    query: {
      place: placeSlug,
    },
    cache: "no-store",
  });

  return response.results ?? [];
}

export async function createPlaceReview(
  payload: CreatePlaceReviewPayload,
): Promise<PlaceReview> {
  return apiRequest("/reviews/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
