import { Metadata } from "next";

import { BusinessProfileEditForm } from "@/components/accounts/business-profile-edit-form";

export const metadata: Metadata = {
  title: "Editar negocio | Elbigotes",
  description: "Editar datos de registro de la cuenta comercial.",
};

export default function MiNegocioEditarPage() {
  return <BusinessProfileEditForm />;
}
