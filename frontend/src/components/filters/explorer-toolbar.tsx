"use client";

import { ChangeEvent } from "react";

import { Button } from "@/components/ui/button";

interface ExplorerToolbarProps {
  search: string;
  showOnlyVerified: boolean;
  onSearchChange: (value: string) => void;
  onVerifiedChange: (checked: boolean) => void;
}

export function ExplorerToolbar({
  search,
  showOnlyVerified,
  onSearchChange,
  onVerifiedChange,
}: ExplorerToolbarProps) {
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

      <label className="toolbar__toggle">
        <input
          type="checkbox"
          checked={showOnlyVerified}
          onChange={(event) => onVerifiedChange(event.target.checked)}
        />
        <span>Solo fichas verificadas</span>
      </label>

      <Button href="/publicar-mascota-perdida" variant="primary">
        Publicar mascota perdida
      </Button>
    </div>
  );
}

