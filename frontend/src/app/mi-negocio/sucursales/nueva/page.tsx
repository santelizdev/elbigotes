import { Metadata } from "next";

import { BusinessBranchCreateForm } from "@/components/accounts/business-branch-create-form";

export const metadata: Metadata = {
  title: "Nueva sucursal | Elbigotes",
  description: "Crear una nueva sucursal asociada a la cuenta comercial.",
};

export default function NuevaSucursalPage() {
  return <BusinessBranchCreateForm />;
}
