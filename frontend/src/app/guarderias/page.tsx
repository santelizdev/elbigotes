import { Metadata } from "next";

import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { ErrorState } from "@/components/shared/error-state";
import { loadPlacesPageData } from "@/lib/services/server-loaders";

export const metadata: Metadata = {
  title: "Guarderías para mascotas en Chile | Elbigotes",
  description: "Encuentra guarderías y estancias con fichas claras para comparar operación y ubicación.",
};

export default async function GuarderiasPage() {
  const { places, hasError } = await loadPlacesPageData({
    category: "guarderias",
  });

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todas las guarderías ahora mismo. La vista sigue disponible con los registros que sí llegaron." />
      ) : null}
      <MapExplorerPage
        title="Guarderías y estancias"
        description="Selecciona opciones de cuidado diario o estadía con un mapa preparado para comparar cobertura, contacto y contexto local."
        initialPlaces={places}
        initialCategory="guarderias"
      />
    </>
  );
}
