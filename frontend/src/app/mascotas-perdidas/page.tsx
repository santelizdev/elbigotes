import { Metadata } from "next";

import { LostPetsExplorer } from "@/components/lost-pets/lost-pets-explorer";
import { ErrorState } from "@/components/shared/error-state";
import { loadLostPetsPageData } from "@/lib/services/server-loaders";

export const metadata: Metadata = {
  title: "Mascotas perdidas en Chile | Elbigotes",
  description: "Reportes públicos con última ubicación conocida para acelerar búsquedas sobre mapa.",
};

export default async function MascotasPerdidasPage() {
  const { lostPets, hasError } = await loadLostPetsPageData();

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar todos los reportes. Mostramos la sección con los datos disponibles." />
      ) : null}
      <LostPetsExplorer reports={lostPets} />
    </>
  );
}
