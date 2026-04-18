"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormField, FormGrid } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { loginAccount, setStoredAccessToken } from "@/lib/services/accounts-service";

export function AccountLoginForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(event.currentTarget);

    try {
      const response = await loginAccount({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
      });

      setStoredAccessToken(response.token);

      if (response.user.role === "business_owner") {
        router.push("/mi-negocio");
        router.refresh();
        return;
      }

      if (response.user.role === "pet_owner") {
        router.push("/mi-cuenta");
        router.refresh();
        return;
      }

      setError("Esta cuenta todavía no tiene un panel habilitado en esta versión.");
    } catch (error) {
      setError(
        getApiErrorMessage(
          error,
          "No pudimos iniciar sesión. Revisa tus credenciales e intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageShell>
      <PageHero
        eyebrow="Acceso cliente"
        title="Ingresar al área cliente"
        description="Desde aquí podrás entrar al panel comercial o al espacio personal de tutores, según el rol asociado a tu cuenta."
      />

      <SurfaceCard className="grid gap-4">
        <h2 className="m-0 font-display-ui text-3xl leading-tight">Iniciar sesión</h2>
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <FormGrid>
            <FormField label="Email" htmlFor="email">
              <input id="email" name="email" type="email" required className="form-control" />
            </FormField>
            <FormField label="Password" htmlFor="password">
              <input
                id="password"
                name="password"
                type="password"
                required
                className="form-control"
              />
            </FormField>
          </FormGrid>

          <Button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Entrar"}
          </Button>

          {loading ? <LoadingPanel message="Validando acceso..." /> : null}
          {error ? <ErrorState message={error} /> : null}
        </form>
      </SurfaceCard>
    </PageShell>
  );
}
