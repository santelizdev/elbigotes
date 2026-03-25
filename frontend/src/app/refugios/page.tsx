import { Metadata } from "next";

import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { ErrorState } from "@/components/shared/error-state";
import { loadPlacesPageData } from "@/lib/services/server-loaders";
import { getPublicCategories } from "@/lib/services/taxonomy-service";

export const metadata: Metadata = {
  title: "Refugios y albergues en Chile | Elbigotes",
  description: "Explora refugios y organizaciones de rescate con contexto territorial y fichas moderadas.",
};

export default async function RefugiosPage() {
  const categories = await getPublicCategories();
  const { places, hasError } = await loadPlacesPageData({
    category: "refugios-albergues",
  });

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los refugios ahora mismo. La vista sigue funcionando con los datos que sí llegaron." />
      ) : null}
      <MapExplorerPage
        title="Refugios y albergues"
        description="Ubica organizaciones de rescate y espacios de tránsito sobre mapa, con información lista para tomar contacto."
        initialPlaces={places}
        initialCategory="refugios-albergues"
        categories={categories}
      />
    </>
  );
}
