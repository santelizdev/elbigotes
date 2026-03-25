import { ErrorState } from "@/components/shared/error-state";
import { MapExplorerPage } from "@/components/explorer/map-explorer-page";
import { loadHomePageData } from "@/lib/services/server-loaders";
import { getPublicCategories } from "@/lib/services/taxonomy-service";

type HomeSearchParams = Record<string, string | string[] | undefined>;

function getSingleQueryValue(value?: string | string[]) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function HomePage({
  searchParams,
}: {
  searchParams?: Promise<HomeSearchParams>;
}) {
  const resolvedSearchParams: HomeSearchParams = await (
    searchParams ?? Promise.resolve<HomeSearchParams>({})
  );
  const initialCategory = getSingleQueryValue(resolvedSearchParams.category);
  const categories = await getPublicCategories();
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
        initialCategory={initialCategory}
        categories={categories}
        lostPetsCount={lostPets.length}
      />
    </>
  );
}
