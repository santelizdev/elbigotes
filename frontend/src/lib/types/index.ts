export type CategorySlug = string;

export interface ContactPoint {
  label: string;
  kind: string;
  value: string;
  notes?: string;
  isPrimary: boolean;
}

export interface Place {
  name: string;
  slug: string;
  summary: string;
  description?: string;
  category: string;
  subcategory?: string | null;
  formattedAddress: string;
  commune: string;
  region: string;
  country: string;
  isVerified: boolean;
  isFeatured: boolean;
  isEmergencyService: boolean;
  isOpen247: boolean;
  website?: string;
  latitude: number | null;
  longitude: number | null;
  distanceKm?: number | null;
  contactPoints: ContactPoint[];
  metadata?: Record<string, unknown>;
  source?: string | null;
}

export interface LostPetReport {
  id: string;
  petName: string;
  species: string;
  breed?: string;
  sex: string;
  colorDescription: string;
  distinctiveMarks?: string;
  status: string;
  lastSeenAt: string;
  lastSeenAddress: string;
  lastSeenReference?: string;
  latitude: number | null;
  longitude: number | null;
  photoUrl?: string;
  isRewardOffered: boolean;
  rewardAmount?: number | null;
  createdAt: string;
}

export interface PlaceFilters {
  category?: string;
  search?: string;
  region?: string;
  commune?: string;
  lat?: number;
  lng?: number;
  radiusKm?: number;
  verifiedOnly?: boolean;
  isOpen247?: boolean;
  isEmergencyService?: boolean;
}
