"use client";

import { startTransition, useDeferredValue, useEffect, useRef, useState } from "react";

import { trackSearchEvent } from "@/lib/services/analytics-service";
import { ApiRequestError, getApiErrorMessage } from "@/lib/services/api-client";
import { Place, PlaceFilters } from "@/lib/types";
import { getPlaces } from "@/lib/services/places-service";

interface UsePlacesQueryOptions {
  initialPlaces: Place[];
  initialCategory?: string;
}

type GeolocationPermissionState = PermissionState | "unsupported" | "unknown";

const GEOLOCATION_PERMISSION_DENIED = 1;
const GEOLOCATION_POSITION_UNAVAILABLE = 2;
const GEOLOCATION_TIMEOUT = 3;

function buildTerritoryOptions(values: string[]) {
  const counts = values.reduce<Map<string, number>>((map, value) => {
    const normalizedValue = value.trim();
    if (!normalizedValue) {
      return map;
    }

    map.set(normalizedValue, (map.get(normalizedValue) ?? 0) + 1);
    return map;
  }, new Map());

  return [...counts.entries()]
    .sort((left, right) => left[0].localeCompare(right[0], "es"))
    .map(([name, count]) => ({ name, count }));
}

function getGeolocationPermissionState(): Promise<GeolocationPermissionState> {
  if (typeof navigator === "undefined" || !("permissions" in navigator)) {
    return Promise.resolve("unsupported");
  }

  return navigator.permissions
    .query({ name: "geolocation" as PermissionName })
    .then((status) => status.state)
    .catch(() => "unknown");
}

function getCurrentPosition(
  options: PositionOptions,
): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, options);
  });
}

function isGeolocationError(error: unknown): error is Pick<GeolocationPositionError, "code"> {
  return typeof error === "object" && error !== null && "code" in error;
}

function getLocationErrorMessage(error: Pick<GeolocationPositionError, "code">) {
  switch (error.code) {
    case GEOLOCATION_PERMISSION_DENIED:
      return "Tu navegador o Safari tiene bloqueado el permiso de ubicación. Revísalo en Configuración del sitio o en Ajustes > Safari > Ubicación.";
    case GEOLOCATION_POSITION_UNAVAILABLE:
      return "No pudimos determinar tu ubicación exacta. Prueba moverte a un lugar con mejor señal o vuelve a intentarlo.";
    case GEOLOCATION_TIMEOUT:
      return "La ubicación tardó demasiado en responder. Intentaremos una versión menos precisa para no dejar el mapa bloqueado.";
    default:
      return "No pudimos obtener tu ubicación. Revisa los permisos del navegador e inténtalo otra vez.";
  }
}

async function requestUserPosition() {
  try {
    return await getCurrentPosition({
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000,
    });
  } catch (error) {
    if (
      isGeolocationError(error) &&
      error.code !== GEOLOCATION_PERMISSION_DENIED
    ) {
      return getCurrentPosition({
        enableHighAccuracy: false,
        timeout: 15000,
        maximumAge: 600000,
      });
    }

    throw error;
  }
}

