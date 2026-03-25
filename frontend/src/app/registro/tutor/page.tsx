import { Metadata } from "next";

import { PetOwnerRegistrationForm } from "@/components/accounts/pet-owner-registration-form";

export const metadata: Metadata = {
  title: "Registro de tutor | Elbigotes",
  description: "Crea una cuenta personal y la primera ficha de mascota para futuras campañas y servicios.",
};

export default function RegistroTutorPage() {
  return <PetOwnerRegistrationForm />;
}
