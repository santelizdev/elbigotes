import { mockLostPetReports } from "@/lib/mocks/places";
import { LostPetReport } from "@/lib/types";
import { apiRequest } from "@/lib/services/api-client";
import { siteConfig } from "@/lib/constants/site";

interface ApiListResponse<T> {
  count?: number;
  results?: T[];
}

interface LostPetReportApiResponse {
  id: string;
  pet_name: string;
  species: string;
  breed?: string;
  sex: string;
  color_description: string;
  distinctive_marks?: string;
  status: string;
  last_seen_at: string;
  last_seen_address: string;
  last_seen_reference?: string;
  latitude: number | null;
  longitude: number | null;
  photo_url?: string;
  is_reward_offered: boolean;
  reward_amount?: number | null;
  created_at: string;
}

function mapLostPetReport(payload: LostPetReportApiResponse): LostPetReport {
  return {
    id: payload.id,
    petName: payload.pet_name,
    species: payload.species,
    breed: payload.breed,
    sex: payload.sex,
    colorDescription: payload.color_description,
    distinctiveMarks: payload.distinctive_marks,
    status: payload.status,
    lastSeenAt: payload.last_seen_at,
    lastSeenAddress: payload.last_seen_address,
    lastSeenReference: payload.last_seen_reference,
    latitude: payload.latitude,
    longitude: payload.longitude,
    photoUrl: payload.photo_url,
    isRewardOffered: payload.is_reward_offered,
    rewardAmount: payload.reward_amount,
    createdAt: payload.created_at,
  };
}

function buildFallbackLostPetReport(
  payload: FormData,
  response?: Partial<LostPetReportApiResponse> | null,
): LostPetReport {
  const latitude = Number(payload.get("last_seen_latitude"));
  const longitude = Number(payload.get("last_seen_longitude"));
  const breedFromPayload = String(payload.get("breed") ?? "") || undefined;
  const lastSeenReferenceFromPayload =
    String(payload.get("last_seen_reference") ?? "") || undefined;

  return {
    id: response?.id ?? crypto.randomUUID(),
    petName: response?.pet_name ?? String(payload.get("pet_name") ?? ""),
    species: response?.species ?? String(payload.get("species") ?? ""),
    breed: response?.breed ?? breedFromPayload,
    sex: response?.sex ?? String(payload.get("sex") ?? "unknown"),
    colorDescription:
      response?.color_description ?? String(payload.get("color_description") ?? ""),
    distinctiveMarks: response?.distinctive_marks ?? undefined,
    status: response?.status ?? String(payload.get("status") ?? "lost"),
    lastSeenAt: response?.last_seen_at ?? String(payload.get("last_seen_at") ?? ""),
    lastSeenAddress:
      response?.last_seen_address ?? String(payload.get("last_seen_address") ?? ""),
    lastSeenReference: response?.last_seen_reference ?? lastSeenReferenceFromPayload,
    latitude: Number.isFinite(latitude) ? latitude : null,
    longitude: Number.isFinite(longitude) ? longitude : null,
    photoUrl: response?.photo_url ?? undefined,
    isRewardOffered:
      response?.is_reward_offered ?? payload.get("is_reward_offered") === "true",
    rewardAmount:
      response?.reward_amount ??
      (payload.get("reward_amount") ? Number(payload.get("reward_amount")) : null),
    createdAt: response?.created_at ?? new Date().toISOString(),
  };
}

export async function getLostPetReports(): Promise<LostPetReport[]> {
  try {
    const response = await apiRequest<ApiListResponse<LostPetReportApiResponse>>(
      "/lost-pets/reports/",
      {
        cache: "no-store",
      },
    );
    return (response.results ?? []).map(mapLostPetReport);
  } catch (error) {
    if (!siteConfig.useMocks) {
      throw error;
    }
    return mockLostPetReports;
  }
}

export async function createLostPetReport(payload: FormData): Promise<LostPetReport> {
  try {
    const response = await apiRequest<LostPetReportApiResponse | null>("/lost-pets/reports/", {
      method: "POST",
      body: payload,
    });

    if (response && typeof response === "object" && "id" in response && "pet_name" in response) {
      return mapLostPetReport(response);
    }

    return buildFallbackLostPetReport(payload, response);
  } catch (error) {
    if (!siteConfig.useMocks) {
      throw error;
    }
    return buildFallbackLostPetReport(payload);
  }
}