export function usePlacesQuery({ initialPlaces, initialCategory }: UsePlacesQueryOptions) {
  const [places, setPlaces] = useState(initialPlaces);
  const [territoryPlaces, setTerritoryPlaces] = useState(initialPlaces);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory ?? "");
  const [search, setSearch] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("");
  const [selectedCommune, setSelectedCommune] = useState("");
  const [radiusKm, setRadiusKm] = useState<number | null>(null);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [showOnlyVerified, setShowOnlyVerified] = useState(false);
  const [showOnly247, setShowOnly247] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);
  const deferredSearch = useDeferredValue(search);
  const lastTrackedSearchKeyRef = useRef<string>("");

  useEffect(() => {
    let active = true;
    const normalizedSearch = deferredSearch.trim();
    const filters: PlaceFilters = {
      category: selectedCategory || undefined,
      search: normalizedSearch.length >= 2 ? normalizedSearch : undefined,
      region: selectedRegion || undefined,
      commune: selectedCommune || undefined,
      lat: radiusKm && userLocation ? userLocation.lat : undefined,
      lng: radiusKm && userLocation ? userLocation.lng : undefined,
      radiusKm: radiusKm && userLocation ? radiusKm : undefined,
      verifiedOnly: showOnlyVerified,
      isOpen247: showOnly247,
    };

    setLoading(true);
    setError(null);

    getPlaces(filters)
      .then((items) => {
        if (!active) {
          return;
        }
        setPlaces(items);
        if (typeof window !== "undefined") {
          const trackingPayload = {
            category_slug: filters.category,
            search_term: filters.search,
            region: filters.region,
            commune: filters.commune,
            has_user_location: Boolean(userLocation),
            user_latitude: userLocation?.lat,
            user_longitude: userLocation?.lng,
            radius_km: filters.radiusKm,
            verified_only: filters.verifiedOnly,
            result_count: items.length,
            path: `${window.location.pathname}${window.location.search}`,
          };
          const trackingKey = JSON.stringify(trackingPayload);

          if (lastTrackedSearchKeyRef.current !== trackingKey) {
            lastTrackedSearchKeyRef.current = trackingKey;
            void trackSearchEvent(trackingPayload);
          }
        }
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }

        if (error instanceof ApiRequestError) {
          console.error("[usePlacesQuery] API request failed", {
            status: error.status,
            details: error.details,
            category: filters.category,
            search: filters.search,
            region: filters.region,
            commune: filters.commune,
            radiusKm: filters.radiusKm,
            verifiedOnly: filters.verifiedOnly,
            isOpen247: filters.isOpen247,
          });
        } else {
          console.error("[usePlacesQuery] Unexpected error", error);
        }

        setError(
          getApiErrorMessage(error, "No fue posible cargar los puntos del mapa en este momento."),
        );
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [
    selectedCategory,
    deferredSearch,
    selectedRegion,
    selectedCommune,
    radiusKm,
    userLocation,
    showOnlyVerified,
    showOnly247,
  ]);

  useEffect(() => {
    let active = true;
    const territoryFilters: PlaceFilters = {
      category: selectedCategory || undefined,
      verifiedOnly: showOnlyVerified,
      isOpen247: showOnly247,
    };

    getPlaces(territoryFilters)
      .then((items) => {
        if (!active) {
          return;
        }
        setTerritoryPlaces(items);
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }

        console.error("[usePlacesQuery] Failed to load territory filters", error);
      });

    return () => {
      active = false;
    };
  }, [selectedCategory, showOnlyVerified, showOnly247]);

  const availableRegions = buildTerritoryOptions(territoryPlaces.map((place) => place.region));
  const regionNames = availableRegions.map((item) => item.name);
  const selectedRegionPlaces = selectedRegion
    ? territoryPlaces.filter((place) => place.region === selectedRegion)
    : [];
  const availableCommunes = selectedRegion
    ? buildTerritoryOptions(selectedRegionPlaces.map((place) => place.commune))
    : [];
  const communeNames = availableCommunes.map((item) => item.name);

  useEffect(() => {
    if (selectedRegion && !regionNames.includes(selectedRegion)) {
      setSelectedRegion("");
      setSelectedCommune("");
      return;
    }

    if (selectedCommune && !communeNames.includes(selectedCommune)) {
      setSelectedCommune("");
    }
  }, [
    availableCommunes,
    availableRegions,
    communeNames,
    regionNames,
    selectedCommune,
    selectedRegion,
  ]);

  const updateCategory = (value: string) => {
    startTransition(() => {
      setSelectedCategory(value);
      setSelectedRegion("");
      setSelectedCommune("");
    });
  };

  const updateRegion = (value: string) => {
    startTransition(() => {
      setSelectedRegion(value);
      setSelectedCommune("");
    });
  };

  const toggleUserLocation = () => {
    if (userLocation) {
      setUserLocation(null);
      setRadiusKm(null);
      setLocationMessage("Filtro por radio desactivado.");
      return;
    }

    if (typeof navigator === "undefined" || !navigator.geolocation) {
      setLocationMessage("Este navegador no permite usar geolocalización.");
      return;
    }

    if (typeof window !== "undefined" && !window.isSecureContext) {
      setLocationMessage("La ubicación solo funciona en una conexión segura (HTTPS).");
      return;
    }

    setLocating(true);
    setLocationMessage("Solicitando acceso a tu ubicación...");

    getGeolocationPermissionState()
      .then((permissionState) => {
        if (permissionState === "denied") {
          setLocationMessage(
            "El permiso de ubicación está bloqueado. En iPhone Safari debes permitirlo para este sitio y volver a intentarlo.",
          );
          setLocating(false);
          return null;
        }

        return requestUserPosition();
      })
      .then((position) => {
        if (!position) {
          return;
        }

        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setRadiusKm((currentRadius) => currentRadius ?? 5);
        setLocationMessage("Ubicación activada para filtrar por radio.");
        setLocating(false);
      })
      .catch((error: unknown) => {
        if (isGeolocationError(error)) {
          setLocationMessage(getLocationErrorMessage(error));
        } else {
          setLocationMessage(
            "No pudimos obtener tu ubicación. Revisa los permisos del navegador e inténtalo otra vez.",
          );
        }
        setLocating(false);
      });
  };

  return {
    places,
    selectedCategory,
    search,
    selectedRegion,
    selectedCommune,
    availableRegions,
    availableCommunes,
    totalPlacesCount: territoryPlaces.length,
    selectedRegionPlacesCount: selectedRegionPlaces.length,
    radiusKm,
    hasUserLocation: Boolean(userLocation),
    locating,
    loading,
    error,
    locationMessage,
    showOnlyVerified,
    showOnly247,
    setSearch,
    setSelectedCommune,
    setRadiusKm,
    setShowOnlyVerified,
    setShowOnly247,
    updateCategory,
    updateRegion,
    toggleUserLocation,
  };
}
