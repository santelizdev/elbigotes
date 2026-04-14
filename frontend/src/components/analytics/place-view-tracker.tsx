"use client";

import { useEffect, useRef } from "react";

import { trackPlaceViewEvent } from "@/lib/services/analytics-service";

export function PlaceViewTracker({ placeSlug }: { placeSlug: string }) {
  const lastTrackedSlugRef = useRef<string>("");

  useEffect(() => {
    if (!placeSlug || typeof window === "undefined") {
      return;
    }

    if (lastTrackedSlugRef.current === placeSlug) {
      return;
    }

    lastTrackedSlugRef.current = placeSlug;
    void trackPlaceViewEvent({
      place_slug: placeSlug,
      path: `${window.location.pathname}${window.location.search}`,
    });
  }, [placeSlug]);

  return null;
}
