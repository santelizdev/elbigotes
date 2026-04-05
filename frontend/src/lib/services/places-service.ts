import { mockPlaces } from "@/lib/mocks/places";
import { Place, PlaceFilters } from "@/lib/types";
import { ApiRequestError, apiRequest } from "@/lib/services/api-client";
import { siteConfig } from "@/lib/constants/site";

interface ApiListResponse<T> {
  count?: number;
  results?: T[];
}

interface PlaceApiResponse {
  name: string;
  slug: string;
  summary: string;
  description?: string;
  category: string;
  subcategory?: string | null;
  formatted_address: string;
  commune: string;
  region: string;
  country: string;
  is_verified: boolean;
  is_featured: boolean;
  is_emergency_service: boolean;
  is_open_24_7: boolean;
  website?: string;
  latitude: number;
  longitude: number;
  distance_km?: number | null;
  contact_points: Array<{
    label: string;
    kind: string;
    value: string;
    notes?: string;
    is_primary: boolean;
  }>;
  metadata?: Record<string, unknown>;
  source?: string | null;
}

function mapPlace(payload: PlaceApiResponse): Place {
  return {
    name: payload.name,
    slug: payload.slug,
    summary: payload.summary,
    description: payload.description,
    category: payload.category,
    subcategory: payload.subcategory,
    formattedAddress: payload.formatted_address,
    commune: payload.commune,
    region: payload.region,
    country: payload.country,
    isVerified: payload.is_verified,
    isFeatured: payload.is_featured,
    isEmergencyService: payload.is_emergency_service,
    isOpen247: payload.is_open_24_7,
    website: payload.website,
    latitude: payload.latitude,
    longitude: payload.longitude,
    distanceKm: payload.distance_km,
    contactPoints: payload.contact_points.map((contact) => ({
      label: contact.label,
      kind: contact.kind,
      value: contact.value,
      notes: contact.notes,
      isPrimary: contact.is_primary,
    })),
    metadata: payload.metadata,
    source: payload.source,
  };
}

function distanceKmBetween(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number,
) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const earthRadiusKm = 6371;
  const deltaLat = toRadians(lat2 - lat1);
  const deltaLng = toRadians(lng2 - lng1);
  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(deltaLng / 2) *
      Math.sin(deltaLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadiusKm * c;
}

function filterMockPlaces(filters?: PlaceFilters) {
  return mockPlaces.filter((place) => {
    if (filters?.category && place.category !== filters.category) {
      return false;
    }
    if (filters?.region && !place.region.toLowerCase().includes(filters.region.toLowerCase())) {
      return false;
    }
    if (filters?.commune && place.commune.toLowerCase() !== filters.commune.toLowerCase()) {
      return false;
    }
    if (filters?.search) {
      const term = filters.search.toLowerCase();
      const haystack = `${place.name} ${place.summary} ${place.formattedAddress}`.toLowerCase();
      if (!haystack.includes(term)) {
        return false;
      }
    }
    if (filters?.verifiedOnly && !place.isVerified) {
      return false;
    }
    if (filters?.isOpen247 && !place.isOpen247) {
      return false;
    }
    if (filters?.isEmergencyService && !place.isEmergencyService) {
      return false;
    }
    if (
      filters?.lat !== undefined &&
      filters?.lng !== undefined &&
      filters?.radiusKm !== undefined &&
      place.latitude !== null &&
      place.longitude !== null
    ) {
      const distance = distanceKmBetween(
        filters.lat,
        filters.lng,
        place.latitude,
        place.longitude,
      );
      if (distance > filters.radiusKm) {
        return false;
      }
    }
    return true;
  });
}

export async function getPlaces(filters?: PlaceFilters): Promise<Place[]> {
  try {
    const response = await apiRequest<ApiListResponse<PlaceApiResponse>>("/places/", {
      query: {
        category: filters?.category,
        search: filters?.search,
        region: filters?.region,
        commune: filters?.commune,
        lat: filters?.lat,
        lng: filters?.lng,
        radius_km: filters?.radiusKm,
        verified_only: filters?.verifiedOnly,
        is_open_24_7: filters?.isOpen247,
        is_emergency_service: filters?.isEmergencyService,
      },
      cache: "no-store",
    });

    const items = response.results ?? [];
    return items.map(mapPlace);
  } catch (error) {
    if (!siteConfig.useMocks) {
      throw error;
    }
    return filterMockPlaces(filters);
  }
}

export async function getPlaceBySlug(slug: string): Promise<Place | null> {
  try {
    const response = await apiRequest<PlaceApiResponse>(`/places/${slug}/`, {
      cache: "no-store",
    });
    return mapPlace(response);
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      return null;
    }
    if (!siteConfig.useMocks) {
      throw error;
    }
    return mockPlaces.find((place) => place.slug === slug) ?? null;
  }
}
