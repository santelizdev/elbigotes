import { Metadata } from "next";

import { BusinessRegistrationForm } from "@/components/accounts/business-registration-form";
import { ErrorState } from "@/components/shared/error-state";
import { RegistrationCatalogItem, getRegistrationCatalog } from "@/lib/services/accounts-service";

export const metadata: Metadata = {
  title: "Registro de negocio | Elbigotes",
  description: "Crea una cuenta comercial para negocios y organizaciones del ecosistema pet.",
};

const fallbackBusinessKinds: RegistrationCatalogItem[] = [
  { value: "veterinary", label: "Veterinaria" },
  { value: "daycare", label: "Guarderia" },
  { value: "emergency", label: "Emergencia 24/7" },
  { value: "shelter", label: "Refugio" },
  { value: "park", label: "Parque" },
];

export default async function RegistroNegocioPage() {
  let hasError = false;
  let businessKinds: RegistrationCatalogItem[] = fallbackBusinessKinds;

  try {
    const catalog = await getRegistrationCatalog();
    businessKinds = catalog.business_kinds;
  } catch {
    hasError = true;
  }

  return (
    <>
      {hasError ? (
        <ErrorState message="No pudimos cargar el catálogo dinámico de tipos de negocio. Usamos una versión segura por defecto." />
      ) : null}
      <BusinessRegistrationForm businessKinds={businessKinds} />
    </>
  );
}
