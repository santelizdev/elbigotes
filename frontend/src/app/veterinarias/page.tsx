import { Metadata } from "next";

import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { ErrorState } from "@/components/shared/error-state";
import { loadPlacesPageData } from "@/lib/services/server-loaders";
import { getPublicCategories } from "@/lib/services/taxonomy-service";

export const metadata: Metadata = {
  title: "Veterinarias en Chile | Elbigotes",
  description: "Mapa público para encontrar veterinarias confiables, cercanas y verificadas.",
};

export default async function VeterinariasPage() {
  const categories = await getPublicCategories();
  const { places, hasError } = await loadPlacesPageData({
    category: "veterinarias",
  });

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todas las veterinarias en este momento. Mostramos la vista con los datos disponibles." />
      ) : null}
      <MapExplorerPage
        title="Veterinarias verificadas"
        description="Consulta clínicas y centros veterinarios con foco en confianza operativa, cercanía y lectura rápida desde mapa."
        initialPlaces={places}
        initialCategory="veterinarias"
        categories={categories}
      />
    </>
  );
}
