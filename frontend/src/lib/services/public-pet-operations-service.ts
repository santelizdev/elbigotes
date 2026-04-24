import { PublicPetOperation } from "@/lib/types";
import { ApiRequestError, apiRequest } from "@/lib/services/api-client";
import { siteConfig } from "@/lib/constants/site";

interface ApiListResponse<T> {
  count?: number;
  results?: T[];
}

interface PublicPetOperationApiResponse {
  title: string;
  slug: string;
  operation_type: string;
  creator_type: string;
  creator_name: string;
  address: string;
  commune: string;
  region: string;
  latitude: number | null;
  longitude: number | null;
  starts_at: string;
  ends_at?: string | null;
  requirements?: string;
  image_url?: string | null;
  status: string;
  is_expired: boolean;
  is_publicly_visible: boolean;
  created_at: string;
  updated_at: string;
}

function mapPublicPetOperation(payload: PublicPetOperationApiResponse): PublicPetOperation {
  return {
    title: payload.title,
    slug: payload.slug,
    operationType: payload.operation_type,
    creatorType: payload.creator_type,
    creatorName: payload.creator_name,
    address: payload.address,
    commune: payload.commune,
    region: payload.region,
    latitude: payload.latitude,
    longitude: payload.longitude,
    startsAt: payload.starts_at,
    endsAt: payload.ends_at,
    requirements: payload.requirements,
    imageUrl: payload.image_url,
    status: payload.status,
    isExpired: payload.is_expired,
    isPubliclyVisible: payload.is_publicly_visible,
    createdAt: payload.created_at,
    updatedAt: payload.updated_at,
  };
}

export async function getPublicPetOperations(): Promise<PublicPetOperation[]> {
  try {
    const response = await apiRequest<ApiListResponse<PublicPetOperationApiResponse>>(
      "/places/public-operations/",
      {
        cache: "no-store",
      },
    );
    return (response.results ?? []).map(mapPublicPetOperation);
  } catch (error) {
    if (!siteConfig.useMocks) {
      throw error;
    }
    return [];
  }
}

export async function getPublicPetOperationBySlug(slug: string): Promise<PublicPetOperation | null> {
  try {
    const response = await apiRequest<PublicPetOperationApiResponse>(
      `/places/public-operations/${slug}/`,
      {
        cache: "no-store",
      },
    );
    return mapPublicPetOperation(response);
  } catch (error) {
    if (error instanceof ApiRequestError && error.status === 404) {
      return null;
    }
    if (!siteConfig.useMocks) {
      throw error;
    }
    return null;
  }
}
