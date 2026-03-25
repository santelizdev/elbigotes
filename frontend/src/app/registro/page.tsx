import { Metadata } from "next";

import { RegistrationHub } from "@/components/accounts/registration-hub";

export const metadata: Metadata = {
  title: "Registro de usuarios | Elbigotes",
  description: "Crea cuentas comerciales o de tutor con una base lista para operar y crecer.",
};

export default function RegistroPage() {
  return <RegistrationHub />;
}
