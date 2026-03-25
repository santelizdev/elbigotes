import styles from "@/components/accounts/registration.module.css";
import { Button } from "@/components/ui/button";

export function AccountAccessNotice({
  title = "Necesitas iniciar sesión",
  message = "Ingresa con tu cuenta comercial para administrar tu perfil y tus sucursales.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <section className={styles.formCard}>
      <p className="eyebrow">Acceso requerido</p>
      <h2>{title}</h2>
      <p>{message}</p>
      <div className={styles.heroActions}>
        <Button href="/ingresar" variant="primary">
          Ingresar
        </Button>
        <Button href="/registro/negocio" variant="ghost">
          Crear cuenta comercial
        </Button>
      </div>
    </section>
  );
}
