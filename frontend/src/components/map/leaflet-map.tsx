"use client";

import dynamic from "next/dynamic";

import { LoadingPanel } from "@/components/shared/loading-panel";
import { MapPoint } from "@/components/map/types";

const LeafletMapRuntime = dynamic(() => import("@/components/map/leaflet-map-runtime"), {
  ssr: false,
  loading: () => <LoadingPanel message="Preparando mapa interactivo..." />,
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
