import { apiRequest } from "@/lib/services/api-client";

export interface RegistrationCatalogItem {
  value: string;
  label: string;
}

export interface BusinessRegistrationPayload {
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
  business_name: string;
  business_kind: string;
  phone: string;
  commune: string;
  region?: string;
  website?: string;
  place_label: string;
  latitude: number;
  longitude: number;
  marketing_opt_in?: boolean;
  notes?: string;
}

export interface PetOwnerRegistrationPayload {
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
  phone: string;
  address_line?: string;
  commune?: string;
  region?: string;
  marketing_opt_in?: boolean;
  pet: {
    name: string;
    species: string;
    breed?: string;
    sex?: string;
    birth_date?: string;
  };
}

interface UserSummary {
  id: number;
  email: string;
  email_verified: boolean;
  first_name: string;
  last_name: string;
  role: string;
}

interface MembershipAssignmentSummary {
  id: number;
  plan_name: string;
  plan_slug: string;
  audience: string;
  status: string;
  starts_at: string;
  ends_at?: string | null;
  renews_at?: string | null;
  access_tier?: string;
  is_current?: boolean;
  renewal_required?: boolean;
}

export interface AccountLoginPayload {
  email: string;
  password: string;
}

export interface AccountLoginResponse {
  token: string;
  user: UserSummary;
}

export interface BusinessOwnedPlace {
  name: string;
  slug: string;
  status: string;
  formatted_address: string;
  commune: string;
  region: string;
  website?: string;
  latitude: number | null;
  longitude: number | null;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface BusinessRegistrationResponse {
  user: UserSummary;
  profile: {
    place_slug?: string | null;
    business_name: string;
    business_kind: string;
    phone: string;
    commune: string;
    region: string;
    website?: string;
    marketing_opt_in: boolean;
    notes?: string;
    memberships: MembershipAssignmentSummary[];
  };
}

export interface BusinessWorkspaceResponse {
  user: UserSummary;
  profile: BusinessRegistrationResponse["profile"];
  places: BusinessOwnedPlace[];
}

export interface BusinessWorkspaceUpdatePayload {
  first_name: string;
  last_name?: string;
  business_name: string;
  phone: string;
  commune: string;
  region: string;
  website?: string;
  marketing_opt_in?: boolean;
  notes?: string;
}

export interface BusinessBranchCreatePayload {
  branch_name: string;
  phone?: string;
  commune: string;
  region: string;
  website?: string;
  place_label: string;
  latitude: number;
  longitude: number;
  notes?: string;
}

export interface PetOwnerRegistrationResponse {
  user: UserSummary;
  profile: {
    phone: string;
    address_line?: string;
    commune: string;
    region: string;
    marketing_opt_in: boolean;
    memberships: MembershipAssignmentSummary[];
    pets: Array<{
      id: string;
      name: string;
      species: string;
      breed?: string;
      sex: string;
      birth_date?: string | null;
      notes?: string;
      is_active: boolean;
    }>;
  };
  initial_pet: {
    id: string;
    name: string;
    species: string;
    breed?: string;
    sex: string;
    birth_date?: string | null;
    notes?: string;
    is_active: boolean;
  };
}

export interface PetOwnerWorkspaceResponse {
  user: UserSummary;
  profile: PetOwnerRegistrationResponse["profile"];
  reports: Array<{
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
    photo_url?: string | null;
    is_reward_offered: boolean;
    reward_amount?: number | null;
    moderation_status: string;
    created_at: string;
  }>;
}

export async function getRegistrationCatalog(): Promise<{
  business_kinds: RegistrationCatalogItem[];
}> {
  return apiRequest("/accounts/catalog/", {
    cache: "no-store",
  });
}

export async function registerBusinessAccount(
  payload: BusinessRegistrationPayload,
): Promise<BusinessRegistrationResponse> {
  return apiRequest("/accounts/register/business/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function registerPetOwnerAccount(
  payload: PetOwnerRegistrationPayload,
): Promise<PetOwnerRegistrationResponse> {
  return apiRequest("/accounts/register/pet-owner/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function buildAuthHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem("elbigotes-access-token");
}

export function setStoredAccessToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem("elbigotes-access-token", token);
}

export function clearStoredAccessToken() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem("elbigotes-access-token");
}

export async function loginAccount(payload: AccountLoginPayload): Promise<AccountLoginResponse> {
  return apiRequest("/accounts/login/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getBusinessWorkspace(token: string): Promise<BusinessWorkspaceResponse> {
  return apiRequest("/accounts/me/business/", {
    headers: buildAuthHeaders(token),
    cache: "no-store",
  });
}

export async function getPetOwnerWorkspace(token: string): Promise<PetOwnerWorkspaceResponse> {
  return apiRequest("/accounts/me/pet-owner/", {
    headers: buildAuthHeaders(token),
    cache: "no-store",
  });
}

export async function updateBusinessWorkspace(
  token: string,
  payload: BusinessWorkspaceUpdatePayload,
): Promise<BusinessWorkspaceResponse> {
  return apiRequest("/accounts/me/business/", {
    method: "PATCH",
    headers: buildAuthHeaders(token),
    body: JSON.stringify(payload),
  });
}

export async function createBusinessBranch(
  token: string,
  payload: BusinessBranchCreatePayload,
): Promise<BusinessOwnedPlace> {
  return apiRequest("/accounts/me/business/branches/", {
    method: "POST",
    headers: buildAuthHeaders(token),
    body: JSON.stringify(payload),
  });
}
