import { ErrorState } from "@/components/shared/error-state";
import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { loadHomePageData } from "@/lib/services/server-loaders";

export default async function HomePage() {
  const { places, lostPets, hasError } = await loadHomePageData();

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los datos del home. La vista seguirá operativa con la información disponible." />
      ) : null}
      <MapExplorerPage
        title="Mapa del ecosistema pet en Chile"
        description="Explora veterinarias, refugios, parques pet friendly, guarderías y servicios 24/7 en una interfaz pensada para decidir rápido y con contexto territorial."
        initialPlaces={places}
        lostPetsCount={lostPets.length}
      />
    </>
  );
}
