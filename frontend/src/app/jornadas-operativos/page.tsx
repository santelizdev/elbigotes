import { Metadata } from "next";

import { PublicPetOperationsExplorer } from "@/components/operations/public-pet-operations-explorer";
import { ErrorState } from "@/components/shared/error-state";
import { loadPublicPetOperationsPageData } from "@/lib/services/server-loaders";

export const metadata: Metadata = {
  title: "Jornadas y operativos para mascotas | Elbigotes",
  description: "Operativos vigentes con dirección confirmada y visualización sobre mapa.",
};

export default async function JornadasOperativosPage() {
  const { operations, hasError } = await loadPublicPetOperationsPageData();

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los operativos. Mostramos la sección con los datos disponibles." />
      ) : null}
      <PublicPetOperationsExplorer operations={operations} />
    </>
  );
}
