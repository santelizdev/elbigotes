import { apiRequest } from "@/lib/services/api-client";

export interface ClaimRequestPayload {
  claimer_name: string;
  organization_name?: string;
  email: string;
  phone?: string;
  relationship_to_place: string;
  message?: string;
  evidence_url?: string;
}

export interface ClaimRequestResponse {
  id: string;
  place_name: string;
  place_slug: string;
  status: string;
  claimer_name: string;
  organization_name?: string;
  email: string;
  phone?: string;
  relationship_to_place: string;
  message?: string;
  evidence_url?: string;
  created_at: string;
}

export async function createClaimRequest(
  placeSlug: string,
  payload: ClaimRequestPayload,
): Promise<ClaimRequestResponse> {
  return apiRequest(`/claims/places/${placeSlug}/requests/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
