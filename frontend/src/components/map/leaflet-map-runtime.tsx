"use client";

import "leaflet/dist/leaflet.css";

import { useEffect } from "react";
import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

import { siteConfig } from "@/lib/constants/site";
import { getMapBounds } from "@/lib/utils/maps";
import { MapPoint } from "@/components/map/types";

interface RuntimeProps {
  points: MapPoint[];
  onSelect?: (id: string) => void;
  focusedPointId?: string | null;
}

function createMarkerIcon(accent: string, active: boolean) {
  return L.divIcon({
    className: "custom-map-marker__wrapper",
    html: `<span class="custom-map-marker ${active ? "custom-map-marker--active" : ""}" style="--marker-accent: ${accent}"></span>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function MapViewportController({
  points,
  focusedPointId,
}: {
  points: MapPoint[];
  focusedPointId?: string | null;
}) {
  const map = useMap();

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      map.invalidateSize();
    });
    return () => cancelAnimationFrame(frame);
  }, [map, points.length, focusedPointId]);

  useEffect(() => {
    const focusedPoint = focusedPointId
      ? points.find((point) => point.id === focusedPointId)
      : null;

    if (focusedPoint) {
      map.stop();
      map.setView([focusedPoint.latitude, focusedPoint.longitude], 14, {
        animate: false,
      });
      return;
    }

    // El mapa se reajusta desde los datos visibles para que móvil y desktop compartan la misma lógica.
    const bounds = getMapBounds(points);
    if (!bounds) {
      map.stop();
      map.setView(
        [siteConfig.defaultCenter.lat, siteConfig.defaultCenter.lng],
        siteConfig.defaultZoom,
        { animate: false },
      );
      return;
    }

    if (points.length === 1) {
      map.stop();
      map.setView([points[0].latitude, points[0].longitude], 14, { animate: false });
      return;
    }

    map.stop();
    map.fitBounds(bounds, { padding: [34, 34], animate: false, maxZoom: 14 });
  }, [focusedPointId, map, points]);

  return null;
}

export default function LeafletMapRuntime({
  points,
  onSelect,
  focusedPointId,
}: RuntimeProps) {
  const safePoints = points.filter(
    (point) => Number.isFinite(point.latitude) && Number.isFinite(point.longitude),
  );
  const mapSignature =
    safePoints.map((point) => `${point.id}:${point.latitude}:${point.longitude}`).join("|") || "empty";

  return (
    <MapContainer
      key={mapSignature}
      center={[siteConfig.defaultCenter.lat, siteConfig.defaultCenter.lng]}
      zoom={siteConfig.defaultZoom}
      scrollWheelZoom
      zoomAnimation={false}
      fadeAnimation={false}
      markerZoomAnimation={false}
      className="leaflet-shell"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapViewportController points={safePoints} focusedPointId={focusedPointId} />

      {safePoints.map((point) => (
        <Marker
          key={point.id}
          position={[point.latitude, point.longitude]}
          icon={createMarkerIcon(point.accent ?? "var(--accent-emerald)", Boolean(point.active))}
          eventHandlers={{
            click: () => onSelect?.(point.id),
          }}
        >
          <Popup>
            <strong>{point.title}</strong>
            <br />
            {point.subtitle}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
