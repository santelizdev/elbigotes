"use client";

import "leaflet/dist/leaflet.css";

import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, TileLayer, useMapEvents } from "react-leaflet";

import { siteConfig } from "@/lib/constants/site";

function createMarkerIcon() {
  return L.divIcon({
    className: "custom-map-marker__wrapper",
    html: '<span class="custom-map-marker custom-map-marker--active" style="--marker-accent: var(--accent-emerald)"></span>',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function ClickHandler({
  latitude,
  longitude,
  onChange,
}: {
  latitude?: number;
  longitude?: number;
  onChange: (latitude: number, longitude: number) => void;
}) {
  const map = useMapEvents({
    click(event) {
      onChange(event.latlng.lat, event.latlng.lng);
    },
  });

  useEffect(() => {
    requestAnimationFrame(() => {
      map.invalidateSize();
      if (latitude !== undefined && longitude !== undefined) {
        map.setView([latitude, longitude], 15, { animate: true });
      }
    });
  }, [latitude, longitude, map]);

  return null;
}

export function LocationPickerRuntime({
  latitude,
  longitude,
  onChange,
}: {
  latitude?: number;
  longitude?: number;
  onChange: (latitude: number, longitude: number) => void;
}) {
  return (
    <MapContainer
      center={[
        latitude ?? siteConfig.defaultCenter.lat,
        longitude ?? siteConfig.defaultCenter.lng,
      ]}
      zoom={latitude !== undefined && longitude !== undefined ? 15 : siteConfig.defaultZoom}
      scrollWheelZoom
      className="leaflet-shell"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler latitude={latitude} longitude={longitude} onChange={onChange} />
      {latitude !== undefined && longitude !== undefined ? (
        <Marker position={[latitude, longitude]} icon={createMarkerIcon()} />
      ) : null}
    </MapContainer>
  );
}
