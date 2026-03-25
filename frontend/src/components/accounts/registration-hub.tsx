import styles from "@/components/accounts/registration.module.css";
import { Button } from "@/components/ui/button";

export function RegistrationHub() {
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Alta inicial de cuentas</p>
        <h1 className="page-title">Registra tu perfil en Elbigotes</h1>
        <p className="page-lead">
          Abrimos dos flujos distintos porque el producto tendrá necesidades muy diferentes:
          negocios y organizaciones del ecosistema pet por un lado, y tutores con sus mascotas por
          otro.
        </p>
        <div className={styles.heroActions}>
          <Button href="/ingresar" variant="ghost">
            Ya tengo cuenta
          </Button>
        </div>
      </section>

      <section className={styles.cards}>
        <article className={styles.card}>
          <p className="eyebrow">Negocios y organizaciones</p>
          <h3>Veterinarias, guarderías, emergencias, refugios y parques</h3>
          <p>
            Este registro crea la cuenta comercial y deja lista la base para membresías, periodo
            de gracia y gestión operativa desde admin.
          </p>
          <div className={styles.cardFooter}>
            <Button href="/registro/negocio" variant="primary">
              Registrar negocio
            </Button>
          </div>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Tutores de mascotas</p>
          <h3>Cuenta personal más ficha inicial de mascota</h3>
          <p>
            Este flujo deja creado el perfil del tutor y la primera ficha de mascota para futuras
            campañas, recordatorios, cumpleaños y comunicación segmentada.
          </p>
          <div className={styles.cardFooter}>
            <Button href="/registro/tutor" variant="primary">
              Registrar tutor
            </Button>
          </div>
        </article>
      </section>
    </div>
  );
}
