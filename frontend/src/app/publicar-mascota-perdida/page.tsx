import { Metadata } from "next";

import { LostPetReportForm } from "@/components/lost-pets/lost-pet-report-form";

export const metadata: Metadata = {
  title: "Publicar mascota perdida | Elbigotes",
  description: "Formulario geolocalizado para reportar una mascota perdida con foco en búsqueda territorial.",
};

export default function PublicarMascotaPerdidaPage() {
  return <LostPetReportForm />;
}

