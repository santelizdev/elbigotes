"use client";

import { startTransition, useDeferredValue, useEffect, useState } from "react";

import { Place, PlaceFilters } from "@/lib/types";
import { getPlaces } from "@/lib/services/places-service";

interface UsePlacesQueryOptions {
  initialPlaces: Place[];
  initialCategory?: string;
}

export function usePlacesQuery({ initialPlaces, initialCategory }: UsePlacesQueryOptions) {
  const [places, setPlaces] = useState(initialPlaces);
  const [selectedCategory, setSelectedCategory] = useState(initialCategory ?? "");
  const [search, setSearch] = useState("");
  const [selectedCommune, setSelectedCommune] = useState("");
  const [radiusKm, setRadiusKm] = useState<number | null>(null);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [showOnlyVerified, setShowOnlyVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    let active = true;
    const normalizedSearch = deferredSearch.trim();
    const filters: PlaceFilters = {
      category: selectedCategory || undefined,
      search: normalizedSearch.length >= 2 ? normalizedSearch : undefined,
      commune: selectedCommune || undefined,
      lat: radiusKm && userLocation ? userLocation.lat : undefined,
      lng: radiusKm && userLocation ? userLocation.lng : undefined,
      radiusKm: radiusKm && userLocation ? radiusKm : undefined,
      verifiedOnly: showOnlyVerified,
    };

    setLoading(true);
    setError(null);

    getPlaces(filters)
      .then((items) => {
        if (!active) {
          return;
        }
        setPlaces(items);
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setError("No fue posible cargar los puntos del mapa.");
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedCategory, deferredSearch, selectedCommune, radiusKm, userLocation, showOnlyVerified]);

  const updateCategory = (value: string) => {
    startTransition(() => {
      setSelectedCategory(value);
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

    setLocating(true);
    setLocationMessage(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setRadiusKm((currentRadius) => currentRadius ?? 5);
        setLocationMessage("Ubicación activada para filtrar por radio.");
        setLocating(false);
      },
      () => {
        setLocationMessage("No pudimos obtener tu ubicación. Revisa los permisos del navegador.");
        setLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000,
      },
    );
  };

  return {
    places,
    selectedCategory,
    search,
    selectedCommune,
    radiusKm,
    hasUserLocation: Boolean(userLocation),
    locating,
    loading,
    error,
    locationMessage,
    showOnlyVerified,
    setSearch,
    setSelectedCommune,
    setRadiusKm,
    setShowOnlyVerified,
    updateCategory,
    toggleUserLocation,
  };
}
