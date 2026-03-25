import { Metadata } from "next";

import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { ErrorState } from "@/components/shared/error-state";
import { loadPlacesPageData } from "@/lib/services/server-loaders";
import { getPublicCategories } from "@/lib/services/taxonomy-service";

export const metadata: Metadata = {
  title: "Emergencias veterinarias 24/7 en Chile | Elbigotes",
  description: "Accede a hospitales y servicios veterinarios de urgencia con mapa y contacto prioritario.",
};

export default async function EmergenciasVeterinariasPage() {
  const categories = await getPublicCategories();
  const { places, hasError } = await loadPlacesPageData({
    category: "emergencias-veterinarias",
    isEmergencyService: true,
  });

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los servicios de emergencia. Mostramos la vista con la información disponible." />
      ) : null}
      <MapExplorerPage
        title="Emergencias veterinarias 24/7"
        description="Cuando el tiempo importa, el mapa debe responder primero. Esta vista destaca centros críticos con contacto directo y lectura inmediata."
        initialPlaces={places}
        initialCategory="emergencias-veterinarias"
        categories={categories}
      />
    </>
  );
}
