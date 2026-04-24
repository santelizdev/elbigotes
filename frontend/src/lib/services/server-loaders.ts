import { ApiRequestError } from "@/lib/services/api-client";
import { getLostPetReports } from "@/lib/services/lost-pets-service";
import { getPlaceBySlug, getPlaces } from "@/lib/services/places-service";
import { getPublicPetOperationBySlug, getPublicPetOperations } from "@/lib/services/public-pet-operations-service";
import { LostPetReport, Place, PlaceFilters, PublicPetOperation } from "@/lib/types";

function logLoaderFailure(scope: string, error: unknown) {
  if (error instanceof ApiRequestError) {
    console.error(`[${scope}] API request failed`, {
      status: error.status,
      details: error.details,
      message: error.message,
    });
    return;
  }

  if (error instanceof Error) {
    console.error(`[${scope}] Unexpected error`, {
      name: error.name,
      message: error.message,
      stack: error.stack,
    });
    return;
  }

  console.error(`[${scope}] Unknown error`, error);
}

function isDynamicServerUsageError(error: unknown) {
  return error instanceof Error && error.message.includes("Dynamic server usage:");
}

export async function loadHomePageData(): Promise<{
  places: Place[];
  lostPets: LostPetReport[];
  hasError: boolean;
}> {
  const [placesResult, lostPetsResult] = await Promise.allSettled([getPlaces(), getLostPetReports()]);

  if (placesResult.status === "rejected" && isDynamicServerUsageError(placesResult.reason)) {
    throw placesResult.reason;
  }

  if (lostPetsResult.status === "rejected" && isDynamicServerUsageError(lostPetsResult.reason)) {
    throw lostPetsResult.reason;
  }

  if (placesResult.status === "rejected") {
    logLoaderFailure("home:places", placesResult.reason);
  }

  if (lostPetsResult.status === "rejected") {
    logLoaderFailure("home:lost-pets", lostPetsResult.reason);
  }

  return {
    places: placesResult.status === "fulfilled" ? placesResult.value : [],
    lostPets: lostPetsResult.status === "fulfilled" ? lostPetsResult.value : [],
    // El home depende críticamente del catálogo de lugares; el contador de mascotas perdidas
    // es complementario y puede degradarse a cero sin ensuciar toda la portada.
    hasError: placesResult.status === "rejected",
  };
}

export async function loadLostPetsPageData(): Promise<{
  lostPets: LostPetReport[];
  hasError: boolean;
}> {
  try {
    const lostPets = await getLostPetReports();
    return { lostPets, hasError: false };
  } catch (error) {
    if (isDynamicServerUsageError(error)) {
      throw error;
    }
    logLoaderFailure("lost-pets:index", error);
    return { lostPets: [], hasError: true };
  }
}

export async function loadPlacesPageData(filters: PlaceFilters): Promise<{
  places: Place[];
  hasError: boolean;
}> {
  try {
    const places = await getPlaces(filters);
    return { places, hasError: false };
  } catch (error) {
    if (isDynamicServerUsageError(error)) {
      throw error;
    }
    logLoaderFailure("places:index", error);
    return { places: [], hasError: true };
  }
}

export async function loadPlaceDetailData(slug: string): Promise<{
  place: Place | null;
  hasError: boolean;
}> {
  try {
    const place = await getPlaceBySlug(slug);
    return { place, hasError: false };
  } catch (error) {
    if (isDynamicServerUsageError(error)) {
      throw error;
    }
    logLoaderFailure(`places:detail:${slug}`, error);
    return { place: null, hasError: true };
  }
}

export async function loadPublicPetOperationsPageData(): Promise<{
  operations: PublicPetOperation[];
  hasError: boolean;
}> {
  try {
    const operations = await getPublicPetOperations();
    return { operations, hasError: false };
  } catch (error) {
    if (isDynamicServerUsageError(error)) {
      throw error;
    }
    logLoaderFailure("public-operations:index", error);
    return { operations: [], hasError: true };
  }
}

export async function loadPublicPetOperationDetailData(slug: string): Promise<{
  operation: PublicPetOperation | null;
  hasError: boolean;
}> {
  try {
    const operation = await getPublicPetOperationBySlug(slug);
    return { operation, hasError: false };
  } catch (error) {
    if (isDynamicServerUsageError(error)) {
      throw error;
    }
    logLoaderFailure(`public-operations:detail:${slug}`, error);
    return { operation: null, hasError: true };
  }
}
