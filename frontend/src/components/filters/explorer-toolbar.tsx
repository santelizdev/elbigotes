"use client";

import { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";
import { getAllCommunes } from "@/lib/constants/chile-locations";

interface ExplorerToolbarProps {
  search: string;
  commune: string;
  radiusKm: number | null;
  hasUserLocation: boolean;
  locating: boolean;
  locationMessage?: string | null;
  showOnlyVerified: boolean;
  onSearchChange: (value: string) => void;
  onCommuneChange: (value: string) => void;
  onRadiusChange: (value: number | null) => void;
  onLocationToggle: () => void;
  onVerifiedChange: (checked: boolean) => void;
}

export function ExplorerToolbar({
  search,
  commune,
  radiusKm,
  hasUserLocation,
  locating,
  locationMessage,
  showOnlyVerified,
  onSearchChange,
  onCommuneChange,
  onRadiusChange,
  onLocationToggle,
  onVerifiedChange,
}: ExplorerToolbarProps) {
  const communes = getAllCommunes();

  return (
    <div className="toolbar">
      <label className="toolbar__search">
        <span className="sr-only">Buscar por nombre o dirección</span>
        <input
          type="search"
          value={search}
          onChange={(event: ChangeEvent<HTMLInputElement>) => onSearchChange(event.target.value)}
          placeholder="Buscar por nombre, comuna o dirección"
        />
      </label>

      <label className="toolbar__field">
        <span className="toolbar__label">Comuna</span>
        <select
          value={commune}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => onCommuneChange(event.target.value)}
        >
          <option value="">Todas las comunas</option>
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

      <Button onClick={onLocationToggle} type="button" variant="secondary">
        {locating ? "Ubicando..." : hasUserLocation ? "Quitar radio" : "Usar mi ubicación"}
      </Button>

      <Button href="/publicar-mascota-perdida" variant="primary">
        Publicar mascota perdida
      </Button>

      {locationMessage ? <p className="toolbar__helper">{locationMessage}</p> : null}
    </div>
  );
}
