import { getLostPetReports } from "@/lib/services/lost-pets-service";
import { getPlaceBySlug, getPlaces } from "@/lib/services/places-service";
import { LostPetReport, Place, PlaceFilters } from "@/lib/types";

export async function loadHomePageData(): Promise<{
  places: Place[];
  lostPets: LostPetReport[];
  hasError: boolean;
}> {
  const [placesResult, lostPetsResult] = await Promise.allSettled([getPlaces(), getLostPetReports()]);

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
  } catch {
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
  } catch {
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
  } catch {
    return { place: null, hasError: true };
  }
}
