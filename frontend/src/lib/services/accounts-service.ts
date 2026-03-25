import { apiRequest } from "@/lib/services/api-client";

export interface RegistrationCatalogItem {
  value: string;
  label: string;
  billing_mode?: string;
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
    membership_status: string;
    grace_expires_at?: string | null;
    marketing_opt_in: boolean;
    notes?: string;
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

export async function getRegistrationCatalog(): Promise<{
  business_kinds: RegistrationCatalogItem[];
  membership_status: RegistrationCatalogItem[];
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
