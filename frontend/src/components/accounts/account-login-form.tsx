"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import styles from "@/components/accounts/registration.module.css";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
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
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Acceso cliente</p>
        <h1 className="page-title">Ingresar al área cliente</h1>
        <p className="page-lead">
          Desde aquí podrás entrar al panel comercial o al espacio personal de tutores, según el
          rol asociado a tu cuenta.
        </p>
      </section>

      <section className={styles.formCard}>
        <h2>Iniciar sesión</h2>
        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGrid}>
            <div className={styles.field}>
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" required />
            </div>
            <div className={styles.field}>
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" required />
            </div>
          </div>

          <Button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Entrar"}
          </Button>

          {loading ? <LoadingPanel message="Validando acceso..." /> : null}
          {error ? <ErrorState message={error} /> : null}
        </form>
      </section>
    </div>
  );
}
