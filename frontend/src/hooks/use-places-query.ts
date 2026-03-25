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
  const [showOnlyVerified, setShowOnlyVerified] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    let active = true;
    const filters: PlaceFilters = {
      category: selectedCategory || undefined,
      search: deferredSearch || undefined,
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
  }, [selectedCategory, deferredSearch, showOnlyVerified]);

  const updateCategory = (value: string) => {
    startTransition(() => {
      setSelectedCategory(value);
    });
  };

  return {
    places,
    selectedCategory,
    search,
    loading,
    error,
    showOnlyVerified,
    setSearch,
    setShowOnlyVerified,
    updateCategory,
  };
}
