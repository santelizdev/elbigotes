import { Metadata } from "next";

import { BusinessDashboard } from "@/components/accounts/business-dashboard";

export const metadata: Metadata = {
  title: "Mi negocio | Elbigotes",
  description: "Resumen del área cliente comercial y estado de tus fichas públicas.",
};

export default function MiNegocioPage() {
  return <BusinessDashboard />;
}
