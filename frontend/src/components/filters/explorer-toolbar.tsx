"use client";

import { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

interface ExplorerToolbarProps {
  region: string;
  commune: string;
  availableRegions: Array<{ name: string; count: number }>;
  availableCommunes: Array<{ name: string; count: number }>;
  totalPlacesCount: number;
  selectedRegionPlacesCount: number;
  radiusKm: number | null;
  hasUserLocation: boolean;
  locating: boolean;
  locationMessage?: string | null;
  showOnlyVerified: boolean;
  showOnly247: boolean;
  onRegionChange: (value: string) => void;
  onCommuneChange: (value: string) => void;
  onRadiusChange: (value: number | null) => void;
  onLocationToggle: () => void;
  onVerifiedChange: (checked: boolean) => void;
  onOpen247Change: (checked: boolean) => void;
}

export function ExplorerToolbar({
  region,
  commune,
  availableRegions,
  availableCommunes,
  totalPlacesCount,
  selectedRegionPlacesCount,
  radiusKm,
  hasUserLocation,
  locating,
  locationMessage,
  showOnlyVerified,
  showOnly247,
  onRegionChange,
  onCommuneChange,
  onRadiusChange,
  onLocationToggle,
  onVerifiedChange,
  onOpen247Change,
}: ExplorerToolbarProps) {
  const helperMessage =
    locationMessage ??
    (hasUserLocation
      ? "Region, comuna y radio pueden combinarse para acotar el mapa sin perder la categoria seleccionada."
      : "Primero elige una region o comuna, o activa 'Usar mi direccion' para delimitar la busqueda por radio.");

  return (
    <div className="grid items-end gap-4 xl:grid-cols-[auto_minmax(210px,1.1fr)_minmax(190px,1fr)_minmax(170px,0.8fr)_auto]">
      <Button onClick={onLocationToggle} type="button" variant="secondary">
        {locating ? "Ubicando..." : hasUserLocation ? "Quitar mi direccion" : "Usar mi direccion"}
      </Button>

      <label className="grid min-w-0 gap-1.5">
        <span className="text-[0.76rem] font-bold uppercase tracking-[0.08em] text-app-text-muted">
          Region
        </span>
        <select
          className="form-control rounded-full"
          value={region}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => onRegionChange(event.target.value)}
        >
          <option value="">
            {`Todas las regiones (${totalPlacesCount.toLocaleString("es-CL")})`}
          </option>
          {availableRegions.map((item) => (
            <option key={item.name} value={item.name}>
              {`${item.name} (${item.count.toLocaleString("es-CL")})`}
            </option>
          ))}
        </select>
      </label>

      <label className="grid min-w-0 gap-1.5">
        <span className="text-[0.76rem] font-bold uppercase tracking-[0.08em] text-app-text-muted">
          Comuna
        </span>
        <select
          className="form-control rounded-full disabled:cursor-not-allowed disabled:opacity-60"
          value={commune}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => onCommuneChange(event.target.value)}
          disabled={!region}
        >
          <option value="">
            {region
              ? `Todas las comunas (${selectedRegionPlacesCount.toLocaleString("es-CL")})`
              : "Selecciona una region"}
          </option>
          {availableCommunes.map((item) => (
            <option key={item.name} value={item.name}>
              {`${item.name} (${item.count.toLocaleString("es-CL")})`}
            </option>
          ))}
        </select>
      </label>

      <label className="grid min-w-0 gap-1.5">
        <span className="text-[0.76rem] font-bold uppercase tracking-[0.08em] text-app-text-muted">
          Radio
        </span>
        <select
          className="form-control rounded-full disabled:cursor-not-allowed disabled:opacity-60"
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

      <div className="grid gap-2">
        <label className="inline-flex min-h-[1.4rem] items-center gap-3 text-app-text-soft">
          <input
            type="checkbox"
            checked={showOnly247}
            onChange={(event) => onOpen247Change(event.target.checked)}
            className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
          />
          <span>Solo 24 horas</span>
        </label>

        <label className="inline-flex min-h-[1.4rem] items-center gap-3 text-app-text-soft">
          <input
            type="checkbox"
            checked={showOnlyVerified}
            onChange={(event) => onVerifiedChange(event.target.checked)}
            className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
          />
          <span>Solo fichas verificadas</span>
        </label>
      </div>

      <p className={cn("m-0 text-sm text-app-text-muted xl:col-span-full")}>{helperMessage}</p>
    </div>
  );
}
