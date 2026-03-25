import { Metadata } from "next";

import { AccountLoginForm } from "@/components/accounts/account-login-form";

export const metadata: Metadata = {
  title: "Ingresar | Elbigotes",
  description: "Acceso al área comercial para administrar fichas y sucursales.",
};

export default function IngresarPage() {
  return <AccountLoginForm />;
}
