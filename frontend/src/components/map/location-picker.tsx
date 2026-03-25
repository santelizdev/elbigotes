"use client";

import dynamic from "next/dynamic";

import { LoadingPanel } from "@/components/shared/loading-panel";

const LocationPickerRuntime = dynamic(
  () =>
    import("@/components/map/location-picker-runtime").then((module) => module.LocationPickerRuntime),
  {
    ssr: false,
    loading: () => <LoadingPanel message="Preparando selector de ubicación..." />,
  },
);

export function LocationPicker({
  latitude,
  longitude,
  onChange,
}: {
  latitude?: number;
  longitude?: number;
  onChange: (latitude: number, longitude: number) => void;
}) {
  return (
    <LocationPickerRuntime
      latitude={latitude}
      longitude={longitude}
      onChange={onChange}
    />
  );
}
