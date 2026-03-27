"use client";

import { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";
import { CHILE_REGIONS, getCommunesForRegion } from "@/lib/constants/chile-locations";

interface ExplorerToolbarProps {
  region: string;
  commune: string;
  radiusKm: number | null;
  hasUserLocation: boolean;
  locating: boolean;
  locationMessage?: string | null;
  showOnlyVerified: boolean;
  onRegionChange: (value: string) => void;
  onCommuneChange: (value: string) => void;
  onRadiusChange: (value: number | null) => void;
  onLocationToggle: () => void;
  onVerifiedChange: (checked: boolean) => void;
}

export function ExplorerToolbar({
  region,
  commune,
  radiusKm,
  hasUserLocation,
  locating,
  locationMessage,
  showOnlyVerified,
  onRegionChange,
  onCommuneChange,
  onRadiusChange,
  onLocationToggle,
  onVerifiedChange,
}: ExplorerToolbarProps) {
  const communes = region ? getCommunesForRegion(region) : [];
  const helperMessage =
    locationMessage ??
    (hasUserLocation
      ? "Region, comuna y radio pueden combinarse para acotar el mapa sin perder la categoria seleccionada."
      : "Primero elige una region o comuna, o activa 'Usar mi direccion' para delimitar la busqueda por radio.");

  return (
    <div className="toolbar">
      <Button onClick={onLocationToggle} type="button" variant="secondary">
        {locating ? "Ubicando..." : hasUserLocation ? "Quitar mi direccion" : "Usar mi direccion"}
      </Button>

      <label className="toolbar__field">
        <span className="toolbar__label">Region</span>
        <select
          value={region}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => onRegionChange(event.target.value)}
        >
          <option value="">Todas las regiones</option>
          {CHILE_REGIONS.map((item) => (
            <option key={item.region} value={item.region}>
              {item.region}
            </option>
          ))}
        </select>
      </label>

      <label className="toolbar__field">
        <span className="toolbar__label">Comuna</span>
        <select
          value={commune}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => onCommuneChange(event.target.value)}
          disabled={!region}
        >
          <option value="">{region ? "Todas las comunas" : "Selecciona una region"}</option>
          {communes.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>

      <label className="toolbar__field">
        <span className="toolbar__label">Radio</span>
        <select
          value={radiusKm ?? ""}
          onChange={(event: ChangeEvent<HTMLSelectElement>) =>
            onRadiusChange(event.target.value ? Number(event.target.value) : null)
          }
          disabled={!hasUserLocation}
        >
          <option value="">Sin radio</option>
          <option value="3">3 km</option>
          <option value="5">5 km</option>
          <option value="10">10 km</option>
          <option value="20">20 km</option>
        </select>
      </label>

      <label className="toolbar__toggle">
        <input
          type="checkbox"
          checked={showOnlyVerified}
          onChange={(event) => onVerifiedChange(event.target.checked)}
        />
        <span>Solo fichas verificadas</span>
      </label>

      <p className="toolbar__helper">{helperMessage}</p>
    </div>
  );
}
