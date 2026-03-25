import { Metadata } from "next";

import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { ErrorState } from "@/components/shared/error-state";
import { loadPlacesPageData } from "@/lib/services/server-loaders";

export const metadata: Metadata = {
  title: "Parques pet friendly en Chile | Elbigotes",
  description: "Mapa de parques y espacios públicos aptos para mascotas en ciudades chilenas.",
};

export default async function ParquesPage() {
  const { places, hasError } = await loadPlacesPageData({
    category: "parques-pet-friendly",
  });

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los parques en este momento. Mostramos los datos que sí están disponibles." />
      ) : null}
      <MapExplorerPage
        title="Parques pet friendly"
        description="Encuentra áreas para paseo, recreación y socialización con una vista que prioriza territorio y accesibilidad."
        initialPlaces={places}
        initialCategory="parques-pet-friendly"
      />
    </>
  );
}
