"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { FaFacebookF, FaGoogle } from "react-icons/fa6";

import { PetOwnerRegistrationPanel } from "@/components/accounts/pet-owner-registration-panel";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormField, InfoBox } from "@/components/ui/form-primitives";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { loginAccount, setStoredAccessToken } from "@/lib/services/accounts-service";
import { cn } from "@/lib/utils/cn";

interface LoginFieldErrors {
  email?: string;
  password?: string;
}

const GOOGLE_AUTH_URL = process.env.NEXT_PUBLIC_GOOGLE_AUTH_URL?.trim() || "";
const FACEBOOK_AUTH_URL = process.env.NEXT_PUBLIC_FACEBOOK_AUTH_URL?.trim() || "";

function buildLoginFieldErrors(email: string, password: string): LoginFieldErrors {
  const errors: LoginFieldErrors = {};

  if (!email.trim()) {
    errors.email = "Ingresa tu correo para iniciar sesión.";
  }

  if (!password.trim()) {
    errors.password = "Ingresa tu contraseña.";
  }

  return errors;
}

export function AccountLoginForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<LoginFieldErrors>({});
  const [socialMessage, setSocialMessage] = useState<string | null>(null);

  const socialButtonsDisabled = useMemo(() => loading, [loading]);

  function handleGoogleLogin() {
    setSocialMessage(null);

    if (!GOOGLE_AUTH_URL) {
      setSocialMessage(
        "Google OAuth aún no está conectado en frontend. Falta configurar NEXT_PUBLIC_GOOGLE_AUTH_URL y el callback del backend.",
      );
      return;
    }

    // TODO(auth): conectar este redirect con el callback OAuth real del backend.
    window.location.assign(GOOGLE_AUTH_URL);
  }

  function handleFacebookLogin() {
    setSocialMessage(null);

    if (!FACEBOOK_AUTH_URL) {
      setSocialMessage(
        "Facebook OAuth aún no está conectado en frontend. Falta configurar NEXT_PUBLIC_FACEBOOK_AUTH_URL y el callback del backend.",
      );
      return;
    }

    // TODO(auth): conectar este redirect con el callback OAuth real del backend.
    window.location.assign(FACEBOOK_AUTH_URL);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSocialMessage(null);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const nextFieldErrors = buildLoginFieldErrors(email, password);
    setFieldErrors(nextFieldErrors);

    if (Object.keys(nextFieldErrors).length > 0) {
      setLoading(false);
      return;
    }

    try {
      const response = await loginAccount({ email, password });

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
    } catch (submitError) {
      setError(
        getApiErrorMessage(
          submitError,
          "No pudimos iniciar sesión. Revisa tus credenciales e intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageShell className="gap-5 py-6 md:gap-6">
      <PageHero
        eyebrow="Acceso cliente"
        title="Ingresa o crea tu cuenta de tutor"
        description="Mantuvimos el acceso actual y sumamos un registro más claro para tutores de mascotas, listo para crecer con login social y validación por correo."
        className="p-6"
      />

      <div className="grid items-start gap-5 lg:grid-cols-[minmax(18rem,0.86fr)_minmax(22rem,1.14fr)]">
        <SurfaceCard className="grid content-start gap-4 self-start p-5 md:p-6">
          <div className="grid gap-2 md:max-w-[32rem]">
            <p className="eyebrow">Login existente</p>
            <h2 className="m-0 font-display-ui text-[1.85rem] leading-tight">Iniciar sesión</h2>
            <p className="m-0 text-sm leading-7 text-app-text-soft">
              Entra al panel comercial o a tu espacio personal según el rol asociado a tu cuenta.
            </p>
          </div>

          <div className="grid gap-3 md:max-w-[32rem]">
            <Button
              type="button"
              variant="secondary"
              fullWidth
              disabled={socialButtonsDisabled}
              className="min-h-[3.5rem] justify-center py-2.5"
              onClick={handleGoogleLogin}
            >
              <FaGoogle aria-hidden="true" />
              Continuar con Google
            </Button>

            <Button
              type="button"
              variant="secondary"
              fullWidth
              disabled={socialButtonsDisabled}
              className="min-h-[3.5rem] justify-center py-2.5"
              onClick={handleFacebookLogin}
            >
              <FaFacebookF aria-hidden="true" />
              Continuar con Facebook
            </Button>
          </div>

          {socialMessage ? (
            <InfoBox tone="muted" className="rounded-[1.2rem] md:max-w-[32rem]">
              {socialMessage}
            </InfoBox>
          ) : null}

          <div className="flex items-center gap-3 text-xs uppercase tracking-[0.22em] text-app-text-muted md:max-w-[32rem]">
            <span className="h-px flex-1 bg-app-border" />
            <span>o sigue con tu email</span>
            <span className="h-px flex-1 bg-app-border" />
          </div>

          <form className="grid max-w-[32rem] gap-4" onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <FormField label="Email" htmlFor="email" error={fieldErrors.email}>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className={cn("form-control", fieldErrors.email && "border-red-500")}
                />
              </FormField>

              <FormField label="Password" htmlFor="password" error={fieldErrors.password}>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className={cn("form-control", fieldErrors.password && "border-red-500")}
                />
              </FormField>
            </div>

            <Button type="submit" disabled={loading} fullWidth className="min-h-[3.6rem] py-2.5">
              {loading ? "Ingresando..." : "Entrar"}
            </Button>

            {loading ? <LoadingPanel message="Validando acceso..." /> : null}
            {error ? <ErrorState message={error} /> : null}
          </form>
        </SurfaceCard>

        <SurfaceCard className="grid content-start gap-4 self-start p-5 md:p-6">
          <div className="grid gap-2">
            <p className="eyebrow">Registro tutor</p>
            <h2 className="m-0 font-display-ui text-[1.85rem] leading-tight">
              Crea tu perfil y registra a tu mascota
            </h2>
            <p className="m-0 text-sm leading-7 text-app-text-soft">
              El flujo ya separa autenticación, perfil del tutor y datos de la mascota para que
              luego podamos sumar más mascotas, campañas y verificación por correo sin rehacer la
              base.
            </p>
          </div>

          <PetOwnerRegistrationPanel submitLabel="Crear cuenta y continuar" />
        </SurfaceCard>
      </div>
    </PageShell>
  );
}
