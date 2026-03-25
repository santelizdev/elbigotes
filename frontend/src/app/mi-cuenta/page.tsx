import { Metadata } from "next";

import { PetOwnerDashboard } from "@/components/accounts/pet-owner-dashboard";

export const metadata: Metadata = {
  title: "Mi cuenta | Elbigotes",
  description: "Área personal para tutores con mascotas registradas y reportes de extravío.",
};

export default function MiCuentaPage() {
  return <PetOwnerDashboard />;
}
