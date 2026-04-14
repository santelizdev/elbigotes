import { getStoredAccessToken } from "@/lib/services/accounts-service";
import { apiRequest } from "@/lib/services/api-client";

function buildTrackingHeaders() {
  const token = getStoredAccessToken();
  if (!token) {
    return undefined;
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

export interface SearchTrackingPayload {
  category_slug?: string;
  search_term?: string;
  region?: string;
  commune?: string;
  has_user_location?: boolean;
  user_latitude?: number;
  user_longitude?: number;
  radius_km?: number | null;
  verified_only?: boolean;
  result_count?: number;
  path?: string;
}

export interface PlaceViewTrackingPayload {
  place_slug: string;
  path?: string;
}

export async function trackSearchEvent(payload: SearchTrackingPayload) {
  try {
    await apiRequest("/analytics/events/searches/", {
      method: "POST",
      headers: buildTrackingHeaders(),
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error("[analytics] search tracking failed", error);
  }
}

export async function trackPlaceViewEvent(payload: PlaceViewTrackingPayload) {
  try {
    await apiRequest("/analytics/events/place-views/", {
      method: "POST",
      headers: buildTrackingHeaders(),
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error("[analytics] place view tracking failed", error);
  }
}
