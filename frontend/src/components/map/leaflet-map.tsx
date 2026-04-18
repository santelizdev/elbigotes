"use client";

import dynamic from "next/dynamic";

import { MapPoint } from "@/components/map/types";
import { MapLoadingShell } from "@/components/ui/map-loading-shell";

const LeafletMapRuntime = dynamic(() => import("@/components/map/leaflet-map-runtime"), {
  ssr: false,
  loading: () => <MapLoadingShell />,
});

interface LeafletMapProps {
  points: MapPoint[];
  onSelect?: (id: string) => void;
  focusedPointId?: string | null;
}

export function LeafletMap({ points, onSelect, focusedPointId }: LeafletMapProps) {
  return (
    <LeafletMapRuntime
      points={points}
      onSelect={onSelect}
      focusedPointId={focusedPointId}
    />
  );
}
